from __future__ import annotations

import json
from typing import Any, Dict, List, Sequence


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _text_compact(value: Any) -> str:
    return " ".join(str(value or "").split()).strip()


def _json_compact(value: Any) -> str:
    try:
        return json.dumps(value if value is not None else {}, ensure_ascii=False, sort_keys=True)
    except Exception:
        return json.dumps(str(value), ensure_ascii=False)


def swc_to_col_suffix(swc: str) -> str:
    return swc.lower().replace("-", "_")


def build_rule_score_fieldnames(target_swcs: Sequence[str]) -> List[str]:
    fields = [
        "address",
        "session_id",
        "audit_status",
        "model",
        "pred_swc_list",
        "pred_source",
        "error",
    ]
    for swc in target_swcs:
        suffix = swc_to_col_suffix(swc)
        fields.append(f"score_{suffix}")
        fields.append(f"hit_{suffix}")
        fields.append(f"matched_count_{suffix}")
    fields.extend(["rule_scores_json", "rule_matched_json"])
    return fields


def compute_rule_score_rows(
    contract_rows: Sequence[Dict[str, Any]],
    target_swcs: Sequence[str],
    hit_score_threshold: float,
) -> List[Dict[str, Any]]:
    output: List[Dict[str, Any]] = []

    def parse_json_obj(raw: Any) -> Dict[str, Any]:
        if isinstance(raw, dict):
            return raw
        text = _text_compact(raw)
        if not text:
            return {}
        try:
            parsed = json.loads(text)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}

    for row in contract_rows:
        rule_scores = parse_json_obj(row.get("rule_scores_json", "{}"))
        rule_matched = parse_json_obj(row.get("rule_matched_json", "{}"))

        out_row: Dict[str, Any] = {
            "address": row.get("address", ""),
            "session_id": row.get("session_id", ""),
            "audit_status": row.get("audit_status", ""),
            "model": row.get("model", ""),
            "pred_swc_list": row.get("pred_swc_list", ""),
            "pred_source": row.get("pred_source", ""),
            "error": row.get("error", ""),
        }

        for swc in target_swcs:
            suffix = swc_to_col_suffix(swc)
            score = round(_to_float(rule_scores.get(swc), 0.0), 6)
            matched_items = rule_matched.get(swc)
            matched_count = len(matched_items) if isinstance(matched_items, list) else 0
            out_row[f"score_{suffix}"] = score
            out_row[f"hit_{suffix}"] = 1 if score >= hit_score_threshold else 0
            out_row[f"matched_count_{suffix}"] = matched_count

        out_row["rule_scores_json"] = _json_compact(rule_scores)
        out_row["rule_matched_json"] = _json_compact(rule_matched)
        output.append(out_row)

    return output
