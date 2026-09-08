"""AI 使用报告与 LaTeX 论文的一致性审计。

用法:
    python ai_report_audit.py <PROJECT_ROOT> \
      --report <PROJECT_ROOT>/AI使用报告-LaTeX/main.tex \
      --paper <PROJECT_ROOT>/完整论文-LaTeX/main.tex

退出码: 0 = 无 FAIL（WARN 仍需人工确认），1 = 存在 FAIL。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REPORT_HEADINGS = [
    "AI 工具使用声明",
    "所用 AI 工具清单",
    "使用概述",
    "分环节使用记录",
    "提示方式",
    "人工贡献",
]


def norm(text: str) -> str:
    return re.sub(r"\s+", "", text or "")


def read_tex(path: Path, seen: set[Path] | None = None) -> str:
    """递归读取主 tex 和 input/include 文件，避免循环包含。"""
    if seen is None:
        seen = set()
    path = path.resolve()
    if path in seen or not path.is_file():
        return ""
    seen.add(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    chunks = [text]
    for match in re.finditer(r"\\(?:input|include)\{([^}]+)\}", text):
        child = Path(match.group(1))
        if child.suffix.lower() != ".tex":
            child = child.with_suffix(".tex")
        chunks.append(read_tex(path.parent / child, seen))
    return "\n".join(chunks)


def count_log_usage(log_path: Path) -> tuple[int, list[str]]:
    """统计留痕表中的实质使用行。"""
    if not log_path.exists():
        return 0, []
    used: list[str] = []
    for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 3 or not re.match(r"^(S\d+|Q\d+)", norm(cells[0])):
            continue
        body = norm(" ".join(cells[1:]))
        if any(word in body for word in ("AI", "工具", "脚本", "模型", "代码", "绘图")):
            used.append(cells[0])
    return len(used), used


def audit(project: Path, report_path: Path | None, paper_path: Path | None) -> int:
    fails: list[str] = []
    warns: list[str] = []
    passes: list[str] = []

    if not project.is_dir():
        print(f"[FAIL] PROJECT_ROOT 不存在: {project}")
        return 1

    paper = paper_path or (project / "完整论文-LaTeX" / "main.tex")
    report = report_path or (project / "AI使用报告-LaTeX" / "main.tex")

    if not paper.exists():
        fails.append(f"找不到 LaTeX 论文主文件: {paper}")
        paper_text = ""
    else:
        paper_text = read_tex(paper)
        passes.append(f"已读取论文 LaTeX: {paper}")

    if not report.exists():
        fails.append(f"找不到 AI 使用报告 LaTeX 主文件: {report}")
        report_text = ""
    else:
        report_text = read_tex(report)
        passes.append(f"已读取 AI 报告 LaTeX: {report}")

    paper_norm = norm(paper_text)
    report_norm = norm(report_text)

    # 论文声明和参考文献顺序
    decl = paper_norm.find(norm("AI 工具使用声明"))
    refs = paper_norm.find(norm("参考文献"))
    if decl < 0:
        fails.append("论文中未找到 AI 工具使用声明")
    elif refs < 0:
        fails.append("论文中未找到参考文献，无法检查声明位置")
    elif decl > refs:
        fails.append("AI 工具使用声明位于参考文献之后")
    else:
        passes.append("AI 工具使用声明位于参考文献之前")

    used_decl = norm("使用了 AI 工具") in paper_norm
    unused_decl = norm("未使用任何 AI 工具") in paper_norm
    if used_decl == unused_decl:
        fails.append("论文 AI 使用声明未明确命中且仅命中一个官方口径")
    else:
        passes.append(f"论文声明口径: {'使用了 AI 工具' if used_decl else '未使用任何 AI 工具'}")

    log_count, log_ids = count_log_usage(project / "ai_usage_log.md")
    if log_count == 0:
        if used_decl:
            fails.append("论文声明使用了 AI 工具，但 ai_usage_log.md 无实质记录")
        else:
            warns.append("ai_usage_log.md 缺失或无实质使用行")
    else:
        passes.append(f"ai_usage_log.md 有 {log_count} 条记录 ({', '.join(log_ids[:8])})")
        if unused_decl:
            fails.append("论文声明未使用 AI，但 ai_usage_log.md 存在使用记录")

    # 报告结构和报告/论文口径
    for heading in REPORT_HEADINGS:
        if norm(heading) not in report_norm:
            fails.append(f"AI 使用报告缺少结构部分: {heading}")
    if report_norm:
        if used_decl and norm("使用了 AI 工具") not in report_norm:
            fails.append("报告未体现论文的 AI 使用口径")
        if unused_decl and norm("未使用任何 AI 工具") not in report_norm:
            fails.append("报告未体现论文的未使用口径")
        if norm("参赛队主导") not in report_norm:
            warns.append("报告未明确出现“参赛队主导”，请人工核对核心建模表述")
        else:
            passes.append("报告包含参赛队主导口径")

    pdf = project / "AI工具使用详情.pdf"
    if pdf.exists():
        passes.append("AI工具使用详情.pdf 已存在")
    else:
        warns.append("AI工具使用详情.pdf 尚未生成；编译后必须再次检查")

    for item in passes:
        print(f"[PASS] {item}")
    for item in warns:
        print(f"[WARN] {item}")
    for item in fails:
        print(f"[FAIL] {item}")
    print(f"RESULT: PASS={len(passes)} WARN={len(warns)} FAIL={len(fails)}")
    return 1 if fails else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="AI 使用报告与 LaTeX 论文一致性审计")
    parser.add_argument("project", type=Path, help="PROJECT_ROOT")
    parser.add_argument("--report", type=Path, default=None, help="AI 使用报告 LaTeX 主文件")
    parser.add_argument("--paper", type=Path, default=None, help="论文 LaTeX 主文件")
    args = parser.parse_args()
    return audit(args.project, args.report, args.paper)


if __name__ == "__main__":
    raise SystemExit(main())
