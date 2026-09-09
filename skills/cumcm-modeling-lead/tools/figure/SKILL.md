---
name: cumcm-figure
description: 在国赛建模流程中根据数据与论证目标选择图型、生成和审查论文数据图；SciPilot 方法负责先分析再选图，Nature Figure 只增强少数已冻结的核心终稿图。流程图和模型架构图改用 drawio。
---

# 国赛绘图决策中心

## 路由

先确认模型与结果状态，再选择路线：

| 目的 | 路线 |
|---|---|
| 看数据、诊断模型、快速比较 | SciPilot 轻量探索图 |
| 放入论文的普通数据图 | SciPilot 选图、绘图与视觉回审 |
| 少数核心多面板图或用户明确要求 Nature Figure | SciPilot 先定图型，Nature 再做终稿增强和严格审计 |
| 流程图、模型结构图、思维导图 | `../drawio/SKILL.md` |

Nature 路线不能用于未冻结模型，不能改变源数据、指标或结论。

## SciPilot 主流程

读取 `../../references/roles/编程手/可视化规范.md` 和当前问题需要的 `../../references/绘图参考/`：

1. 剖析变量类型、样本量、分布、异常、分组、时间和相关结构；
2. 明确这张图要支持的一个主要结论；
3. 按数据结构和论证目标推荐图型，同时给出一个备选和不推荐图型的理由；
4. 建模手确认结论和比较口径；普通低风险选择可依据已冻结模型直接推进；
5. 使用 `../../scripts/plot_style.py` 绘图；
6. 使用 `../../scripts/figure_audit.py` 做基础检查，并实际查看渲染图；
7. 保存源数据、脚本、PNG/SVG 和图表—结论映射。

主动拦截掩盖小样本分布的均值柱状图、双 Y 轴、装饰性 3D、饼图、不合理截断、rainbow/jet 色图、分类点错误连线和图例遮挡。

## Nature 终稿增强

只有模型与结果已冻结、图表结论和源数据已锁定时进入：

1. 写明图表结论、源数据、轴与单位、视觉证据和误读风险；
2. 沿用国赛中文字体、最终页面宽度、图题位置和官方模板要求；
3. 默认导出 PNG、SVG、PDF；TIFF 仅在明确需要时导出；
4. 运行 `nature_audit/validate_figure.py` 检查绘图源文件；
5. 多面板图运行 `nature_audit/audit_panel_alignment.py`；
6. 运行 `nature_audit/audit_pdf_text.py` 和 `nature_audit/audit_figure_collisions.py`；
7. 实际查看 PNG/PDF，检查中文、符号、图例、裁切、对齐和灰度辨识；
8. 审计通过后登记到论文证据链。

Nature 期刊专用文件合同、图注字数、AI 图形摘要、OpenRouter 生图、R 后端选择和默认 TIFF 不进入国赛主流程。竞赛官方要求优先于期刊风格。

## 终稿产物

```text
figure.png       论文插图
figure.svg       可编辑矢量图
figure.pdf       最终尺寸和字体检查
source_data.csv  图表源数据
figure_note.md   结论、口径、单位和风险
audit.json       自动检查结果
```

终稿图完成必须满足：数值与冻结结果一致、图型支持声明的结论、无裁切遮挡、最终尺寸可读、源数据与脚本可追溯，并经过人工查看。
