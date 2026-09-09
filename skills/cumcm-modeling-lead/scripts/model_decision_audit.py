#!/usr/bin/env python3
"""审计模型推荐与建模手冻结状态，防止自动排行被当成最终模型。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


VALID_STATUS = {
    "构想",
    "候选",
    "已跑通",
    "暂定推荐",
    "待建模手裁决",
    "已冻结",
    "已解冻",
    "已淘汰",
}


def audit(state: dict, require_frozen: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    notes: list[str] = []

    status = state.get("model_status", "构想")
    decision = state.get("modeler_decision", "待确认")
    recommended = state.get("recommended_model")
    frozen = state.get("frozen_model")
    confirmed = bool(state.get("model_confirmed", False))

    if status not in VALID_STATUS:
        errors.append(f"未知模型状态：{status}")

    if recommended and not frozen:
        notes.append(f"AI当前推荐：{recommended}；它仍不是冻结模型")

    freeze_signals = (status == "已冻结", decision == "通过", confirmed, bool(frozen))
    if any(freeze_signals) and not all(freeze_signals):
        errors.append(
            "冻结字段不一致：已冻结、建模手裁决通过、model_confirmed=true、"
            "frozen_model非空必须同时成立"
        )

    if require_frozen and not all(freeze_signals):
        errors.append("当前模型尚未通过建模手冻结，不能进入正式预测、终稿图或论文")

    if all(freeze_signals):
        notes.append(f"建模手已冻结：{frozen}")
    else:
        notes.append(f"当前状态：{status}；建模手裁决：{decision}")

    return errors, notes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", type=Path, help="registries/项目状态.json")
    parser.add_argument(
        "--require-frozen",
        action="store_true",
        help="用于正式预测、终稿图或论文前的冻结门检查",
    )
    args = parser.parse_args()

    state = json.loads(args.state.read_text(encoding="utf-8-sig"))
    errors, notes = audit(state, args.require_frozen)
    result = {
        "通过": not errors,
        "错误": errors,
        "说明": notes,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
