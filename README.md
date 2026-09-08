# CUMCM Modeling Lead

面向全国大学生数学建模竞赛（CUMCM）的全队一体化 Agent Skill。以建模手为总控，把读题、建模、编程、验证、绘图、论文和提交接入同一条可追溯证据链。

> 本项目用于竞赛训练和队内协作。参赛时应以当届官方规则为准，队员必须理解、核验并负责最终模型、代码、论文和 AI 使用披露。

![数学建模全流程](docs/workflow.png)

## 核心目标

- 完整读取题面和附件，明确每一问及其依赖关系；
- 区分题目事实、数据发现、领域依据、建模假设、设计选择和未知项；
- 建立可追溯的假设—变量—方程—目标—约束逻辑链；
- 比较基线、主模型和强备选，说明选模与模型组合理由；
- 所有正式数值来自真实运行，并记录输入、代码、参数、种子、输出和哈希；
- 独立检查数据、公式、量纲、泄漏、约束、边界、敏感性和稳健性；
- 论文只引用已经冻结的结果和图表；
- 检查摘要、正文、表格、图片、结论、附录和支撑材料的一致性。

## 全流程

```text
题面与附件
→ 全题拆解与依赖图
→ M0 模型合同
→ 数据契约与基线
→ 主模型与真实运行
→ 独立验证与敏感性分析
→ 结果、图表和结论冻结
→ 论文装配
→ 一致性与评委终审
→ 提交包复核
```

权威证据链：

```text
Requirement → Model Contract → Run → Result → Figure → Claim → Paper
```

## 三人分工

| 角色 | 负责内容 | 核心交付 |
|---|---|---|
| 建模手 | 题意、依赖关系、假设、变量、公式、目标、约束、选模和结论边界 | `建模总控.md`、`模型合同.md`、`术语与符号表.md` |
| 编程手 | 数据契约、EDA、基线、主模型、真实运行、验证、敏感性和图表数据 | 代码、Run、Result、诊断和复现入口 |
| 论文手 | 根据冻结证据写作、制图、排版、编译和一致性检查 | 论文、图表、表格、引用和提交包 |

独立验证是一个职责，可以由未参与当前部分的队员承担。验证者默认怀疑主方案，不能用润色掩盖数据、模型或证据问题。

## 安装

### 使用 Codex Skill Installer

在 Codex 中发送：

> 请使用 skill-installer 从 GitHub 仓库 `gift-maker/Enabling-Skill-` 的 `skills/cumcm-modeling-lead` 路径安装这个 Skill。

安装后新建任务，或在下一轮明确调用：

> 使用 `$cumcm-modeling-lead` 分析这道国赛题。先完成题包审计、全题依赖图和逐问模型合同，通过 M0 后再进行正式计算。

### 手动安装

将整个目录：

```text
skills/cumcm-modeling-lead
```

复制到：

```text
%USERPROFILE%\.codex\skills\cumcm-modeling-lead
```

必须复制整个目录，不能只复制 `SKILL.md`。

## 第一次使用

初始化比赛项目：

```powershell
python skills/cumcm-modeling-lead/scripts/init_competition_project.py `
  D:/cumcm/projects/2026-C `
  --competition CUMCM `
  --problem C
```

初始化后会生成：

```text
2026-C/
├── 0_题面与附件/
├── 1_数据/
│   ├── raw/
│   ├── processed/
│   └── data_contract.json
├── 2_建模/
├── 3_代码/
├── 4_结果/runs/
├── 5_图表/
├── 6_论文/
├── 7_提交/
├── registries/
├── 建模总控.md
├── 模型合同.md
├── 术语与符号表.md
├── ai_usage_log.md
└── project_state.json
```

## 真实运行记录

使用统一入口执行模型：

```powershell
python skills/cumcm-modeling-lead/scripts/record_run.py `
  --root D:/cumcm/projects/2026-C `
  --question Q1 `
  --purpose baseline `
  --status baseline `
  --input 1_数据/raw/data.csv `
  --code 3_代码/q1.py `
  --output 4_结果/q1.csv `
  -- python 3_代码/q1.py
