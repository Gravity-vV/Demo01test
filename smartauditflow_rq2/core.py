#!/usr/bin/env python3
"""Run SmartAuditFlow audits against EmpiricalSCST RQ2 ground truth.

Features:
- Calls SmartAuditFlow API workflow: start -> poll status -> fetch results
- Supports `single` and `batch` modes
- Multi-label classification:
    predicts zero or more from SWC-101/SWC-105/SWC-106/SWC-107/SWC-115
    and treats empty prediction as SWC-OTHER
- Rule-first SWC mapping, with optional LLM fallback classification
- Optional static_tool input from a directory
- Outputs per-model CSV summaries under test/results/<run_id>/<model>/
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import datetime as dt
import http.client
import json
import math
import re
import shutil
import sys
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple
from urllib import error as urlerror
from urllib import request as urlrequest

from .rule_reports import build_rule_score_fieldnames, compute_rule_score_rows


class FatalAuditStop(Exception):
    """Raised when upstream LLM retries exhaust and auditing must halt."""


TARGET_SWCS: List[str] = ["SWC-101", "SWC-105", "SWC-106", "SWC-107", "SWC-115"]
OTHER_LABEL = "SWC-OTHER"
ALL_LABELS: List[str] = TARGET_SWCS + [OTHER_LABEL]
DEFAULT_MODEL_ORDER = [
    "deepseek_school",
    "deepseek_silicon",
    "deepseek",
    "auto",
]


def now_iso() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def sanitize_model_name(name: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9._-]+", "_", name.strip())
    return safe or "unknown_model"


def normalize_address(address: str) -> str:
    return (address or "").strip().lower()


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_scalar(raw: str) -> Any:
    value = raw.strip()
    if value == "":
        return ""

    low = value.lower()
    if low in {"true", "yes", "on"}:
        return True
    if low in {"false", "no", "off"}:
        return False
    if low in {"null", "none", "~"}:
        return None

    if (value.startswith("\"") and value.endswith("\"")) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]

    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(item) for item in inner.split(",")]

    if re.fullmatch(r"[-+]?\d+", value):
        return int(value)

    if re.fullmatch(r"[-+]?\d*\.\d+", value):
        return float(value)

    return value


def load_config(path: Optional[Path]) -> Dict[str, Any]:
    if path is None:
        return {}

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    text = path.read_text(encoding="utf-8")
    stripped = text.strip()
    if not stripped:
        return {}

    if path.suffix.lower() == ".json":
        data = json.loads(stripped)
        if not isinstance(data, dict):
            raise ValueError("Config JSON must be an object")
        return data

    # Lightweight YAML parser for key/value plus flat lists.
    data: Dict[str, Any] = {}
    current_list_key: Optional[str] = None
    for line in text.splitlines():
        content = line.split("#", 1)[0]
        if not content.strip():
            continue

        if re.match(r"^\s*-\s+", content):
            if current_list_key is None:
                continue
            item = re.sub(r"^\s*-\s+", "", content).strip()
            if not isinstance(data.get(current_list_key), list):
                data[current_list_key] = []
            data[current_list_key].append(parse_scalar(item))
            continue

        current_list_key = None
        if ":" not in content:
            continue
        key, value = content.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue

        if value == "":
            data[key] = []
            current_list_key = key
        else:
            data[key] = parse_scalar(value)

    return data


def resolve_path(value: Optional[Any], base_dir: Optional[Path]) -> Optional[Path]:
    if value is None or value == "":
        return None
    p = Path(str(value)).expanduser()
    if not p.is_absolute() and base_dir is not None:
        p = (base_dir / p).resolve()
    return p.resolve() if p.exists() else p


def parse_models(models_value: Any) -> List[str]:
    if isinstance(models_value, list):
        parts = [str(x).strip() for x in models_value if str(x).strip()]
    else:
        raw = str(models_value or "").strip()
        parts = [x.strip() for x in raw.split(",") if x.strip()]

    seen = set()
    ordered: List[str] = []
    for item in parts:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def ordered_swc_labels(values: Sequence[str]) -> List[str]:
    normalized = {text_compact(v) for v in values if text_compact(v) in TARGET_SWCS}
    return [swc for swc in TARGET_SWCS if swc in normalized]


def format_pct(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 6)


def text_compact(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def json_compact(value: Any) -> str:
    try:
        return json.dumps(value if value is not None else {}, ensure_ascii=False, sort_keys=True)
    except Exception:
        return json.dumps(str(value), ensure_ascii=False)


def http_json(
    method: str,
    url: str,
    payload: Optional[Dict[str, Any]] = None,
    timeout: int = 30,
    retries: int = 0,
) -> Tuple[Optional[int], Dict[str, Any], str]:
    body: Optional[bytes] = None
    headers: Dict[str, str] = {}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    last_status: Optional[int] = None
    last_json: Dict[str, Any] = {}
    last_text = ""

    for attempt in range(retries + 1):
        req = urlrequest.Request(url=url, data=body, headers=headers, method=method.upper())
        try:
            with urlrequest.urlopen(req, timeout=timeout) as resp:
                status = resp.getcode()
                text = resp.read().decode("utf-8", errors="replace")
                parsed: Dict[str, Any]
                try:
                    maybe = json.loads(text) if text else {}
                    parsed = maybe if isinstance(maybe, dict) else {"data": maybe}
                except json.JSONDecodeError:
                    parsed = {"raw": text}
                return status, parsed, text
        except urlerror.HTTPError as exc:
            status = exc.code
            text = exc.read().decode("utf-8", errors="replace")
            try:
                maybe = json.loads(text) if text else {}
                parsed = maybe if isinstance(maybe, dict) else {"data": maybe}
            except json.JSONDecodeError:
                parsed = {"raw": text}

            last_status, last_json, last_text = status, parsed, text

            if attempt < retries and status >= 500:
                time.sleep(min(3.0, 0.5 * (attempt + 1)))
                continue
            return status, parsed, text
        except (urlerror.URLError, TimeoutError, http.client.RemoteDisconnected, http.client.HTTPException, ConnectionResetError, OSError) as exc:
            last_status = None
            last_json = {"error": str(exc)}
            last_text = str(exc)
            if attempt < retries:
                time.sleep(min(3.0, 0.5 * (attempt + 1)))
                continue
            return last_status, last_json, last_text

    return last_status, last_json, last_text


class LlmFallbackClassifier:
    def __init__(
        self,
        api_base: str,
        timeout: int,
        confidence_threshold: float,
        request_timeout: int,
        retries: int,
    ) -> None:
        self.api_base = str(api_base or "").rstrip("/")
        self.timeout = timeout
        self.confidence_threshold = confidence_threshold
        self.request_timeout = request_timeout
        self.retries = retries

    @staticmethod
    def _models_call_timeout_seconds(model_timeout: int) -> int:
        # Backend model layer now retries in-process with fixed 10s backoff and >=20 attempts.
        # Avoid client timeout/retry from spawning overlapping duplicate /api/models/call requests.
        attempts = 20
        backoff = 10
        return (attempts * model_timeout) + ((attempts - 1) * backoff) + 120

    def _call_via_api(self, prompt: str, model_name: str, timeout: Optional[int] = None) -> Tuple[bool, str]:
        return self._call_via_api_with_label(prompt, model_name=model_name, timeout=timeout, call_label="")

    def _call_via_api_with_label(
        self,
        prompt: str,
        model_name: str,
        timeout: Optional[int] = None,
        call_label: str = "",
    ) -> Tuple[bool, str]:
        if not self.api_base:
            return False, "Missing api_base for LLM API calls"
        url = f"{self.api_base}/api/models/call"
        payload = {
            "prompt": prompt,
            "model": model_name,
            "timeout": int(timeout or self.timeout),
            "call_label": str(call_label or "").strip(),
        }
        per_call_timeout = int(payload["timeout"])
        api_timeout = max(int(self.request_timeout), self._models_call_timeout_seconds(per_call_timeout))
        try:
            status, body, raw = http_json(
                "POST",
                url,
                payload=payload,
                timeout=api_timeout,
                retries=0,
            )
        except Exception as exc:
            return False, str(exc)
        if status != 200:
            err = text_compact(body.get("error") or body.get("raw") or raw or f"HTTP {status}")
            return False, err
        if isinstance(body, dict) and body.get("status") == "success":
            resp = body.get("response")
            return True, str(resp or "")
        err = text_compact(body.get("error") or body.get("message") or body.get("status") or "Unknown error")
        return False, err

    @staticmethod
    def _extract_json_block(text: str) -> Optional[Dict[str, Any]]:
        text = (text or "").strip()
        if not text:
            return None

        candidates = [text]
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            candidates.append(match.group(0))

        for candidate in candidates:
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                continue
        return None

    @staticmethod
    def _normalize_label(raw: Any) -> str:
        label = str(raw or "").strip().upper().replace(" ", "")
        if not label:
            return OTHER_LABEL

        if label in {"OTHER", "SWCOTHER", "UNMAPPED", "UNKNOWN", "SWC-UNK"}:
            return OTHER_LABEL

        if re.fullmatch(r"SWC-\d+", label):
            return label

        if re.fullmatch(r"\d+", label):
            return f"SWC-{label}"

        match = re.search(r"SWC-\d+", label)
        if match:
            return match.group(0)

        return OTHER_LABEL

    @staticmethod
    def _normalize_labels(raw: Any) -> List[str]:
        if raw is None:
            return []
        if isinstance(raw, list):
            candidates = raw
        else:
            candidates = [raw]

        labels: List[str] = []
        seen = set()
        for item in candidates:
            label = LlmFallbackClassifier._normalize_label(item)
            if label in TARGET_SWCS and label not in seen:
                seen.add(label)
                labels.append(label)
        return labels

    def classify_multi(
        self,
        model_name: str,
        address: str,
        findings: List[Dict[str, Any]],
        combined_text: str,
    ) -> Dict[str, Any]:
        findings_excerpt = findings[:20]
        prompt = f"""
You are a smart-contract security classifier.

Task:
Classify the audit findings for address {address} into zero or more labels:
- SWC-101 (Integer Overflow/Underflow)
- SWC-105 (Unprotected Ether Withdrawal)
- SWC-106 (Unprotected SELFDESTRUCT)
- SWC-107 (Reentrancy)
- SWC-115 (tx.origin Authorization)

Rules:
1. Output STRICT JSON only.
2. JSON schema:
   {{
     "labels": ["subset of SWC-101/SWC-105/SWC-106/SWC-107/SWC-115, can be empty"],
     "confidence": 0.0 to 1.0,
     "reason": "short reason"
   }}
3. If uncertain or none match, return empty labels list [].
4. Do not output SWC-OTHER in labels; empty list implies OTHER.

