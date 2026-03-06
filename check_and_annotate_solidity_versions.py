#!/usr/bin/env python3
"""
Scan pragma solidity versions for contracts and annotate ground truth CSV rows.

Default behavior:
- Read addresses from RQ2 ground truth CSV
- Analyze `<mainnet_dir>/<address>.sol`
- Write a new CSV with appended version columns (no in-place overwrite)
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple


PRAGMA_RE = re.compile(r"(?im)^\s*pragma\s+solidity\s+([^;]+);")
VERSION_RE = re.compile(r"(?<!\d)(\d+)\.(\d+)(?:\.(\d+))?(?!\d)")


@dataclass
class ContractVersionInfo:
    source_exists: int
    read_ok: int
    pragma_count: int
    pragma_unique_count: int
    pragma_unique_exprs: str
    version_bucket_set: str
    version_bucket: str
    pragma_uniform: int
    version_bucket_uniform: int
    scan_error: str


def normalize_expr(expr: str) -> str:
    return " ".join((expr or "").strip().split())


def version_bucket_from_expr(expr: str) -> List[str]:
    buckets = set()
    for match in VERSION_RE.finditer(expr):
        major = int(match.group(1))
        minor = int(match.group(2))
        buckets.add((major, minor))
    ordered = sorted(buckets)
    return [f"{major}.{minor}.0" for major, minor in ordered]


def analyze_contract(path: Path) -> ContractVersionInfo:
    if not path.exists():
        return ContractVersionInfo(
            source_exists=0,
            read_ok=0,
            pragma_count=0,
            pragma_unique_count=0,
            pragma_unique_exprs="",
            version_bucket_set="",
            version_bucket="",
            pragma_uniform=0,
            version_bucket_uniform=0,
            scan_error="source_not_found",
        )

    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:  # pragma: no cover
        return ContractVersionInfo(
            source_exists=1,
            read_ok=0,
            pragma_count=0,
            pragma_unique_count=0,
            pragma_unique_exprs="",
            version_bucket_set="",
            version_bucket="",
            pragma_uniform=0,
            version_bucket_uniform=0,
            scan_error=f"read_error:{exc}",
        )

    expr_list = [normalize_expr(m.group(1)) for m in PRAGMA_RE.finditer(text)]
    uniq_exprs = sorted(set(expr_list))

    bucket_set = sorted({bucket for expr in uniq_exprs for bucket in version_bucket_from_expr(expr)})
    bucket_text = "|".join(bucket_set)

    pragma_uniform = 1 if len(uniq_exprs) == 1 else 0
    bucket_uniform = 1 if len(bucket_set) == 1 else 0
    bucket_primary = bucket_set[0] if len(bucket_set) == 1 else ("MULTI" if bucket_set else "")

    return ContractVersionInfo(
        source_exists=1,
        read_ok=1,
        pragma_count=len(expr_list),
        pragma_unique_count=len(uniq_exprs),
        pragma_unique_exprs=" | ".join(uniq_exprs),
        version_bucket_set=bucket_text,
        version_bucket=bucket_primary,
        pragma_uniform=pragma_uniform,
        version_bucket_uniform=bucket_uniform,
        scan_error="",
    )


def read_csv_rows(path: Path) -> Tuple[List[Dict[str, str]], List[str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])
    return rows, fieldnames


def write_csv_rows(path: Path, rows: Sequence[Dict[str, object]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    default_gt = repo_root / "EmpiricalSCST" / "_RQ2" / "manual" / "ground_truth" / "RQ2_ground_truth.csv"
    default_mainnet = repo_root / "EmpiricalSCST" / "mainnet"
    default_output = default_gt.with_name("RQ2_ground_truth_with_solidity_versions.csv")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ground-truth-csv", default=str(default_gt), help="Path to ground truth CSV")
    parser.add_argument("--mainnet-dir", default=str(default_mainnet), help="Path to mainnet source directory")
    parser.add_argument("--output-csv", default=str(default_output), help="Output CSV path")
    parser.add_argument("--in-place", action="store_true", help="Overwrite input CSV (output_csv ignored)")
    parser.add_argument("--workers", type=int, default=8, help="Thread workers for file scan")
    parser.add_argument("--limit-addresses", type=int, default=0, help="Only scan first N unique addresses (debug)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    gt_csv = Path(args.ground_truth_csv).expanduser().resolve()
    mainnet_dir = Path(args.mainnet_dir).expanduser().resolve()
    output_csv = gt_csv if args.in_place else Path(args.output_csv).expanduser().resolve()

    if not gt_csv.exists():
        raise SystemExit(f"ground truth csv not found: {gt_csv}")
    if not mainnet_dir.exists():
        raise SystemExit(f"mainnet dir not found: {mainnet_dir}")

    rows, base_fields = read_csv_rows(gt_csv)
    if "address" not in base_fields:
        raise SystemExit("input csv must contain `address` column")

    addresses: List[str] = []
    seen = set()
    for row in rows:
        addr = (row.get("address") or "").strip().lower()
        if not addr or addr in seen:
            continue
        seen.add(addr)
        addresses.append(addr)

    if args.limit_addresses and args.limit_addresses > 0:
        addresses = addresses[: args.limit_addresses]

    workers = max(1, int(args.workers))
    version_map: Dict[str, ContractVersionInfo] = {}

    with ThreadPoolExecutor(max_workers=workers) as executor:
        fut_map = {executor.submit(analyze_contract, mainnet_dir / f"{addr}.sol"): addr for addr in addresses}
        done = 0
        total = len(fut_map)
        for fut in as_completed(fut_map):
            addr = fut_map[fut]
            try:
                version_map[addr] = fut.result()
            except Exception as exc:  # pragma: no cover
                version_map[addr] = ContractVersionInfo(
                    source_exists=1,
                    read_ok=0,
                    pragma_count=0,
                    pragma_unique_count=0,
                    pragma_unique_exprs="",
                    version_bucket_set="",
                    version_bucket="",
                    pragma_uniform=0,
                    version_bucket_uniform=0,
                    scan_error=f"worker_error:{exc}",
                )
            done += 1
            if done % 500 == 0 or done == total:
                print(f"scanned {done}/{total} addresses")

    added_fields = [
        "solidity_source_exists",
        "solidity_read_ok",
        "solidity_pragma_count",
        "solidity_pragma_unique_count",
        "solidity_pragma_uniform",
        "solidity_version_bucket_uniform",
        "solidity_version_bucket",
        "solidity_version_bucket_set",
        "solidity_pragma_unique_exprs",
        "solidity_scan_error",
    ]

    output_rows: List[Dict[str, object]] = []
    for row in rows:
        addr = (row.get("address") or "").strip().lower()
        info = version_map.get(
            addr,
            ContractVersionInfo(
                source_exists=0,
                read_ok=0,
                pragma_count=0,
                pragma_unique_count=0,
                pragma_unique_exprs="",
                version_bucket_set="",
                version_bucket="",
                pragma_uniform=0,
                version_bucket_uniform=0,
                scan_error="address_not_scanned",
            ),
        )
        merged = dict(row)
        merged["solidity_source_exists"] = info.source_exists
        merged["solidity_read_ok"] = info.read_ok
        merged["solidity_pragma_count"] = info.pragma_count
        merged["solidity_pragma_unique_count"] = info.pragma_unique_count
        merged["solidity_pragma_uniform"] = info.pragma_uniform
        merged["solidity_version_bucket_uniform"] = info.version_bucket_uniform
        merged["solidity_version_bucket"] = info.version_bucket
        merged["solidity_version_bucket_set"] = info.version_bucket_set
        merged["solidity_pragma_unique_exprs"] = info.pragma_unique_exprs
        merged["solidity_scan_error"] = info.scan_error
        output_rows.append(merged)

    output_fields = list(base_fields) + [f for f in added_fields if f not in base_fields]
    write_csv_rows(output_csv, output_rows, output_fields)

    summary = {
        "ground_truth_csv": str(gt_csv),
        "mainnet_dir": str(mainnet_dir),
        "output_csv": str(output_csv),
        "input_rows": len(rows),
        "unique_addresses_scanned": len(addresses),
        "source_exists": sum(v.source_exists for v in version_map.values()),
        "pragma_uniform": sum(v.pragma_uniform for v in version_map.values()),
        "pragma_multi_expr": sum(1 for v in version_map.values() if v.pragma_unique_count > 1),
        "version_bucket_uniform": sum(v.version_bucket_uniform for v in version_map.values()),
        "version_bucket_multi": sum(1 for v in version_map.values() if v.version_bucket_uniform == 0 and v.version_bucket_set),
        "no_pragma_found": sum(1 for v in version_map.values() if v.pragma_count == 0),
    }
    summary_path = output_csv.with_suffix(output_csv.suffix + ".summary.json")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"written: {output_csv}")
    print(f"written: {summary_path}")


if __name__ == "__main__":
    main()

