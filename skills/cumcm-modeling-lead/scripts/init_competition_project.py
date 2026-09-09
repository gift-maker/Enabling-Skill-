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

- 现在做到：项目目录已初始化，尚未读取题面
- 这一步要解决：完整读取题面和附件，确认每问交付物
- 为什么现在做：题意和数据结构是设计模型的依据
- 我们已有：竞赛名称、题号和项目目录；题面事实待读取
- 这一步产出：题目清单、全题依赖和第一版数据结构
- 怎样算完成：全队能复述每问输入、输出、约束和依赖
- 下一步：读取题面与附件并用真实内容更新本说明卡

## 全题依赖

尚未读取题面，当前未知；读题后必须填写，不能保留本句作为最终内容。

## 题目事实、数据发现与未知项

当前仅确认项目已经初始化。题目事实、数据发现和未知项待读题与数据体检后填写。

## 逐问建模

尚未确认题目数量。读题后为每一问填写现实问题、输入、输出、结构、完整候选方案、假设约束、验证和边界。

## 模型决策中心

- 正在决定：待读题后确定
- 问题结构：未知，需根据题面和附件识别
- 完整候选方案：尚未生成
- 统一比较口径：尚未确定
- AI建议：尚未形成
- 建模手裁决：待确认
- 模型状态：构想

## 关键决定

| 时间 | 决定 | 为什么 | 谁已理解 | 是否需要复查 |
|---|---|---|---|---|
| 项目初始化时 | 尚无模型决定 | 需要先读题和检查数据 | 待全队复述 | 是 |

## 全队复述检查

- 思路负责人：待读题后填写复述结论
- 计算负责人：待读题后填写数据理解
- 论文负责人：待读题后填写交付物理解
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
                "schema_version": "3.0",
                "competition": args.competition,
                "problem": args.problem,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "current_step": "读题",
                "model_status": "构想",
                "modeler_decision": "待确认",
                "recommended_model": None,
                "frozen_model": None,
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