Findings JSON:
{json.dumps(findings_excerpt, ensure_ascii=False)}

Findings text summary:
{combined_text[:5000]}
""".strip()

        ok, response = self._call_via_api_with_label(
            prompt,
            model_name=model_name,
            timeout=self.timeout,
            call_label=f"rq2 classify {address[:10]}",
        )
        if not ok:
            return {
                "labels": [],
                "source": "llm_failed",
                "confidence": 0.0,
                "reason": f"LLM call failed: {response}",
                "raw": "",
            }

        parsed = self._extract_json_block(response)
        if not parsed:
            return {
                "labels": [],
                "source": "llm_failed",
                "confidence": 0.0,
                "reason": "LLM output is not valid JSON",
                "raw": response,
            }

        labels = self._normalize_labels(
            parsed.get("labels")
            or parsed.get("pred_swc_list")
            or parsed.get("pred_swcs")
            or parsed.get("swcs")
        )
        if not labels:
            single_label = self._normalize_label(
                parsed.get("label")
                or parsed.get("pred_primary_swc")
                or parsed.get("swc")
                or parsed.get("prediction")
            )
            if single_label in TARGET_SWCS:
                labels = [single_label]

        confidence = to_float(parsed.get("confidence"), 0.0)
        reason = text_compact(parsed.get("reason") or "")

        source = "llm"
        if labels and confidence < self.confidence_threshold:
            labels = []
            source = "llm_low_confidence"
            reason = (
                f"LLM confidence {confidence:.3f} < threshold {self.confidence_threshold:.3f}; "
                f"fallback to {OTHER_LABEL}."
            )

        return {
            "labels": labels,
            "source": source,
            "confidence": confidence,
            "reason": reason,
            "raw": response,
        }

    def explain_labels(
        self,
        model_name: str,
        address: str,
        chosen_labels: List[str],
        findings: List[Dict[str, Any]],
        combined_text: str,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Ask LLM to explain an already chosen label set without re-classifying."""
        chosen_text = ",".join(chosen_labels) if chosen_labels else OTHER_LABEL
        prompt = f"""
You are a smart-contract security analyst.

Chosen labels (already decided): {chosen_text}
Address: {address}

Task:
Provide a concise explanation for why this label set is reasonable based on findings.
Do NOT change the chosen labels.
Output STRICT JSON:
{{
  "reason": "1-3 short sentences grounded in findings",
  "evidence": ["up to 3 short evidence bullets"]
}}

Findings JSON:
{json.dumps(findings[:20], ensure_ascii=False)}

Findings text summary:
{combined_text[:5000]}
""".strip()

        ok, response = self._call_via_api_with_label(
            prompt,
            model_name=model_name,
            timeout=timeout or self.timeout,
            call_label=f"rq2 explain {address[:10]}",
        )
        if not ok:
            return {
                "ok": False,
                "reason": f"LLM explanation call failed: {response}",
                "raw": "",
            }

        parsed = self._extract_json_block(response)
        if not parsed:
            return {
                "ok": False,
                "reason": "LLM explanation output is not valid JSON",
                "raw": response,
            }

        reason = text_compact(parsed.get("reason") or "")
        evidence_raw = parsed.get("evidence")
        evidence = evidence_raw if isinstance(evidence_raw, list) else []
        evidence_list = [text_compact(x) for x in evidence if text_compact(x)]
        return {
            "ok": True,
            "reason": reason,
            "evidence": evidence_list[:3],
            "raw": response,
        }


