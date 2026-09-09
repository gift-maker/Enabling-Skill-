# Nature Figure 审计脚本来源

本目录中的四个 Python 脚本取自：

- 项目：Yuan1z0825/nature-skills
- 路径：`skills/nature-figure/scripts/`
- 上游提交：`7e626a86a0ac8d078be224e0a76aa1327875b0a1`
- 取得日期：2026-09-09
- 许可证：Apache License 2.0，见 `LICENSE-NATURE-SKILLS.txt`

内置文件：

- `validate_figure.py`
- `audit_panel_alignment.py`
- `audit_pdf_text.py`
- `audit_figure_collisions.py`

本 Skill 只把它们作为已冻结国赛核心终稿图的可选质量审计工具。国赛官方尺寸、中文字体和提交格式优先；Nature 期刊专用规则、AI 图形摘要与 OpenRouter 路线未被整合。

本地仅把碰撞审计脚本的依赖安装提示改为本 Skill 的 `requirements-validation.txt`，审计逻辑未改变。
