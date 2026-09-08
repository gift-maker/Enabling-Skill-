#!/usr/bin/env python3
"""建立 CUMCM 一体化项目骨架和空白证据登记表。"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path


DIRECTORIES = (
    "0_题面与附件",
    "1_数据/raw",
    "1_数据/processed",
    "2_建模",
    "3_代码",
    "4_结果/runs",
    "5_图表",
    "6_论文",
    "7_提交",
    "registries",
)

TEXT_FILES = {
    "建模总控.md": "# 建模总控\n\n## 全题目标\n\n## 子问依赖\n\n## 系统边界\n\n## 关键风险\n\n## 时间预算\n",
    "模型合同.md": "# 模型合同\n\n状态：待建模手确认\n\n## 问题一\n\n### 输入与输出\n\n### 假设、变量与参数\n\n### 方程、目标与约束\n\n### 候选、基线与主方案\n\n### 验证与失败条件\n",
    "术语与符号表.md": "# 术语与符号表\n\n| 符号 | 含义 | 类型 | 单位 | 范围 | 来源 |\n|---|---|---|---|---|---|\n",
    "ai_usage_log.md": "# AI 使用记录\n\n| 时间 | 阶段 | 用途 | 主要输入 | 采纳/修改/弃用 | 人工核验 | 对应文件 |\n|---|---|---|---|---|---|---|\n",
}

REGISTRIES = {
    "run_ledger.csv": [
        "run_id", "timestamp", "question", "purpose", "status", "command",
        "inputs", "code", "parameters", "seed", "outputs", "return_code",
        "stdout", "stderr", "validation_status",
    ],
    "result_registry.csv": [
        "result_id", "question", "name", "value", "unit", "denominator",
        "scenario", "run_id", "source_file", "validation_method",
        "validation_status", "boundary", "status",
    ],
    "claim_ledger.csv": [
        "claim_id", "question", "claim", "result_ids", "figure_ids",
        "formula_or_source", "unit", "scenario", "boundary", "paper_location",
        "validation_status", "status",
    ],
    "figure_evidence.csv": [
        "figure_id", "claim_id", "file", "source_data", "source_script",
        "unit", "scenario", "caption", "post_figure_conclusion", "risk_note",
        "render_check_status", "human_visual_check", "validation_status", "status",
    ],
    "issue_ledger.csv": [
        "issue_id", "severity", "stage", "artifact", "location", "issue",
        "impact", "minimum_fix", "owner", "status",
    ],
}


def write_if_missing(path: Path, content: str) -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def write_csv_if_missing(path: Path, header: list[str]) -> None:
    if path.exists():
        return
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        csv.writer(stream).writerow(header)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="题目项目目录")
    parser.add_argument("--competition", default="CUMCM")
    parser.add_argument("--problem", default="")
    args = parser.parse_args()

    root = args.project.resolve()
    root.mkdir(parents=True, exist_ok=True)
    for relative in DIRECTORIES:
        (root / relative).mkdir(parents=True, exist_ok=True)
    for relative, content in TEXT_FILES.items():
        write_if_missing(root / relative, content)
    for name, header in REGISTRIES.items():
        write_csv_if_missing(root / "registries" / name, header)

    data_contract_path = root / "1_数据" / "data_contract.json"
    if not data_contract_path.exists():
        data_contract = {
            "schema_version": "1.0",
            "status": "draft",
            "source_files": [],
            "tables": [],
            "checks": {
                "columns": [],
                "types": [],
                "units": [],
                "missing": [],
                "ranges": [],
                "uniqueness": [],
                "time_order": [],
                "group_or_spatial_structure": [],
                "leakage_risk": [],
            },
            "unknowns": [],
            "owner": "编程手",
            "modeling_lead_status": "pending",
        }
        data_contract_path.write_text(
            json.dumps(data_contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    state_path = root / "project_state.json"
    if not state_path.exists():
        state = {
            "schema_version": "1.0",
            "competition": args.competition,
            "problem": args.problem,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "current_stage": "S0",
            "modeling_gate": "pending",
            "evidence_gate": "pending",
            "submission_gate": "pending",
            "decisions": [],
        }
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