def load_ground_truth(ground_truth_csv: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with ground_truth_csv.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            address = normalize_address(row.get("address", ""))
            swc_id = text_compact(row.get("SWC_ID", ""))
            if not address or not swc_id:
                continue
            rows.append(
                {
                    "address": address,
                    "SWC_ID": swc_id,
                    "gt_label": int(row.get("gt_label", 0) or 0),
                    "conflict_flag": int(row.get("conflict_flag", 0) or 0),
                    "pos_votes": int(row.get("pos_votes", 0) or 0),
                    "neg_votes": int(row.get("neg_votes", 0) or 0),
                }
            )
    return rows


def address_order(rows: Sequence[Dict[str, Any]]) -> List[str]:
    ordered: List[str] = []
    seen = set()
    for row in rows:
        address = row["address"]
        if address not in seen:
            seen.add(address)
            ordered.append(address)
    return ordered


def read_contract_code(mainnet_dir: Path, address: str) -> Tuple[Optional[str], Optional[str]]:
    path = mainnet_dir / f"{address}.sol"
    if not path.exists():
        return None, f"Contract source not found: {path}"
    try:
        return path.read_text(encoding="utf-8", errors="replace"), None
    except Exception as exc:  # pragma: no cover
        return None, f"Failed to read contract source {path}: {exc}"


def build_static_tool_index(static_tool_dir: Optional[Path]) -> Dict[str, Path]:
    if static_tool_dir is None or not static_tool_dir.exists():
        return {}

    extension_priority = [".txt", ".md", ".json"]
    indexed: Dict[str, Tuple[int, Path]] = {}

    for rank, ext in enumerate(extension_priority):
        for file_path in static_tool_dir.glob(f"*{ext}"):
            stem = file_path.stem.lower()
            prev = indexed.get(stem)
            if prev is None or rank < prev[0]:
                indexed[stem] = (rank, file_path)

    return {k: v[1] for k, v in indexed.items()}


def load_static_tool_text(
    static_index: Dict[str, Path],
    address: str,
    max_chars: int,
) -> str:
    if not static_index:
        return ""
    target = normalize_address(address)
    file_path = static_index.get(target)
    if file_path is None:
        return ""

    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""

    if max_chars > 0 and len(content) > max_chars:
        return content[:max_chars] + "\n...[TRUNCATED]"
    return content


def build_keyword_map(
    vulnerability_json: Path,
    vulnerability_csv: Path,
    target_swcs: Sequence[str],
) -> Dict[str, List[str]]:
    target_set = set(target_swcs)
    raw_map: Dict[str, set] = {swc: set() for swc in target_swcs}

    # From json mapping
    data = json.loads(vulnerability_json.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        for _, swc_map in data.items():
            if not isinstance(swc_map, dict):
                continue
            for swc, values in swc_map.items():
                if swc not in target_set or not isinstance(values, list):
                    continue
                for value in values:
                    keyword = normalize_keyword(str(value))
                    if keyword:
                        raw_map[swc].add(keyword)

    # From csv (pairs of columns: swc_col, vuln_col)
    with vulnerability_csv.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        for row in reader:
            if not row:
                continue
            for idx in range(0, len(row) - 1, 2):
                swc_cell = text_compact(row[idx])
                vuln_cell = text_compact(row[idx + 1])
                if not swc_cell or not vuln_cell:
                    continue
                discovered_swcs = re.findall(r"SWC-\d+", swc_cell)
                if not discovered_swcs:
                    continue
                keyword = normalize_keyword(vuln_cell)
                if not keyword:
                    continue
                for swc in discovered_swcs:
                    if swc in target_set:
                        raw_map[swc].add(keyword)

    # Manual seed keywords for robustness.
    manual_seed: Dict[str, Iterable[str]] = {
        "SWC-101": [
            "overflow",
            "underflow",
            "integer arithmetic",
            "arithmetic bugs",
            "checked arithmetic",
        ],
        "SWC-105": [
            "unprotected ether withdrawal",
            "arbitrary-send-eth",
            "eth_leak",
            "unsecuredvaluesend",
            "unchecked send",
            "unchecked transfer",
        ],
        "SWC-106": ["selfdestruct", "suicidal", "destroyable", "accessible selfdestruct"],
        "SWC-107": ["reentrancy", "reentrant", "state access after external call"],
        "SWC-115": ["tx.origin", "dependence on tx.origin", "originused", "avoid-tx-origin"],
    }
    for swc, keywords in manual_seed.items():
        for keyword in keywords:
            norm = normalize_keyword(keyword)
            if norm:
                raw_map[swc].add(norm)

    # Return sorted, deterministic keyword lists.
    return {swc: sorted(list(values)) for swc, values in raw_map.items()}


BAD_KEYWORDS = {
    "",
    "io",
    "ka",
    "dz",
    "fp",
    "tp",
    "event",
    "events",
    "function",
    "functions",
    "state",
    "line",
    "style",
    "quotes",
    "pragma",
    "naming convention",
}


def normalize_keyword(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"\s+", " ", text)
    text = text.strip(" ,;:[](){}\"'")
    if not text or text in BAD_KEYWORDS:
        return ""
    if len(text) < 4:
        return ""
    if text.startswith("swc-"):
        return ""
    return text


RULE_PATTERNS: Dict[str, List[Tuple[str, float]]] = {
    "SWC-101": [
        (r"\boverflow\b", 3.0),
        (r"\bunderflow\b", 3.0),
        (r"integer arithmetic", 2.0),
        (r"arithmetic bug", 2.0),
    ],
    "SWC-105": [
        (r"unprotected ether withdrawal", 3.0),
        (r"arbitrary-send", 2.5),
        (r"eth[_\- ]?leak", 2.5),
        (r"unsecuredvaluesend", 2.5),
        (r"unchecked send", 2.0),
    ],
    "SWC-106": [
        (r"\bselfdestruct\b", 4.0),
        (r"\bsuicid", 3.0),
        (r"\bdestroyable\b", 2.0),
    ],
    "SWC-107": [
        (r"\bre-?entran", 4.0),
        (r"state access after external call", 2.5),
        (r"reentrancy", 3.0),
    ],
    "SWC-115": [
        (r"tx\.origin", 4.0),
        (r"tx origin", 3.0),
        (r"originused", 2.0),
        (r"dependence on tx\.origin", 3.0),
    ],
}

RULE_MULTI_MIN_SCORE = 1.0


def classify_by_rules(
    combined_text: str,
    findings: Sequence[Dict[str, Any]],
    keyword_map: Dict[str, List[str]],
) -> Dict[str, Any]:
    merged_text = "\n".join(
        [combined_text]
        + [
            " | ".join(
                [
                    text_compact(item.get("Issue")),
                    text_compact(item.get("Description")),
                    text_compact(item.get("Impact")),
                    text_compact(item.get("Location")),
                ]
            )
            for item in findings
        ]
    ).lower()

    scores: Dict[str, float] = {swc: 0.0 for swc in TARGET_SWCS}
    matched: Dict[str, List[str]] = {swc: [] for swc in TARGET_SWCS}

    # Keyword scoring.
    for swc in TARGET_SWCS:
        for keyword in keyword_map.get(swc, []):
            if keyword and keyword in merged_text:
                add = 1.0
                if len(keyword) >= 12 or " " in keyword or "-" in keyword:
                    add = 2.0
                scores[swc] += add
                if len(matched[swc]) < 30:
                    matched[swc].append(f"kw:{keyword}")

    # Regex scoring.
    for swc in TARGET_SWCS:
        for pattern, weight in RULE_PATTERNS.get(swc, []):
            if re.search(pattern, merged_text):
                scores[swc] += weight
                if len(matched[swc]) < 30:
                    matched[swc].append(f"re:{pattern}")

    ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    labels = [swc for swc, score in ranked if score >= RULE_MULTI_MIN_SCORE]

    if not labels:
        return {
            "labels": [],
            "source": "rule_none_multi",
            "scores": scores,
            "matched": matched,
            "reason": "No rule hit.",
        }

    return {
        "labels": labels,
        "source": "rule_multi",
        "scores": scores,
        "matched": matched,
        "reason": "Rule hits: "
        + ", ".join([f"{swc}({scores[swc]:.1f})" for swc in labels]),
    }


def findings_to_text(findings: Sequence[Dict[str, Any]]) -> str:
    chunks = []
    for idx, item in enumerate(findings, start=1):
        chunks.append(
            "\n".join(
                [
                    f"Finding {idx}",
                    f"Issue: {text_compact(item.get('Issue'))}",
                    f"Severity: {text_compact(item.get('Severity'))}",
                    f"Description: {text_compact(item.get('Description'))}",
                    f"Impact: {text_compact(item.get('Impact'))}",
                    f"Location: {text_compact(item.get('Location'))}",
                ]
            )
        )
    return "\n\n".join(chunks)


def render_progress_bar(percentage: float, width: int = 24) -> str:
    pct = max(0.0, min(100.0, percentage))
    filled = int(round((pct / 100.0) * width))
    return "[" + ("#" * filled) + ("-" * (width - filled)) + "]"


class ParallelProgressBoard:
    """Render one in-place progress bar line per contract for parallel execution."""

    def __init__(self, model: str, addresses: Sequence[str]) -> None:
        self.model = model
        self.addresses = list(addresses)
        self._index: Dict[str, int] = {}
        self._lines: List[str] = []
        self._lock = threading.Lock()
        self.enabled = bool(self.addresses) and sys.stdout.isatty()
        self._line_count = 0
        if not self.enabled:
            return
        print(f"[{self.model}] Parallel live progress ({len(self.addresses)} contracts)")

    def _clip(self, text: str) -> str:
        width = max(40, shutil.get_terminal_size(fallback=(140, 24)).columns)
        max_len = max(20, width - 1)
        if len(text) <= max_len:
            return text
        return text[: max_len - 1] + "…"

    def _short_addr(self, address: str) -> str:
        return address if len(address) <= 12 else address[:12] + "..."

    def _format_line(self, address: str, event: Dict[str, Any]) -> str:
        status = text_compact(event.get("status") or "queued")
        percentage = to_float(event.get("percentage"), 0.0)
        step_name = text_compact(event.get("step_name") or "Queued")
        elapsed = to_float(event.get("elapsed_seconds"), 0.0)
        sid = text_compact(event.get("session_id") or "")
        sid_short = sid[:8] if sid else "-"
        findings = text_compact(event.get("finding_number") or "")
        finding_suffix = f" findings={findings}" if findings else ""
        line = (
            f"[{self.model}] {self._short_addr(address):<16} "
            f"{render_progress_bar(percentage)} {percentage:5.1f}% "
            f"{status:<10} step={step_name:<16} elapsed={elapsed:6.1f}s "
            f"sid={sid_short}{finding_suffix}"
        )
        return self._clip(line)

    def _redraw_locked(self) -> None:
        if not self.enabled:
            return
        if self._line_count <= 0:
            return
        sys.stdout.write(f"\x1b[{self._line_count}A")
        for line in self._lines:
            sys.stdout.write("\x1b[2K\r" + line + "\n")
        sys.stdout.flush()

    def update(self, address: str, event: Dict[str, Any]) -> None:
        if not self.enabled:
            return
        with self._lock:
            idx = self._index.get(address)
            if idx is None:
                idx = len(self._lines)
                self._index[address] = idx
                self._lines.append(self._format_line(address, event))
                self._line_count = len(self._lines)
                # First appearance: print one new line (no full redraw needed).
                print(self._lines[idx])
                return
            self._lines[idx] = self._format_line(address, event)
            self._redraw_locked()

    def complete(self, address: str, row: Dict[str, Any]) -> None:
        if not self.enabled:
            return
        status = text_compact(row.get("audit_status") or "completed")
        pct = 100.0 if status == "completed" else 0.0
        step = "Done" if status == "completed" else status
        event = {
            "status": status,
            "percentage": pct,
            "step_name": step,
            "elapsed_seconds": to_float(row.get("execution_time"), 0.0),
            "session_id": text_compact(row.get("session_id") or ""),
            "finding_number": row.get("finding_number", ""),
        }
        self.update(address, event)


def run_audit_session(
    api_base: str,
    code_snippet: str,
    static_tool: str,
    model: str,
    poll_interval: float,
    max_wait_seconds: int,
    request_timeout: int,
    retries: int,
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Dict[str, Any]:
    start_url = f"{api_base}/api/audit/start"
    start_payload = {
        "code_snippet": code_snippet,
        "static_tool": static_tool,
        "model": model,
    }

    status_code, body, _ = http_json(
        "POST",
        start_url,
        payload=start_payload,
        timeout=request_timeout,
        retries=retries,
    )
    if status_code != 201:
        if progress_callback:
            progress_callback(
                {
                    "status": "start_failed",
                    "percentage": 0.0,
                    "step_name": "Start Failed",
                    "session_id": "",
                    "error": text_compact(body.get("error") or body.get("raw") or f"HTTP {status_code}"),
                }
            )
        return {
            "session_id": "",
            "audit_status": "start_failed",
            "results": {},
            "error": text_compact(body.get("error") or body.get("raw") or f"HTTP {status_code}"),
        }

    session_id = text_compact(body.get("session_id"))
    if not session_id:
        if progress_callback:
            progress_callback(
                {
                    "status": "start_failed",
                    "percentage": 0.0,
                    "step_name": "Missing Session",
                    "session_id": "",
                    "error": "Missing session_id in /start response",
                }
            )
        return {
            "session_id": "",
            "audit_status": "start_failed",
            "results": {},
            "error": "Missing session_id in /start response",
        }

    status_url = f"{api_base}/api/audit/{session_id}/status"
    final_status = "running"
    timeout_error = ""
    last_percentage = 0.0
    last_step_name = "Starting"
    deadline = time.time() + max_wait_seconds
    if progress_callback:
        progress_callback(
            {
                "status": "running",
                "percentage": 0.0,
                "step_name": "Starting",
                "session_id": session_id,
                "elapsed_seconds": 0.0,
            }
        )
    poll_started_at = time.time()

    while time.time() < deadline:
        code, status_body, _ = http_json(
            "GET",
            status_url,
            timeout=request_timeout,
            retries=retries,
        )
        if code == 200:
            final_status = text_compact(status_body.get("status") or "running").lower()
            progress_info = status_body.get("progress", {}) if isinstance(status_body, dict) else {}
            step_name = text_compact(progress_info.get("current_step_name") or "")
            percentage = to_float(progress_info.get("progress_percentage"), 0.0)
            last_percentage = percentage
            if step_name:
                last_step_name = step_name
            if progress_callback:
                progress_callback(
                    {
                        "status": final_status,
                        "percentage": percentage,
                        "step_name": step_name,
                        "session_id": session_id,
                        "elapsed_seconds": time.time() - poll_started_at,
                    }
                )
            if final_status in {"completed", "failed", "stopped"}:
                break
        elif code == 404:
            final_status = "session_lost"
            timeout_error = (
                f"Session not found during status polling (HTTP 404). "
                f"Likely backend restart or in-memory session reset "
                f"(session_id={session_id})"
            )
            if progress_callback:
                progress_callback(
                    {
                        "status": final_status,
                        "percentage": 0.0,
                        "step_name": "Session Lost",
                        "session_id": session_id,
                        "elapsed_seconds": time.time() - poll_started_at,
                        "error": timeout_error,
                    }
                )
            break
        time.sleep(max(0.2, poll_interval))

    if final_status not in {"completed", "failed", "stopped"}:
        final_status = "timeout"
        timeout_error = (
            f"Session status polling timeout after {max_wait_seconds}s "
            f"(session_id={session_id})"
        )
        if progress_callback:
            progress_callback(
                {
                    "status": "timeout",
                    "percentage": last_percentage,
                    "step_name": f"Timeout (last={last_step_name})",
                    "session_id": session_id,
                    "elapsed_seconds": time.time() - poll_started_at,
                }
            )
        # Avoid leaving backend sessions running after client-side timeout.
        stop_url = f"{api_base}/api/audit/{session_id}/stop"
        stop_code, _, _ = http_json(
            "POST",
            stop_url,
            payload={},
            timeout=request_timeout,
            retries=1,
        )
        if stop_code == 200:
            timeout_error = f"{timeout_error}; stop_requested=true"

    results_url = f"{api_base}/api/audit/{session_id}/results"
    result_payload: Dict[str, Any] = {}
    for _ in range(10):
        code, result_body, _ = http_json(
            "GET",
            results_url,
            timeout=request_timeout,
            retries=retries,
        )
        if code == 200:
            result_payload = result_body
            break
        if final_status in {"completed", "failed", "stopped"}:
            time.sleep(1.0)
    if progress_callback and final_status in {"completed", "failed", "stopped"}:
        final_step_name = "Done"
        if final_status == "failed":
            final_step_name = "Failed"
        elif final_status == "stopped":
            final_step_name = "Stopped"
        progress_callback(
            {
                "status": final_status,
                "percentage": 100.0 if final_status == "completed" else 0.0,
                "step_name": final_step_name,
                "session_id": session_id,
                "elapsed_seconds": time.time() - poll_started_at,
            }
        )

    return {
        "session_id": session_id,
        "audit_status": final_status,
        "results": result_payload,
        "error": timeout_error,
    }


def resolve_models(api_base: str, models_arg: List[str], request_timeout: int, retries: int) -> List[str]:
    if not models_arg:
        return ["deepseek_school"]

    if len(models_arg) == 1 and models_arg[0].lower() == "all":
        info_url = f"{api_base}/api/models/info"
        code, body, _ = http_json("GET", info_url, timeout=request_timeout, retries=retries)
        if code != 200:
            raise RuntimeError(
                f"Failed to query available models from {info_url}: HTTP {code}, body={body}"
            )

        models_info = body.get("models") if isinstance(body, dict) else {}
        if not isinstance(models_info, dict):
            raise RuntimeError("Invalid response from /api/models/info: missing 'models'")

        available = [
            key
            for key in DEFAULT_MODEL_ORDER
            if key in models_info and bool((models_info.get(key) or {}).get("available", False))
        ]
        if not available:
            # fallback to explicit available summary if structure changes
            for key, item in models_info.items():
                if key == "auto":
                    continue
                if isinstance(item, dict) and bool(item.get("available")):
                    available.append(key)

        available = [m for m in available if m != "auto"]
        if not available and isinstance(models_info.get("auto"), dict):
            if bool(models_info["auto"].get("available", False)):
                available = ["auto"]

        if not available:
            raise RuntimeError("No available model found from /api/models/info")
        return available

    # Explicit list
    resolved: List[str] = []
    seen = set()
    for name in models_arg:
        model = name.strip()
        if model and model not in seen:
            seen.add(model)
            resolved.append(model)
    if not resolved:
        resolved = ["deepseek_school"]
    return resolved


def write_csv(path: Path, rows: Sequence[Dict[str, Any]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def append_csv_row(path: Path, row: Dict[str, Any], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writerow({key: row.get(key, "") for key in fieldnames})


def contract_level_fieldnames() -> List[str]:
    return [
        "address",
        "session_id",
        "audit_status",
        "model",
        "pred_swc_list",
        "pred_swc_count",
        "is_other",
        "pred_source",
        "pred_reason",
        "rule_scores_json",
        "rule_matched_json",
        "llm_fallback_json",
        "llm_explanation_json",
        "full_report_available",
        "full_report_chars",
        "full_report_path",
        "audit_plan_chars",
        "audit_plan_path",
        "workflow_debug_dir",
        "static_summary_chars",
        "static_summary_path",
        "rag_used",
        "rag_enabled",
        "rag_effective_task_count",
        "rag_effective_evidence_count",
        "rag_similarity_threshold",
        "record_json_path",
        "audit_attempts",
        "empty_report_retries_used",
        "finding_number",
        "execution_time",
        "gt_swc_set",
        "error",
    ]


def load_existing_contract_rows(contract_csv_path: Path) -> List[Dict[str, Any]]:
    if not contract_csv_path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    with contract_csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            address = normalize_address(row.get("address", ""))
            if not address:
                continue
            normalized = dict(row)
            normalized["address"] = address
            rows.append(normalized)
    # Keep last row per address in case of accidental duplicates.
    rows_by_addr: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        rows_by_addr[row["address"]] = row
    return [rows_by_addr[a] for a in sorted(rows_by_addr.keys())]


def resolve_resume_run_root(output_dir: Path, requested_run_id: str) -> Tuple[str, Path]:
    run_id = text_compact(requested_run_id)
    if run_id:
        run_root = output_dir / run_id
        if not run_root.exists():
            raise SystemExit(f"--resume run_id not found: {run_root}")
        return run_id, run_root

    candidates = sorted([p for p in output_dir.iterdir() if p.is_dir()]) if output_dir.exists() else []
    if not candidates:
        raise SystemExit(f"--resume requested but no previous run directories found in {output_dir}")
    run_root = candidates[-1]
    return run_root.name, run_root


def persist_full_report_for_row(row: Dict[str, Any], model_dir: Optional[Path]) -> None:
    if text_compact(row.get("audit_status") or "") != "completed" or bool(row.get("fatal_error", False)):
        row["full_report_available"] = 0
        row["full_report_chars"] = 0
        row["full_report_path"] = ""
        row.pop("_full_report_text", None)
        return
    report_text = str(row.pop("_full_report_text", "") or "")

    if not report_text:
        row["full_report_available"] = int(row.get("full_report_available", 0) or 0)
        row["full_report_chars"] = int(row.get("full_report_chars", 0) or 0)
        row["full_report_path"] = str(row.get("full_report_path", "") or "")
        return

    row["full_report_available"] = 1
    row["full_report_chars"] = len(report_text)

    if model_dir is None:
        row["full_report_path"] = ""
        return

    address = normalize_address(row.get("address", "")) or "unknown"
    contract_dir = model_dir / "contracts" / address
    contract_dir.mkdir(parents=True, exist_ok=True)
    report_path = contract_dir / "report.md"
    report_path.write_text(report_text, encoding="utf-8")
    row["full_report_path"] = str(report_path)


def persist_static_summary_for_row(row: Dict[str, Any], model_dir: Optional[Path]) -> None:
    """Persist per-contract static analysis summary text."""
    if text_compact(row.get("audit_status") or "") != "completed" or bool(row.get("fatal_error", False)):
        row["static_summary_chars"] = 0
        row["static_summary_path"] = ""
        row.pop("_static_tool_text", None)
        return
    static_summary = str(row.pop("_static_tool_text", "") or "")
    row["static_summary_chars"] = len(static_summary)

    if not static_summary or model_dir is None:
        row["static_summary_path"] = ""
        return

    address = normalize_address(row.get("address", "")) or "unknown"
    contract_dir = model_dir / "contracts" / address
    contract_dir.mkdir(parents=True, exist_ok=True)
    static_path = contract_dir / "static_summary.txt"
    static_path.write_text(static_summary, encoding="utf-8")
    row["static_summary_path"] = str(static_path)


def persist_audit_plan_for_row(row: Dict[str, Any], model_dir: Optional[Path]) -> None:
    """Persist per-contract audit plan raw output text."""
    if text_compact(row.get("audit_status") or "") != "completed" or bool(row.get("fatal_error", False)):
        row["audit_plan_chars"] = 0
        row["audit_plan_path"] = ""
        row.pop("_audit_plan_text", None)
        return
    audit_plan_text = str(row.pop("_audit_plan_text", "") or "")
    row["audit_plan_chars"] = len(audit_plan_text)

    if not audit_plan_text or model_dir is None:
        row["audit_plan_path"] = ""
        return

    address = normalize_address(row.get("address", "")) or "unknown"
    contract_dir = model_dir / "contracts" / address
    contract_dir.mkdir(parents=True, exist_ok=True)
    audit_plan_path = contract_dir / "audit_plan.txt"
    audit_plan_path.write_text(audit_plan_text, encoding="utf-8")
    row["audit_plan_path"] = str(audit_plan_path)


def persist_workflow_debug_for_row(row: Dict[str, Any], model_dir: Optional[Path]) -> None:
    """Persist node-level workflow debug input/output as plain text files."""
    row["workflow_debug_dir"] = ""
    if model_dir is None:
        return
    if text_compact(row.get("audit_status") or "") != "completed" or bool(row.get("fatal_error", False)):
        return

    raw = row.get("raw")
    if not isinstance(raw, dict):
        return
    result_payload = raw.get("result_payload")
    if not isinstance(result_payload, dict):
        return
    execution_summary = result_payload.get("execution_summary")
    if not isinstance(execution_summary, dict):
        return
    debug_artifacts = execution_summary.get("debug_artifacts")
    if not isinstance(debug_artifacts, dict):
        return

    address = normalize_address(row.get("address", "")) or "unknown"
    debug_dir = model_dir / "contracts" / address / "workflow_debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    row["workflow_debug_dir"] = str(debug_dir)

    ordered_stages = [
        ("01", "initial_analysis", debug_artifacts.get("initial_analysis")),
        ("02", "audit_plan", debug_artifacts.get("audit_plan")),
        ("03", "parameter_extractor", debug_artifacts.get("parameter_extractor")),
        ("04", "iteration", debug_artifacts.get("iteration")),
        ("05", "format_converter", debug_artifacts.get("format_converter")),
    ]

    for prefix, stage_name, stage_data in ordered_stages:
        if not isinstance(stage_data, dict):
            continue
        input_text = str(stage_data.get("input_text", "") or "")
        output_text = str(stage_data.get("output_text", "") or "")
        if input_text:
            (debug_dir / f"{prefix}_{stage_name}_input.txt").write_text(input_text, encoding="utf-8")
        if output_text:
            (debug_dir / f"{prefix}_{stage_name}_output.txt").write_text(output_text, encoding="utf-8")

        if stage_name == "iteration":
            task_runs = stage_data.get("task_runs")
            if isinstance(task_runs, list):
                for item in task_runs:
                    if not isinstance(item, dict):
                        continue
                    attempt = int(item.get("attempt", 0) or 0)
                    task_index = int(item.get("task_index", 0) or 0)
                    task_id = item.get("task_id", "")
                    task_prefix = (
                        f"{prefix}_{stage_name}_attempt_{attempt:02d}_"
                        f"task_{task_index:02d}_id_{task_id}"
                    )
                    task_input = str(item.get("input_text", "") or "")
                    task_output = str(item.get("output_text", "") or "")
                    if task_input:
                        (debug_dir / f"{task_prefix}_input.txt").write_text(task_input, encoding="utf-8")
                    if task_output:
                        (debug_dir / f"{task_prefix}_output.txt").write_text(task_output, encoding="utf-8")

            (debug_dir / f"{prefix}_{stage_name}_summary.json").write_text(
                json.dumps(stage_data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )


def persist_contract_record_for_row(row: Dict[str, Any], model_dir: Optional[Path]) -> None:
    """Persist one complete per-contract record JSON immediately after audit."""
    if model_dir is None:
        row["record_json_path"] = ""
        return
    if text_compact(row.get("audit_status") or "") != "completed" or bool(row.get("fatal_error", False)):
        row["record_json_path"] = ""
        return

    address = normalize_address(row.get("address", "")) or "unknown"
    contract_dir = model_dir / "contracts" / address
    contract_dir.mkdir(parents=True, exist_ok=True)
    record_path = contract_dir / "record.json"

    # Keep a self-contained snapshot for this contract (includes raw API payload before trimming).
    snapshot = {
        k: v
        for k, v in row.items()
        if k not in {"_full_report_text", "_static_tool_text", "_audit_plan_text"}
    }
    record_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    row["record_json_path"] = str(record_path)


def compute_summary_metrics(
    pair_rows: Sequence[Dict[str, Any]],
    target_swcs: Sequence[str],
) -> List[Dict[str, Any]]:
    output: List[Dict[str, Any]] = []

    def metrics_for(rows: Sequence[Dict[str, Any]]) -> Tuple[int, int, int, int]:
        tp = sum(1 for r in rows if int(r["gt_label"]) == 1 and int(r["pred_label"]) == 1)
        fp = sum(1 for r in rows if int(r["gt_label"]) == 0 and int(r["pred_label"]) == 1)
        tn = sum(1 for r in rows if int(r["gt_label"]) == 0 and int(r["pred_label"]) == 0)
        fn = sum(1 for r in rows if int(r["gt_label"]) == 1 and int(r["pred_label"]) == 0)
        return tp, fp, tn, fn

    overall_tp, overall_fp, overall_tn, overall_fn = metrics_for(pair_rows)
    overall_total = len(pair_rows)
    overall_other_rate = format_pct(sum(int(r.get("is_other", 0)) for r in pair_rows), overall_total)

    def add_row(scope: str, swc: str, tp: int, fp: int, tn: int, fn: int, other_rate: float) -> None:
        precision = format_pct(tp, tp + fp)
        recall = format_pct(tp, tp + fn)
        f1 = 0.0
        if precision + recall > 0:
            f1 = round(2 * precision * recall / (precision + recall), 6)
        accuracy = format_pct(tp + tn, tp + fp + tn + fn)
        output.append(
            {
                "scope": scope,
                "swc": swc,
                "tp": tp,
                "fp": fp,
                "tn": tn,
                "fn": fn,
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "accuracy": accuracy,
                "other_rate": other_rate,
            }
        )

    add_row("overall", "ALL", overall_tp, overall_fp, overall_tn, overall_fn, overall_other_rate)

    for swc in target_swcs:
        subset = [r for r in pair_rows if r.get("SWC_ID") == swc]
        tp, fp, tn, fn = metrics_for(subset)
        other_rate = format_pct(sum(int(r.get("is_other", 0)) for r in subset), len(subset))
        add_row("per_swc", swc, tp, fp, tn, fn, other_rate)

    return output


def summarize_findings(results_payload: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], str]:
    findings = results_payload.get("findings", [])
    if not isinstance(findings, list):
        findings = []

    normalized: List[Dict[str, Any]] = []
    for item in findings:
        if not isinstance(item, dict):
            continue
        normalized.append(
            {
                "Issue": text_compact(item.get("Issue")),
                "Severity": text_compact(item.get("Severity")),
                "Description": text_compact(item.get("Description")),
                "Impact": text_compact(item.get("Impact")),
                "Location": text_compact(item.get("Location")),
            }
        )

    combined_text = findings_to_text(normalized)
    return normalized, combined_text


def is_trivial_report_text(report_text: str) -> bool:
    normalized = text_compact(report_text).lower()
    return normalized in {"", "[]", "{}", "null", "none"}


def build_llm_signal_text(
    findings_text: str,
    full_report_text: str,
    static_tool_text: str,
    source_code: str,
) -> str:
    parts: List[str] = []
    if findings_text.strip():
        parts.append(findings_text.strip())

    # When findings are empty, include other artifacts to avoid no-signal collapse.
    if not parts:
        if not is_trivial_report_text(full_report_text):
            parts.append(f"Full report raw output:\n{full_report_text.strip()[:6000]}")
        if text_compact(static_tool_text):
            parts.append(f"Static analysis context:\n{static_tool_text.strip()[:6000]}")
        if text_compact(source_code):
            parts.append(f"Contract source excerpt:\n{source_code.strip()[:6000]}")

    return "\n\n".join([p for p in parts if p.strip()])[:12000]


def process_one_address(
    *,
    address: str,
    model: str,
    api_base: str,
    mainnet_dir: Path,
    static_index: Dict[str, Path],
    static_tool_max_chars: int,
    poll_interval: float,
    max_wait_seconds: int,
    request_timeout: int,
    retries: int,
    keyword_map: Dict[str, List[str]],
    llm_classifier: LlmFallbackClassifier,
    enable_llm_fallback: bool,
    enable_llm_explanation: bool,
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Dict[str, Any]:
    gt_label_set: List[str] = []

    code, read_error = read_contract_code(mainnet_dir, address)
    if read_error:
        return {
            "address": address,
            "session_id": "",
            "audit_status": "source_missing",
            "model": model,
            "pred_swc_list": "",
            "pred_swc_count": 0,
            "is_other": 1,
            "pred_source": "source_missing",
            "pred_reason": "Contract source missing; no SWC signal.",
            "rule_scores_json": "{}",
            "rule_matched_json": "{}",
            "llm_fallback_json": "{}",
            "llm_explanation_json": "{}",
            "full_report_available": 0,
            "full_report_chars": 0,
            "full_report_path": "",
            "_static_tool_text": "",
            "_full_report_text": "",
            "rag_used": 0,
            "rag_enabled": 0,
            "rag_effective_task_count": 0,
            "rag_effective_evidence_count": 0,
            "rag_similarity_threshold": 0.0,
            "audit_attempts": 0,
            "empty_report_retries_used": 0,
            "finding_number": 0,
            "execution_time": "",
            "gt_swc_set": "",
            "error": read_error,
            "raw": {
                "address": address,
                "model": model,
                "error": read_error,
            },
        }

    static_tool_text = load_static_tool_text(static_index, address, static_tool_max_chars)
    api_result = run_audit_session(
        api_base=api_base,
        code_snippet=code or "",
        static_tool=static_tool_text,
        model=model,
        poll_interval=poll_interval,
        max_wait_seconds=max_wait_seconds,
        request_timeout=request_timeout,
        retries=retries,
        progress_callback=progress_callback,
    )
    early_audit_status = text_compact(api_result.get("audit_status") or "unknown").lower()
    early_error = text_compact(api_result.get("error") or "")
    results_payload = api_result.get("results") if isinstance(api_result.get("results"), dict) else {}
    execution_summary = (
        results_payload.get("execution_summary")
        if isinstance(results_payload.get("execution_summary"), dict)
        else {}
    )
    fatal_error = bool(execution_summary.get("fatal_error", False))
    fatal_reason = text_compact(execution_summary.get("fatal_reason") or early_error or "")
    if fatal_error or fatal_reason.lower().startswith("fatal") or "exhausted" in fatal_reason.lower():
        raise FatalAuditStop(fatal_reason or "LLM retry limit exhausted")
    if early_audit_status in {"start_failed", "session_lost"}:
        raise FatalAuditStop(early_error or f"audit_status={early_audit_status}")
    if early_audit_status == "failed":
        if not results_payload or "workflow failed at step" in early_error.lower():
            raise FatalAuditStop(early_error or "audit_status=failed")
        if bool(execution_summary.get("error", False)):
            raise FatalAuditStop(fatal_reason or "workflow execution error")
    if early_audit_status == "timeout" and not results_payload:
        raise FatalAuditStop(early_error or "audit status timeout without results")
    findings, _ = summarize_findings(results_payload)

    session_id = text_compact(api_result.get("session_id"))
    audit_status = text_compact(api_result.get("audit_status") or "unknown")
    error = text_compact(api_result.get("error") or "")
    full_report_text = str(results_payload.get("full_report", "") or "")

    finding_number = int(results_payload.get("finding_number", len(findings)) or len(findings))
    selected_is_empty_report = (
        finding_number <= 0
        and not findings
        and full_report_text.strip() in {"", "[]"}
    )
    attempts_meta: List[Dict[str, Any]] = [
        {
            "attempt": 1,
            "session_id": session_id,
            "audit_status": audit_status,
            "error": error,
            "finding_number": finding_number,
            "full_report_chars": len(full_report_text),
            "empty_report": selected_is_empty_report,
        }
    ]
    retries_used = 0

    findings_text = findings_to_text(findings)
    llm_signal_text = build_llm_signal_text(
        findings_text=findings_text,
        full_report_text=full_report_text,
        static_tool_text=static_tool_text,
        source_code=code or "",
    )
    execution_time = results_payload.get("execution_time", "")
    execution_summary = (
        results_payload.get("execution_summary")
        if isinstance(results_payload.get("execution_summary"), dict)
        else {}
    )
    debug_artifacts = (
        execution_summary.get("debug_artifacts")
        if isinstance(execution_summary.get("debug_artifacts"), dict)
        else {}
    )
    audit_plan_text = str(debug_artifacts.get("audit_plan_raw", "") or "")
    rag_used = 1 if bool(execution_summary.get("rag_used", False)) else 0
    rag_enabled = 1 if bool(execution_summary.get("rag_enabled", False)) else 0
    rag_effective_task_count = int(execution_summary.get("rag_effective_retrieval_tasks", 0) or 0)
    rag_effective_evidence_count = int(execution_summary.get("rag_effective_retrieved_evidence", 0) or 0)
    rag_similarity_threshold = to_float(execution_summary.get("rag_similarity_threshold"), 0.0)

    # Rule-first multi-label classification.
    rule_result = classify_by_rules(findings_text, findings, keyword_map)
    rule_labels = ordered_swc_labels(rule_result.get("labels", []))
    pred_source = text_compact(rule_result.get("source") or "rule_none_multi")
    llm_result: Dict[str, Any] = {}
    llm_explanation: Dict[str, Any] = {}

    has_classifiable_signal = bool(findings or llm_signal_text.strip())
    llm_labels: List[str] = []

    # True fallback: only call LLM classifier when rules produced no labels.
    if enable_llm_fallback and has_classifiable_signal and not rule_labels:
        llm_result = llm_classifier.classify_multi(
            model_name=model,
            address=address,
            findings=findings,
            combined_text=llm_signal_text,
        )
        llm_labels = ordered_swc_labels(llm_result.get("labels", []))

    final_labels = ordered_swc_labels(list(set(rule_labels) | set(llm_labels)))
    is_other = 1 if len(final_labels) == 0 else 0

    if is_other:
        if not has_classifiable_signal:
            pred_source = "no_signal"
        elif llm_result:
            pred_source = text_compact(llm_result.get("source") or pred_source or "llm_none")
        else:
            pred_source = pred_source or "rule_none_multi"
    else:
        if rule_labels and llm_labels:
            pred_source = "hybrid_rule_llm"
        elif rule_labels:
            pred_source = pred_source or "rule_multi"
        elif llm_labels:
            pred_source = text_compact(llm_result.get("source") or "llm_multi")

    final_reason = text_compact(rule_result.get("reason") or "")
    llm_reason = text_compact(llm_result.get("reason") or "")
    if llm_reason:
        if final_reason:
            final_reason = f"{final_reason} | LLM: {llm_reason}"
        else:
            final_reason = llm_reason

    # Always ask LLM for rationale on the chosen label set when enabled.
    if enable_llm_explanation and has_classifiable_signal:
        llm_explanation = llm_classifier.explain_labels(
            model_name=model,
            address=address,
            chosen_labels=final_labels,
            findings=findings,
            combined_text=llm_signal_text,
        )
        if llm_explanation.get("ok"):
            reason_text = text_compact(llm_explanation.get("reason") or "")
            evidence = llm_explanation.get("evidence", [])
            evidence_text = "; ".join([text_compact(x) for x in evidence if text_compact(x)])
            if reason_text and evidence_text:
                final_reason = f"{reason_text} Evidence: {evidence_text}"
            elif reason_text:
                final_reason = reason_text

    if audit_status == "start_failed" and not error:
        error = "Audit start failed"

    pred_swc_list = "|".join(final_labels)
    rule_scores_json = json_compact(rule_result.get("scores", {}))
    rule_matched_json = json_compact(rule_result.get("matched", {}))
    llm_fallback_json = json_compact(llm_result)
    llm_explanation_json = json_compact(llm_explanation)

    return {
        "address": address,
        "session_id": session_id,
        "audit_status": audit_status,
        "model": model,
        "pred_swc_list": pred_swc_list,
        "pred_swc_count": len(final_labels),
        "is_other": is_other,
        "pred_source": pred_source,
        "pred_reason": final_reason,
        "rule_scores_json": rule_scores_json,
        "rule_matched_json": rule_matched_json,
        "llm_fallback_json": llm_fallback_json,
        "llm_explanation_json": llm_explanation_json,
        "full_report_available": 1 if full_report_text else 0,
        "full_report_chars": len(full_report_text),
        "full_report_path": "",
        "_audit_plan_text": audit_plan_text,
        "_static_tool_text": static_tool_text,
        "_full_report_text": full_report_text,
        "rag_used": rag_used,
        "rag_enabled": rag_enabled,
        "rag_effective_task_count": rag_effective_task_count,
        "rag_effective_evidence_count": rag_effective_evidence_count,
        "rag_similarity_threshold": rag_similarity_threshold,
        "audit_attempts": len(attempts_meta),
        "empty_report_retries_used": retries_used,
        "finding_number": finding_number,
        "execution_time": execution_time,
        "gt_swc_set": "|".join(gt_label_set),
        "error": error,
        "raw": {
            "address": address,
            "model": model,
            "session_id": session_id,
            "audit_status": audit_status,
            "error": error,
            "findings": findings,
            "result_payload": results_payload,
            "rule_result": rule_result,
            "llm_result": llm_result,
            "rule_labels": rule_labels,
            "llm_labels": llm_labels,
            "pred_labels": final_labels,
            "pred_swc_list": pred_swc_list,
            "pred_source": pred_source,
            "is_other": is_other,
            "pred_reason": final_reason,
            "rule_scores_json": rule_scores_json,
            "rule_matched_json": rule_matched_json,
            "llm_fallback_json": llm_fallback_json,
            "llm_explanation_json": llm_explanation_json,
            "static_tool_used": bool(static_tool_text),
            "audit_plan_text": audit_plan_text,
            "debug_artifacts": debug_artifacts,
            "rag_used": rag_used,
            "rag_enabled": bool(rag_enabled),
            "rag_effective_task_count": rag_effective_task_count,
            "rag_effective_evidence_count": rag_effective_evidence_count,
            "rag_similarity_threshold": rag_similarity_threshold,
            "llm_explanation": llm_explanation,
            "audit_attempts": attempts_meta,
            "selected_is_empty_report": selected_is_empty_report,
            "empty_report_retries_used": retries_used,
        },
    }


def build_pair_rows(
    gt_rows: Sequence[Dict[str, Any]],
    contract_rows_by_address: Dict[str, Dict[str, Any]],
    model_name: str,
) -> List[Dict[str, Any]]:
    pair_rows: List[Dict[str, Any]] = []
    for row in gt_rows:
        address = row["address"]
        contract = contract_rows_by_address.get(address)

        pred_list = ""
        pred_labels: List[str] = []
        is_other = 1
        pred_source = "missing_contract_row"
        session_id = ""
        full_report_available = 0
        full_report_chars = 0
        full_report_path = ""
        if contract:
            pred_list = str(contract.get("pred_swc_list", "") or "")
            pred_labels = ordered_swc_labels(pred_list.split("|") if pred_list else [])
            is_other = int(contract.get("is_other", 1) or 0)
            pred_source = str(contract.get("pred_source", "") or "")
            session_id = str(contract.get("session_id", "") or "")
            full_report_available = int(contract.get("full_report_available", 0) or 0)
            full_report_chars = int(contract.get("full_report_chars", 0) or 0)
            full_report_path = str(contract.get("full_report_path", "") or "")

        pred_label = 1 if row["SWC_ID"] in pred_labels else 0

        pair_rows.append(
            {
                "address": address,
                "SWC_ID": row["SWC_ID"],
                "gt_label": int(row["gt_label"]),
                "conflict_flag": int(row["conflict_flag"]),
                "pred_swc_list": pred_list,
                "pred_label": pred_label,
                "is_other": is_other,
                "pred_source": pred_source,
                "session_id": session_id,
                "model": model_name,
                "full_report_available": full_report_available,
                "full_report_chars": full_report_chars,
                "full_report_path": full_report_path,
            }
        )

    return pair_rows


def patch_contract_rows_with_gt_set(
    contract_rows: List[Dict[str, Any]],
    gt_rows_for_model: Sequence[Dict[str, Any]],
) -> None:
    swcs_by_addr: Dict[str, set] = {}
    for row in gt_rows_for_model:
        swcs_by_addr.setdefault(row["address"], set()).add(row["SWC_ID"])

    for row in contract_rows:
        swc_set = sorted(swcs_by_addr.get(row["address"], set()))
        row["gt_swc_set"] = "|".join(swc_set)


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def build_parser(repo_root: Path) -> argparse.ArgumentParser:
    default_gt = repo_root / "EmpiricalSCST" / "_RQ2" / "manual" / "ground_truth" / "RQ2_ground_truth.csv"
    default_mainnet = repo_root / "EmpiricalSCST" / "mainnet"
    default_vuln_json = repo_root / "EmpiricalSCST" / "_RQ2" / "RQ2_tools_vulnerabilities.json"
    default_vuln_csv = repo_root / "EmpiricalSCST" / "_RQ2" / "vulnerability_types.csv"
    default_output = repo_root / "test" / "results"

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=None, help="Optional config file (.yaml/.yml/.json)")

    sub = parser.add_subparsers(dest="command", required=True)

    def add_common_arguments(target: argparse.ArgumentParser) -> None:
        target.add_argument("--api-base", default=None, help="SmartAuditFlow base URL")
        target.add_argument("--ground-truth-csv", default=None, help="RQ2 ground truth CSV path")
        target.add_argument("--mainnet-dir", default=None, help="Mainnet contracts directory")
        target.add_argument("--vulnerability-json", default=None, help="RQ2 tools vulnerabilities JSON")
        target.add_argument("--vulnerability-csv", default=None, help="vulnerability_types.csv path")
        target.add_argument("--output-dir", default=None, help="Output root directory")
        target.add_argument("--run-id", default=None, help="Resume target run_id (used with --resume)")

        target.add_argument(
            "--models",
            default=None,
            help="Model list: deepseek_school,deepseek_silicon,deepseek or all",
        )
        target.add_argument("--concurrency", type=int, default=None, help="Concurrent workers per model")
        target.add_argument("--poll-interval", type=float, default=None, help="Status polling interval (seconds)")
        target.add_argument("--max-wait-seconds", type=int, default=None, help="Per-session max wait seconds")
        target.add_argument("--request-timeout", type=int, default=None, help="HTTP request timeout (seconds)")
        target.add_argument("--retry", type=int, default=None, help="HTTP retries per request")

        target.add_argument("--static-tool-dir", default=None, help="Optional static_tool input directory")
        target.add_argument("--static-tool-max-chars", type=int, default=None, help="Max chars for static_tool input")

        target.add_argument(
            "--enable-llm-fallback",
            dest="enable_llm_fallback",
            action="store_true",
            help="Enable LLM fallback when rules cannot decide",
        )
        target.add_argument(
            "--disable-llm-fallback",
            dest="enable_llm_fallback",
            action="store_false",
            help="Disable LLM fallback and force SWC-OTHER when rules cannot decide",
        )
        target.set_defaults(enable_llm_fallback=None)

        target.add_argument("--llm-timeout", type=int, default=None, help="LLM fallback timeout (seconds)")
        target.add_argument(
            "--llm-confidence-threshold",
            type=float,
            default=None,
            help="Below threshold => SWC-OTHER",
        )
        target.add_argument(
            "--llm-explain",
            dest="enable_llm_explanation",
            action="store_true",
            help="Always run one LLM pass to explain final chosen label set",
        )
        target.add_argument(
            "--no-llm-explain",
            dest="enable_llm_explanation",
            action="store_false",
            help="Disable LLM explanation pass for final label set",
        )
        target.set_defaults(enable_llm_explanation=None)
        target.add_argument(
            "--live-progress",
            dest="live_progress",
            action="store_true",
            help="Show live progress line while polling session status",
        )
        target.add_argument(
            "--no-live-progress",
            dest="live_progress",
            action="store_false",
            help="Disable live progress line",
        )
        target.set_defaults(live_progress=None)
        target.add_argument(
            "--resume",
            dest="resume",
            action="store_true",
            help="Resume from existing run outputs and skip completed addresses",
        )
        target.add_argument(
            "--no-resume",
            dest="resume",
            action="store_false",
            help="Always start a new run directory",
        )
        target.set_defaults(resume=None)
        target.add_argument("--verbose", action="store_true", help="Verbose logging")

    single = sub.add_parser("single", help="Run one address")
    add_common_arguments(single)
    single.add_argument("--address", default=None, help="Contract address (required for single mode)")

    batch = sub.add_parser("batch", help="Run batch addresses from ground truth")
    add_common_arguments(batch)
    batch.add_argument("--limit", type=int, default=None, help="Limit by unique addresses")

    parser.set_defaults(
        _default_api_base="http://127.0.0.1:5001",
        _default_ground_truth_csv=str(default_gt),
        _default_mainnet_dir=str(default_mainnet),
        _default_vulnerability_json=str(default_vuln_json),
        _default_vulnerability_csv=str(default_vuln_csv),
        _default_output_dir=str(default_output),
        _default_run_id="",
        _default_models="deepseek_school",
        _default_concurrency=1,
        _default_poll_interval=3.0,
        _default_max_wait_seconds=18000,
        _default_request_timeout=30,
        _default_retry=2,
        _default_static_tool_dir="",
        _default_static_tool_max_chars=12000,
        _default_enable_llm_fallback=True,
        _default_enable_llm_explanation=True,
        _default_llm_timeout=40,
        _default_llm_confidence_threshold=0.6,
        _default_live_progress=True,
        _default_resume=False,
    )

    return parser


def merged_setting(
    args: argparse.Namespace,
    config: Dict[str, Any],
    key: str,
    default_key: str,
) -> Any:
    value = getattr(args, key, None)
    if value is not None:
        return value
    if key in config and config[key] is not None:
        return config[key]
    return getattr(args, default_key)


def run_for_model(
    *,
    model: str,
    addresses: Sequence[str],
    gt_rows_model: Sequence[Dict[str, Any]],
    options: Dict[str, Any],
    keyword_map: Dict[str, List[str]],
    llm_classifier: LlmFallbackClassifier,
    static_index: Dict[str, Path],
) -> Dict[str, Any]:
    existing_contract_rows = options.get("existing_contract_rows", []) or []
    contract_rows: List[Dict[str, Any]] = []
    contract_rows_by_addr: Dict[str, Dict[str, Any]] = {}
    for row in existing_contract_rows:
        row_copy = dict(row)
        address = normalize_address(row_copy.get("address", ""))
        if not address:
            continue
        row_copy["address"] = address
        contract_rows_by_addr[address] = row_copy
    contract_rows.extend(contract_rows_by_addr.values())

    gt_swc_by_addr: Dict[str, set] = {}
    for gt_row in gt_rows_model:
        gt_swc_by_addr.setdefault(gt_row["address"], set()).add(gt_row["SWC_ID"])

    concurrency = max(1, int(options["concurrency"]))
    if concurrency != 1:
        print(
            f"[{model}] strict blocking mode enabled; overriding concurrency {concurrency} -> 1"
        )
        concurrency = 1
    live_progress = bool(options.get("live_progress", False))
    sequential_live = live_progress and concurrency == 1
    parallel_live = live_progress and concurrency > 1
    stream_contract_outputs = bool(options.get("stream_contract_outputs", False))
    keep_raw_payload = bool(options.get("keep_raw_payload", True))
    model_dir = Path(options["model_dir"]) if options.get("model_dir") else None
    resume_mode = bool(options.get("resume_mode", False))

    done_addresses_initial = set(contract_rows_by_addr.keys())
    pending_addresses = [addr for addr in addresses if addr not in done_addresses_initial]
    parallel_board = ParallelProgressBoard(model, pending_addresses) if parallel_live else None

    contract_fieldnames = contract_level_fieldnames()
    rule_fieldnames = build_rule_score_fieldnames(TARGET_SWCS)
    contract_output_path = model_dir / "contract_level.csv" if model_dir else None
    rule_output_path = model_dir / "rule_score_per_contract.csv" if model_dir else None
    effective_max_wait_seconds = int(options["max_wait_seconds"])

    if stream_contract_outputs:
        if contract_output_path and (not resume_mode or not contract_output_path.exists()):
            write_csv(contract_output_path, [], contract_fieldnames)
        if rule_output_path and (not resume_mode or not rule_output_path.exists()):
            write_csv(rule_output_path, [], rule_fieldnames)

    def enrich_and_store_row(row: Dict[str, Any]) -> None:
        swc_set = sorted(gt_swc_by_addr.get(row["address"], set()))
        row["gt_swc_set"] = "|".join(swc_set)
        persist_full_report_for_row(row, model_dir)
        persist_audit_plan_for_row(row, model_dir)
        persist_static_summary_for_row(row, model_dir)
        persist_workflow_debug_for_row(row, model_dir)
        persist_contract_record_for_row(row, model_dir)

        if not keep_raw_payload:
            row.pop("raw", None)

        contract_rows.append(row)
        contract_rows_by_addr[row["address"]] = row

        if stream_contract_outputs and contract_output_path and rule_output_path:
            append_csv_row(contract_output_path, row, contract_fieldnames)
            one_rule_row = compute_rule_score_rows([row], TARGET_SWCS, RULE_MULTI_MIN_SCORE)[0]
            append_csv_row(rule_output_path, one_rule_row, rule_fieldnames)

    def build_progress_callback(addr: str) -> Callable[[Dict[str, Any]], None]:
        short_addr = addr[:10] + "..." if len(addr) > 10 else addr

        def _callback(event: Dict[str, Any]) -> None:
            status = text_compact(event.get("status") or "running")
            percentage = to_float(event.get("percentage"), 0.0)
            step_name = text_compact(event.get("step_name") or "")
            elapsed = to_float(event.get("elapsed_seconds"), 0.0)
            sid = text_compact(event.get("session_id") or "")
            sid_short = sid[:8] if sid else "-"
            bar = render_progress_bar(percentage)
            line = (
                f"[{model}] {short_addr} {bar} {percentage:5.1f}% "
                f"{status:<10} step={step_name or '-'} elapsed={elapsed:5.1f}s sid={sid_short}"
            )
            term_width = max(40, shutil.get_terminal_size(fallback=(120, 24)).columns)
            max_len = max(20, term_width - 1)
            if len(line) > max_len:
                clipped = line[: max_len - 1] + "…"
            else:
                clipped = line
            if sys.stdout.isatty():
                print("\x1b[2K\r" + clipped, end="", flush=True)
            else:
                print("\r" + clipped.ljust(max_len), end="", flush=True)

        return _callback

    def task(addr: str) -> Dict[str, Any]:
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
        if sequential_live:
            progress_callback = build_progress_callback(addr)
        elif parallel_board is not None:
            progress_callback = lambda event, _addr=addr: parallel_board.update(_addr, event)
        return process_one_address(
            address=addr,
            model=model,
            api_base=options["api_base"],
            mainnet_dir=options["mainnet_dir"],
            static_index=static_index,
            static_tool_max_chars=int(options["static_tool_max_chars"]),
            poll_interval=float(options["poll_interval"]),
            max_wait_seconds=effective_max_wait_seconds,
            request_timeout=int(options["request_timeout"]),
            retries=int(options["retry"]),
            keyword_map=keyword_map,
            llm_classifier=llm_classifier,
            enable_llm_fallback=bool(options["enable_llm_fallback"]),
            enable_llm_explanation=bool(options["enable_llm_explanation"]),
            progress_callback=progress_callback,
        )

    print(
        f"[{model}] Processing {len(pending_addresses)} pending / {len(addresses)} total "
        f"(concurrency={concurrency})"
    )
    started_at = time.time()

    fatal_triggered = False
    fatal_reason = ""

    if concurrency == 1:
        for idx, address in enumerate(pending_addresses, start=1):
            try:
                row = task(address)
            except FatalAuditStop as exc:
                fatal_triggered = True
                fatal_reason = str(exc)
                if sequential_live:
                    print("")
                print(f"[{model}] Fatal stop triggered at {address}: {fatal_reason}")
                break
            if sequential_live:
                print("")
            enrich_and_store_row(row)
            if idx % 20 == 0 or idx == len(pending_addresses):
                elapsed = time.time() - started_at
                print(f"[{model}] Completed {idx}/{len(pending_addresses)} pending in {elapsed:.1f}s")
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            future_to_address: Dict[concurrent.futures.Future, str] = {}
            for address in pending_addresses:
                if fatal_triggered:
                    break
                future = executor.submit(task, address)
                future_to_address[future] = address
                if parallel_board is not None:
                    parallel_board.update(
                        address,
                        {
                            "status": "submitted",
                            "percentage": 0.0,
                            "step_name": "Queued",
                            "elapsed_seconds": 0.0,
                        },
                    )

            done_count = 0
            for future in concurrent.futures.as_completed(future_to_address):
                address = future_to_address[future]
                if fatal_triggered:
                    future.cancel()
                    continue
                try:
                    row = future.result()
                except FatalAuditStop as exc:
                    fatal_triggered = True
                    fatal_reason = str(exc)
                    if parallel_board is not None:
                        parallel_board.complete(
                            address,
                            {
                                "status": "failed",
                                "percentage": 0.0,
                                "step_name": "Fatal",
                                "session_id": "",
                                "error": fatal_reason,
                            },
                        )
                    print(f"[{model}] Fatal stop triggered at {address}: {fatal_reason}")
                    # Cancel remaining futures to avoid starting new addresses.
                    for f in future_to_address:
                        if f is not future:
                            f.cancel()
                    break
                except Exception as exc:
                    row = {
                        "address": address,
                        "session_id": "",
                        "audit_status": "worker_failed",
                        "model": model,
                        "pred_swc_list": "",
                        "pred_swc_count": 0,
                        "is_other": 1,
                        "pred_source": "worker_failed",
                        "pred_reason": "Worker exception; no SWC signal.",
                        "rule_scores_json": "{}",
                        "rule_matched_json": "{}",
                        "llm_fallback_json": "{}",
                        "llm_explanation_json": "{}",
                        "full_report_available": 0,
                        "full_report_chars": 0,
                        "full_report_path": "",
                        "rag_used": 0,
                        "rag_enabled": 0,
                        "rag_effective_task_count": 0,
                        "rag_effective_evidence_count": 0,
                        "rag_similarity_threshold": 0.0,
                        "audit_attempts": 0,
                        "empty_report_retries_used": 0,
                        "_full_report_text": "",
                        "finding_number": 0,
                        "execution_time": "",
                        "gt_swc_set": "",
                        "error": str(exc),
                        "raw": {
                            "address": address,
                            "model": model,
                            "error": str(exc),
                        },
                    }
                if fatal_triggered:
                    continue
                if parallel_board is not None:
                    parallel_board.complete(address, row)
                enrich_and_store_row(row)
                done_count += 1
                if parallel_board is not None:
                    if done_count == len(pending_addresses):
                        elapsed = time.time() - started_at
                        print(
                            f"[{model}] Completed {done_count}/{len(pending_addresses)} pending in {elapsed:.1f}s"
                        )
                elif done_count % 20 == 0 or done_count == len(pending_addresses):
                    elapsed = time.time() - started_at
                    print(
                        f"[{model}] Completed {done_count}/{len(pending_addresses)} pending in {elapsed:.1f}s"
                    )

    if fatal_triggered:
        raise FatalAuditStop(fatal_reason or "Fatal stop triggered")

    # Deterministic order.
    contract_rows.sort(key=lambda x: x["address"])
    patch_contract_rows_with_gt_set(contract_rows, gt_rows_model)

    pair_rows = build_pair_rows(gt_rows_model, contract_rows_by_addr, model)
    pair_rows.sort(key=lambda x: (x["SWC_ID"], x["address"]))

    summary_rows = compute_summary_metrics(pair_rows, TARGET_SWCS)
    rule_score_rows = compute_rule_score_rows(contract_rows, TARGET_SWCS, RULE_MULTI_MIN_SCORE)

    failure_count = sum(
        1
        for row in contract_rows
        if text_compact(row.get("audit_status") or "").lower() not in {"", "completed"}
        or bool(text_compact(row.get("error") or ""))
    )
    other_count = sum(int(row.get("is_other", 0)) for row in contract_rows)

    return {
        "model": model,
        "contract_rows": contract_rows,
        "pair_rows": pair_rows,
        "summary_rows": summary_rows,
        "rule_score_rows": rule_score_rows,
        "failure_count": failure_count,
        "other_count": other_count,
        "existing_count": len(done_addresses_initial),
        "processed_count": len(pending_addresses),
    }


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    parser = build_parser(repo_root)
    args = parser.parse_args()

    config_path = Path(args.config).expanduser().resolve() if args.config else None
    config = load_config(config_path)
    config_dir = config_path.parent if config_path else None

    settings: Dict[str, Any] = {
        "api_base": merged_setting(args, config, "api_base", "_default_api_base"),
        "ground_truth_csv": merged_setting(args, config, "ground_truth_csv", "_default_ground_truth_csv"),
        "mainnet_dir": merged_setting(args, config, "mainnet_dir", "_default_mainnet_dir"),
        "vulnerability_json": merged_setting(args, config, "vulnerability_json", "_default_vulnerability_json"),
        "vulnerability_csv": merged_setting(args, config, "vulnerability_csv", "_default_vulnerability_csv"),
        "output_dir": merged_setting(args, config, "output_dir", "_default_output_dir"),
        "run_id": merged_setting(args, config, "run_id", "_default_run_id"),
        "models": merged_setting(args, config, "models", "_default_models"),
        "concurrency": int(merged_setting(args, config, "concurrency", "_default_concurrency")),
        "poll_interval": float(merged_setting(args, config, "poll_interval", "_default_poll_interval")),
        "max_wait_seconds": int(
            merged_setting(args, config, "max_wait_seconds", "_default_max_wait_seconds")
        ),
        "request_timeout": int(
            merged_setting(args, config, "request_timeout", "_default_request_timeout")
        ),
        "retry": int(merged_setting(args, config, "retry", "_default_retry")),
        "static_tool_dir": merged_setting(args, config, "static_tool_dir", "_default_static_tool_dir"),
        "static_tool_max_chars": int(
            merged_setting(args, config, "static_tool_max_chars", "_default_static_tool_max_chars")
        ),
        "enable_llm_fallback": merged_setting(
            args, config, "enable_llm_fallback", "_default_enable_llm_fallback"
        ),
        "enable_llm_explanation": merged_setting(
            args, config, "enable_llm_explanation", "_default_enable_llm_explanation"
        ),
        "llm_timeout": int(merged_setting(args, config, "llm_timeout", "_default_llm_timeout")),
        "llm_confidence_threshold": float(
            merged_setting(
                args,
                config,
                "llm_confidence_threshold",
                "_default_llm_confidence_threshold",
            )
        ),
        "live_progress": bool(merged_setting(args, config, "live_progress", "_default_live_progress")),
        "resume": bool(merged_setting(args, config, "resume", "_default_resume")),
        "verbose": bool(getattr(args, "verbose", False)),
    }

    # Command-specific settings.
    if args.command == "single":
        settings["address"] = normalize_address(
            args.address if args.address is not None else config.get("address", "")
        )
        if not settings["address"]:
            raise SystemExit("single mode requires --address or config: address")
    elif args.command == "batch":
        limit_value = args.limit if args.limit is not None else config.get("limit")
        settings["limit"] = int(limit_value) if limit_value is not None else None

    # Resolve paths.
    for key in [
        "ground_truth_csv",
        "mainnet_dir",
        "vulnerability_json",
        "vulnerability_csv",
        "output_dir",
        "static_tool_dir",
    ]:
        settings[key] = resolve_path(settings.get(key), config_dir) if key != "output_dir" else resolve_path(
            settings.get(key), config_dir
        )

    # Required path checks.
    required_paths = ["ground_truth_csv", "mainnet_dir", "vulnerability_json", "vulnerability_csv"]
    for key in required_paths:
        path = settings.get(key)
        if path is None or not Path(path).exists():
            raise SystemExit(f"Required path missing for {key}: {path}")

    if settings["output_dir"] is None:
        raise SystemExit("output_dir cannot be empty")

    gt_rows_all = load_ground_truth(Path(settings["ground_truth_csv"]))
    if not gt_rows_all:
        raise SystemExit("Ground truth CSV is empty")

    if args.command == "single":
        selected_addresses = [settings["address"]]
        gt_rows_selected = [row for row in gt_rows_all if row["address"] == settings["address"]]
        if not gt_rows_selected:
            print(
                f"Warning: address {settings['address']} not found in ground truth. "
                "Outputs will still include contract-level results."
            )
    else:
        ordered = address_order(gt_rows_all)
        limit = settings.get("limit")
        if limit is not None and limit > 0:
            ordered = ordered[: limit]
        selected_addresses = ordered
        selected_set = set(selected_addresses)
        gt_rows_selected = [row for row in gt_rows_all if row["address"] in selected_set]

    models_arg = parse_models(settings["models"])
    models = resolve_models(
        api_base=str(settings["api_base"]).rstrip("/"),
        models_arg=models_arg,
        request_timeout=int(settings["request_timeout"]),
        retries=int(settings["retry"]),
    )

    keyword_map = build_keyword_map(
        vulnerability_json=Path(settings["vulnerability_json"]),
        vulnerability_csv=Path(settings["vulnerability_csv"]),
        target_swcs=TARGET_SWCS,
    )

    static_index = build_static_tool_index(Path(settings["static_tool_dir"])) if settings.get("static_tool_dir") else {}

    llm_classifier = LlmFallbackClassifier(
        api_base=str(settings["api_base"]).rstrip("/"),
        timeout=int(settings["llm_timeout"]),
        confidence_threshold=float(settings["llm_confidence_threshold"]),
        request_timeout=int(settings["request_timeout"]),
        retries=int(settings["retry"]),
    )

    output_dir_path = Path(settings["output_dir"])
    if settings["resume"]:
        run_id, run_root = resolve_resume_run_root(output_dir_path, str(settings.get("run_id", "") or ""))
        run_root = ensure_dir(run_root)
    else:
        run_id = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        run_root = ensure_dir(output_dir_path / run_id)

    run_meta: Dict[str, Any] = {
        "run_id": run_id,
        "started_at": now_iso(),
        "mode": args.command,
        "resume": bool(settings["resume"]),
        "selected_addresses": len(selected_addresses),
        "selected_gt_rows": len(gt_rows_selected),
        "models": models,
        "options": {
            "api_base": str(settings["api_base"]).rstrip("/"),
            "run_id": str(run_id),
            "concurrency": int(settings["concurrency"]),
            "poll_interval": float(settings["poll_interval"]),
            "max_wait_seconds": int(settings["max_wait_seconds"]),
            "request_timeout": int(settings["request_timeout"]),
            "retry": int(settings["retry"]),
            "enable_llm_fallback": bool(settings["enable_llm_fallback"]),
            "enable_llm_explanation": bool(settings["enable_llm_explanation"]),
            "llm_timeout": int(settings["llm_timeout"]),
            "llm_confidence_threshold": float(settings["llm_confidence_threshold"]),
            "live_progress": bool(settings["live_progress"]),
            "static_tool_dir": str(settings["static_tool_dir"] or ""),
            "static_tool_index_size": len(static_index),
            "ground_truth_csv": str(settings["ground_truth_csv"]),
            "mainnet_dir": str(settings["mainnet_dir"]),
        },
        "per_model": {},
    }

    api_base = str(settings["api_base"]).rstrip("/")

    fatal_stop = False
    for model in models:
        model_safe = sanitize_model_name(model)
        model_dir = ensure_dir(run_root / model_safe)
        contract_csv_path = model_dir / "contract_level.csv"
        existing_contract_rows = (
            load_existing_contract_rows(contract_csv_path) if settings["resume"] else []
        )

        try:
            model_result = run_for_model(
                model=model,
                addresses=selected_addresses,
                gt_rows_model=gt_rows_selected,
                options={
                    **settings,
                    "api_base": api_base,
                    "mainnet_dir": Path(settings["mainnet_dir"]),
                    "model_dir": model_dir,
                    "stream_contract_outputs": True,
                    "keep_raw_payload": args.command == "single",
                    "resume_mode": settings["resume"],
                    "existing_contract_rows": existing_contract_rows,
                },
                keyword_map=keyword_map,
                llm_classifier=llm_classifier,
                static_index=static_index,
            )
        except FatalAuditStop as exc:
            print(f"[{model}] Fatal stop for model: {exc}")
            fatal_stop = True
            break

        contract_rows = model_result["contract_rows"]
        pair_rows = model_result["pair_rows"]
        summary_rows = model_result["summary_rows"]
        rule_score_rows = model_result["rule_score_rows"]

        write_csv(
            model_dir / "contract_level.csv",
            contract_rows,
            fieldnames=contract_level_fieldnames(),
        )

        write_csv(
            model_dir / "pair_level.csv",
            pair_rows,
            fieldnames=[
                "address",
                "SWC_ID",
                "gt_label",
                "conflict_flag",
                "pred_swc_list",
                "pred_label",
                "is_other",
                "pred_source",
                "session_id",
                "model",
                "full_report_available",
                "full_report_chars",
                "full_report_path",
            ],
        )

        write_csv(
            model_dir / "summary_metrics.csv",
            summary_rows,
            fieldnames=[
                "scope",
                "swc",
                "tp",
                "fp",
                "tn",
                "fn",
                "precision",
                "recall",
                "f1",
                "accuracy",
                "other_rate",
            ],
        )

        write_csv(
            model_dir / "rule_score_per_contract.csv",
            rule_score_rows,
            fieldnames=build_rule_score_fieldnames(TARGET_SWCS),
        )

        if args.command == "single" and contract_rows:
            (model_dir / "single_contract_result.json").write_text(
                json.dumps(contract_rows[0].get("raw", {}), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        run_meta["per_model"][model] = {
            "contract_rows": len(contract_rows),
            "pair_rows": len(pair_rows),
            "summary_rows": len(summary_rows),
            "rule_score_rows": len(rule_score_rows),
            "existing_count": int(model_result.get("existing_count", 0)),
            "processed_count": int(model_result.get("processed_count", 0)),
            "failure_count": int(model_result["failure_count"]),
            "other_count": int(model_result["other_count"]),
            "output_dir": str(model_dir),
        }

    run_meta["fatal_stop"] = fatal_stop
    run_meta["finished_at"] = now_iso()
    (run_root / "run_meta.json").write_text(json.dumps(run_meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Run finished: {run_root}")
    for model, stats in run_meta["per_model"].items():
        print(
            f"  - {model}: processed={stats['processed_count']}, resumed_existing={stats['existing_count']}, "
            f"contract_rows={stats['contract_rows']}, "
            f"pair_rows={stats['pair_rows']}, failures={stats['failure_count']}, "
            f"other={stats['other_count']}"
        )


if __name__ == "__main__":
    main()
