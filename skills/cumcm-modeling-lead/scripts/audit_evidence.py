#!/usr/bin/env python3
"""审计 CUMCM 项目的 Run、Result、Figure 与 Claim 证据关系。"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def split_ids(value: str) -> set[str]:
    return {item.strip() for item in value.replace(";", ",").split(",") if item.strip()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-final", action="store_true", help="终稿门：要求存在 paper_ready 的结果和结论")
    args = parser.parse_args()
    root = args.project.resolve()
    registry = root / "registries"
    problems: list[dict[str, str]] = []

    try:
        runs = read_rows(registry / "run_ledger.csv")
        results = read_rows(registry / "result_registry.csv")
        claims = read_rows(registry / "claim_ledger.csv")
        figures = read_rows(registry / "figure_evidence.csv")
        issues = read_rows(registry / "issue_ledger.csv")
    except FileNotFoundError as exc:
        print(f"P0 missing_registry {exc}")
        return 2

    run_by_id = {row.get("run_id", ""): row for row in runs if row.get("run_id")}
    result_by_id = {row.get("result_id", ""): row for row in results if row.get("result_id")}
    figure_by_id = {row.get("figure_id", ""): row for row in figures if row.get("figure_id")}
    run_ids = set(run_by_id)
    result_ids = set(result_by_id)
    figure_ids = set(figure_by_id)

    if args.require_final:
        if not runs:
            problems.append({"severity": "P1", "item": "project", "id": "final", "problem": "no recorded run"})
        if not any(row.get("status") == "paper_ready" for row in results):
            problems.append({"severity": "P1", "item": "project", "id": "final", "problem": "no paper_ready result"})
        if not any(row.get("status") == "paper_ready" for row in claims):
            problems.append({"severity": "P1", "item": "project", "id": "final", "problem": "no paper_ready claim"})

    for row in results:
        result_id = row.get("result_id") or "<missing>"
        if not row.get("result_id"):
            problems.append({"severity": "P1", "item": "result", "id": result_id, "problem": "missing result_id"})
        if row.get("run_id") and row["run_id"] not in run_ids:
            problems.append({"severity": "P1", "item": "result", "id": result_id, "problem": f"unknown run_id {row['run_id']}"})
        if row.get("status") == "paper_ready":
            run_id = row.get("run_id", "")
            if not run_id:
                problems.append({"severity": "P1", "item": "result", "id": result_id, "problem": "paper_ready missing run_id"})
            elif run_id in run_by_id:
                run = run_by_id[run_id]
                if run.get("return_code") != "0":
                    problems.append({"severity": "P1", "item": "result", "id": result_id, "problem": f"run {run_id} did not exit successfully"})
                if run.get("validation_status") not in {"passed", "validated", "paper_ready"}:
                    problems.append({"severity": "P1", "item": "result", "id": result_id, "problem": f"run {run_id} is not independently validated"})
            for field in ("value", "unit", "source_file", "validation_method", "boundary"):
                if not row.get(field):
                    problems.append({"severity": "P1", "item": "result", "id": result_id, "problem": f"paper_ready missing {field}"})
            source_file = row.get("source_file", "")
            if source_file:
                source_path = Path(source_file)
                if not (source_path if source_path.is_absolute() else root / source_path).exists():
                    problems.append({"severity": "P1", "item": "result", "id": result_id, "problem": f"missing source_file {source_file}"})

    for row in figures:
        figure_id = row.get("figure_id") or "<missing>"
        file_value = row.get("file", "")
        figure_path = Path(file_value)
        if file_value and not (figure_path if figure_path.is_absolute() else root / figure_path).exists():
            problems.append({"severity": "P1", "item": "figure", "id": figure_id, "problem": f"missing file {file_value}"})
        if row.get("status") == "paper_ready":
            for field in ("claim_id", "source_data", "source_script", "caption", "post_figure_conclusion", "risk_note"):
                if not row.get(field):
                    problems.append({"severity": "P1", "item": "figure", "id": figure_id, "problem": f"paper_ready missing {field}"})
            if row.get("render_check_status") != "passed" and row.get("human_visual_check") != "passed":
                problems.append({"severity": "P1", "item": "figure", "id": figure_id, "problem": "paper_ready without visual check"})

    for row in claims:
        claim_id = row.get("claim_id") or "<missing>"
        linked_results = split_ids(row.get("result_ids", ""))
        linked_figures = split_ids(row.get("figure_ids", ""))
        for result_id in sorted(linked_results - result_ids):
            problems.append({"severity": "P1", "item": "claim", "id": claim_id, "problem": f"unknown result_id {result_id}"})
        for figure_id in sorted(linked_figures - figure_ids):
            problems.append({"severity": "P1", "item": "claim", "id": claim_id, "problem": f"unknown figure_id {figure_id}"})
        if row.get("status") == "paper_ready":
            if not (linked_results or linked_figures or row.get("formula_or_source")):
                problems.append({"severity": "P0", "item": "claim", "id": claim_id, "problem": "paper_ready without evidence"})
            for field in ("claim", "boundary", "paper_location"):
                if not row.get(field):
                    problems.append({"severity": "P1", "item": "claim", "id": claim_id, "problem": f"paper_ready missing {field}"})
            for result_id in sorted(linked_results & result_ids):
                if result_by_id[result_id].get("status") != "paper_ready":
                    problems.append({"severity": "P1", "item": "claim", "id": claim_id, "problem": f"result {result_id} is not paper_ready"})
            for figure_id in sorted(linked_figures & figure_ids):
                if figure_by_id[figure_id].get("status") != "paper_ready":
                    problems.append({"severity": "P1", "item": "claim", "id": claim_id, "problem": f"figure {figure_id} is not paper_ready"})

    for row in issues:
        if row.get("severity") in {"P0", "P1"} and row.get("status") not in {"closed", "accepted"}:
            problems.append({"severity": row["severity"], "item": "issue", "id": row.get("issue_id", "<missing>"), "problem": "open blocking issue"})

    report = {
        "project": str(root),
        "counts": {"runs": len(runs), "results": len(results), "figures": len(figures), "claims": len(claims)},
        "problems": problems,
        "passed": not any(item["severity"] in {"P0", "P1"} for item in problems),
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"runs={len(runs)} results={len(results)} figures={len(figures)} claims={len(claims)}")
        for item in problems:
            print(f"{item['severity']} {item['item']} {item['id']}: {item['problem']}")
        print("PASS" if report["passed"] else "BLOCKED")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