```

工具会生成唯一 `run_id`，保存日志，并记录输入、代码和输出的 SHA-256。

独立验证完成后，带验证证据更新状态：

```powershell
python skills/cumcm-modeling-lead/scripts/update_evidence_status.py `
  --root D:/cumcm/projects/2026-C `
  --registry run `
  --id R001 `
  --field validation_status `
  --value passed `
  --evidence 4_结果/Q1验证报告.md
```

## 五本证据登记账

| 文件 | 用途 |
|---|---|
| `run_ledger.csv` | 记录计算命令、输入、代码、参数、输出和运行状态 |
| `result_registry.csv` | 记录可引用结果、单位、场景、来源 Run 和验证状态 |
| `claim_ledger.csv` | 记录论文核心结论及其结果、图表、公式或来源证据 |
| `figure_evidence.csv` | 记录图表文件、源数据、生成脚本、结论和视觉检查 |
| `issue_ledger.csv` | 记录 P0–P3 问题、修复责任人和状态 |

程序成功运行不代表模型有效；图表成功导出不代表可以写进论文；文字表达流畅不代表结论有证据。

## 终稿证据门

终稿前运行：

```powershell
python skills/cumcm-modeling-lead/scripts/audit_evidence.py `
  D:/cumcm/projects/2026-C `
  --require-final
```

以下情况会被阻塞：

- 没有真实运行记录；
- 正式结果没有 `run_id` 或来源文件；
- 对应运行失败或尚未独立验证；
- 论文主张没有结果、图表、公式或来源支持；
- 正式图表没有源数据、生成脚本或视觉检查；
- 结论引用尚未冻结的结果；
- 存在开放的 P0/P1 问题。

## 模型选择与组合

每问默认建立三层路线：

- **基线：**最简单且能完整回答问题；
- **主模型：**针对本题关键结构，并产生可验证增益；
- **强备选：**假设或求解路线不同，用于主模型失败或稳健性检查。

支持预测→优化、机制+数据、并行比较、集成预测、分层模型、评价→决策等组合。模型组合必须明确输入输出接口，并传播上游误差。遗传算法、粒子群等属于求解方法，不能代替数学模型。

## 可选验证工具

基础依赖见 `requirements.txt`。按题目需要安装：

```powershell
pip install -r skills/cumcm-modeling-lead/requirements-validation.txt
```

可选工具包括：

- Pandera：数据字段、类型、范围和唯一性检查；
- SymPy：表达式等价、符号推导和解回代；
- SALib：Morris、Sobol、FAST 等敏感性分析；
- Pint：单位与量纲；
- uncertainties：不确定性传播。

这些工具只能检查各自覆盖的部分，不能自动证明整个现实模型正确。

## Skill 结构

```text
skills/cumcm-modeling-lead/
├── SKILL.md
├── README.md
├── references/
├── assets/
├── scripts/
├── tools/
├── agents/
├── requirements.txt
└── requirements-validation.txt
```

主要入口：

- [`SKILL.md`](skills/cumcm-modeling-lead/SKILL.md)
- [`全队一体化工作流`](skills/cumcm-modeling-lead/references/全队一体化工作流.md)
- [`证据链与独立验证`](skills/cumcm-modeling-lead/references/证据链与独立验证.md)
- [`模型选择与整合协议`](skills/cumcm-modeling-lead/references/模型选择与整合协议.md)
- [`论文与图表证据协议`](skills/cumcm-modeling-lead/references/论文与图表证据协议.md)
- [`第三方来源与整合说明`](skills/cumcm-modeling-lead/references/第三方来源与整合说明.md)

## 验证状态

本地已完成：

- Skill 结构校验；
- Python 源码语法检查；
- Markdown 相对链接检查；
- 项目初始化测试；
- 真实运行与 SHA-256 记录测试；
- 未验证结果阻塞测试；
- 终稿证据门通过测试；
- ZIP 内容与缓存残留检查。

许可证、原始基础框架和参考项目见 [`CREDITS.md`](skills/cumcm-modeling-lead/CREDITS.md) 与 Skill 内各第三方组件的许可证文件。
