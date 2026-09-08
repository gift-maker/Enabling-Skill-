# cumcm-modeling-lead｜国赛全队一体化总控版

本 Skill 从队内 `cumcm-step-review` 改造而来，以建模手为总控，把建模、编程、论文和独立验证接入同一条可追溯证据链。它保留真实计算、题型匹配验证、结果冻结、复现和 AI 使用留痕能力，并把建模手对全题逻辑的掌控设为正式编程前的硬门槛。

核心闭环：

```text
完整读题与附件
→ 全题依赖图
→ M0 建模逻辑门
→ 审计基线与主方案原型
→ 全量计算
→ 题型匹配验证
→ 建模手结果回审
→ 跨问一致性
→ 结果冻结与论文交接
→ Claim/Result/Figure/Run 一致性审查
→ Fresh-eyes 评委终审
```

## 关键改变

- 区分题目事实、数据发现、领域依据、建模假设、设计选择和未知项；
- 每条核心公式、目标和约束记录现实含义、来源、单位、代码接口与失效条件；
- 候选阶段比较 2–4 个模型族，实现阶段默认保留审计基线与主方案；
- 建模手能够独立解释逻辑链并通过 M0 后，才进入正式全量计算；
- 优化问题先完成数学规划结构，再选择精确、结构化、近似或启发式求解方法；
- 前问结果进入后问时检查单位、索引、时间尺度和不确定性传播；
- 文献和优秀论文检索限时进行，用于补充候选与证据，不替代本题推导；
- 缺少 Subagent 时允许由未参与该部分的队员交叉复核；
- AI 留痕记录实际采纳、修改、弃用与人工核验，固定声明不能替代真实主导。

## 使用

把赛题和附件放在独立项目目录，然后调用：

> 使用 `$cumcm-modeling-lead` 完成这道国赛题。先建立全题依赖图和逐问模型合同，逐项说明假设、变量、方程、目标与约束的来源；我通过 M0 后，再实现审计基线和主方案，完成真实计算、验证、跨问回审和结果冻结。

初始化一套全队共享的题目项目：

```bash
python scripts/init_competition_project.py D:/cumcm/projects/2026-C --competition CUMCM --problem C
```

用统一入口执行并记录一次计算：

```bash
python scripts/record_run.py --root D:/cumcm/projects/2026-C --question Q1 --purpose baseline --status baseline --input 1_数据/raw/data.csv --code 3_代码/q1.py --output 4_结果/q1.csv -- python 3_代码/q1.py
```

独立验证完成后，带证据更新运行状态：

```bash
python scripts/update_evidence_status.py --root D:/cumcm/projects/2026-C --registry run --id R001 --field validation_status --value passed --evidence 4_结果/Q1验证报告.md
```

论文冻结前审计证据关系：

```bash
python scripts/audit_evidence.py D:/cumcm/projects/2026-C --require-final
```

## 主要产物

- `建模总控.md`
- `模型合同.md`
- `术语与符号表.md`
- `results/` 下的真实结果、日志和复现清单
- `ai_usage_log.md`
- `registries/run_ledger.csv`
- `registries/result_registry.csv`
- `registries/claim_ledger.csv`
- `registries/figure_evidence.csv`
- `registries/issue_ledger.csv`
- 向编程手和论文手交付的逐问结果包

所有题目产物写入题目项目目录，Skill 目录保持只读。主体许可证与第三方来源见 [LICENSE](LICENSE) 和 [CREDITS.md](CREDITS.md)。
