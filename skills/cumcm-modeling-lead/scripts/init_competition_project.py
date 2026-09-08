#!/usr/bin/env python3
"""建立默认轻量、可选严格记录的国赛项目。"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path


LIGHT_DIRECTORIES = (
    "题面与附件",
    "数据",
    "建模与代码",
    "结果",
    "论文",
)

STRICT_DIRECTORIES = (
    "结果/运行记录",
    "内部记录",
    "registries",
)

SHARED_NOTE = """# 全队建模记录

## 现在做到

- 现在做到：
- 这一步要解决：
- 为什么现在做：
- 我们已有：
- 这一步产出：
- 怎样算完成：
- 下一步：

## 全题依赖

## 题目事实、数据发现与未知项

## 逐问建模

### 问题一

- 现实问题：
- 输入：
- 输出：
- 思路：
- 假设与约束：
- 验证：
- 结果与边界：

## 关键决定

| 时间 | 决定 | 为什么 | 谁已理解 | 是否需要复查 |
|---|---|---|---|---|

## 全队复述检查

- 思路负责人：
- 计算负责人：
- 论文负责人：
"""

AI_NOTE = """# AI使用记录

| 时间 | 用途 | AI给出的内容 | 全队怎样修改或取舍 | 怎样人工核验 | 对应文件 |
|---|---|---|---|---|---|
"""

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
    parser.add_argument("--competition", default="CUMCM", help="竞赛名称")
    parser.add_argument("--problem", default="", help="题号")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="建立正式运行、结果、图表和论文结论的详细记录",
    )
    args = parser.parse_args()

    root = args.project.resolve()
    root.mkdir(parents=True, exist_ok=True)

    for relative in LIGHT_DIRECTORIES:
        (root / relative).mkdir(parents=True, exist_ok=True)

    write_if_missing(root / "全队建模记录.md", SHARED_NOTE)
    write_if_missing(root / "AI使用记录.md", AI_NOTE)

    if args.strict:
        for relative in STRICT_DIRECTORIES:
            (root / relative).mkdir(parents=True, exist_ok=True)
        record_dir = root / "registries"
        for name, header in REGISTRIES.items():
            write_csv_if_missing(record_dir / name, header)

        state_path = record_dir / "项目状态.json"
        if not state_path.exists():
            state = {
                "schema_version": "2.0",
                "competition": args.competition,
                "problem": args.problem,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "current_step": "读题",
                "model_confirmed": False,
                "results_frozen": False,
                "submission_checked": False,
                "decisions": [],
            }
            state_path.write_text(
                json.dumps(state, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

    mode = "严格记录模式" if args.strict else "默认轻量模式"
    print(f"{root}\n已建立：{mode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
