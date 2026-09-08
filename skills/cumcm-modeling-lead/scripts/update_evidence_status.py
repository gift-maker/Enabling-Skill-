#!/usr/bin/env python3
"""在人工完成对应检查后，受控更新一条证据的状态字段。"""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path


REGISTRIES = {
    "run": ("run_ledger.csv", "run_id"),
    "result": ("result_registry.csv", "result_id"),
    "claim": ("claim_ledger.csv", "claim_id"),
    "figure": ("figure_evidence.csv", "figure_id"),
    "issue": ("issue_ledger.csv", "issue_id"),
}

ALLOWED = {
    "status": {"planned", "exploratory", "candidate", "validated", "paper_ready", "rejected", "superseded", "open", "closed", "accepted"},
    "validation_status": {"pending", "passed", "failed", "validated", "paper_ready"},
    "render_check_status": {"pending", "passed", "failed"},
    "human_visual_check": {"pending", "passed", "failed"},
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--registry", choices=sorted(REGISTRIES), required=True)
    parser.add_argument("--id", required=True)
    parser.add_argument("--field", choices=sorted(ALLOWED), required=True)
    parser.add_argument("--value", required=True)
    parser.add_argument("--evidence", required=True, help="人工检查记录或报告路径/说明")
    args = parser.parse_args()

    if args.value not in ALLOWED[args.field]:
        parser.error(f"{args.field} 不允许值 {args.value}")
    filename, id_field = REGISTRIES[args.registry]
    path = args.root.resolve() / "registries" / filename
    if not path.is_file():
        parser.error(f"登记表不存在：{path}")

    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fieldnames = reader.fieldnames or []
        rows = list(reader)
    if args.field not in fieldnames:
        parser.error(f"{filename} 没有字段 {args.field}")
    matched = [row for row in rows if row.get(id_field) == args.id]
    if len(matched) != 1:
        parser.error(f"要求唯一命中 {args.id}，实际 {len(matched)} 条")
    matched[0][args.field] = args.value

    audit_note = path.with_name("status_changes.csv")
    audit_exists = audit_note.exists()
    with audit_note.open("a", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        if not audit_exists:
            writer.writerow(["registry", "id", "field", "value", "evidence"])
        writer.writerow([args.registry, args.id, args.field, args.value, args.evidence])

    temporary = path.with_suffix(f".{os.getpid()}.tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)
    print(f"{args.registry}:{args.id} {args.field}={args.value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
