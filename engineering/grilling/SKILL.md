---
name: grilling
description: "在实现前拷问方案、查证可访问事实、收敛需求或设计决策，并默认在临时目录沉淀术语、ADR 与决策记录。"
---

# Grilling

在实现前把需求、方案或预期行为变更里没定下来的选择谈清楚。`grilling` 是唯一的会话控制者：调查事实、维护 Design Tree、计算 frontier、组织 round，把真正的决策交给用户，并按 `domain-modeling` 的纪律把确认的术语、ADR 和决策沉淀为会话文档。开始时读取 `domain-modeling` Skill（唯一规则来源，不把它的格式、ADR gate 或写入规则复制到本文件），按它的规则发现适用 `AGENTS.md`、Profile、已有领域文档和相关代码事实；用一两句话说清 **Destination**（任务完成后应达到的状态和边界），然后创建会话文档目录 `${TMPDIR:-/tmp}/grilling-<UTC 时间戳>/`。被 `wayfinding` 等 workflow 编排时，落盘位置遵循编排方的约定。

## 会话文档

- `decisions.md`：Design Tree 快照——已确认决策、放弃的主要方案、默认假设、待解问题。每轮结束更新，由本 skill 维护，始终存放在会话目录。
- `glossary.md` 与 `adr/NNNN-*.md`：会话中确认的术语和通过 ADR gate 的长期决策；判定规则和格式沿用 `domain-modeling` 的 CONTEXT-FORMAT 与 ADR-FORMAT，ADR 编号在该目录内递增。
- 文件懒创建，有内容才写；用户确认一项立即写入一项，不等会话结束。术语冲突、一词多义、表述与代码或公开 contract 冲突、新概念需要记录时，纳入 Design Tree 随 frontier 提出，不另开访谈。
- 写入位置：glossary 和 ADR 默认随 `decisions.md` 存放在会话目录，不写目标仓库。用户要求写入项目时，先检查 Profile 的 `domain_glossary` 与 `adr_root`：已配置则按配置位置写入；未配置或为 `auto` 时先调用 `project-setup` 确认文档目录，再继续执行；setup 取消或仍为 `auto` 时按 `domain-modeling` 的规则动态发现。

## 访谈机制

把会改变方案的决策连成 **Design Tree**，让每个决策都能解锁、排除或改变后面的决策。按 **round** 推进，**frontier** 是前置事实和上游决定都已解决、现在不用猜就能问的所有决策。每轮一次问完完整 frontier，等用户回答后重新计算；某题要看本轮另一道未决题的答案才能决定时留到下一轮，不按业务叙述顺序拆开本可同时回答的问题。

每道题说清会改到的契约或范围，列出主要互斥方案，给出推荐项和可验证依据。事实由你负责查：互不依赖的代码事实可以并行派出 sub-agent 调查，不让用户提供能从工作区、工具、文档、调用链或测试里查到的信息；某个事实没查清时只锁定依赖它的题目，其余照常提出。决策是用户的：提出并等待。

每轮按以下格式提问，题号、推荐和分隔符必须保留：

```markdown
❓ **Q1** - **<问题标题>**：<问题说明和候选>

➡️ <推荐答案及理由>

---
**回答格式：** `1A 2B`<需要保留边界时直接写明，例如 `3B（保留：……）`。>
```

frontier 清空后，汇总已确认结论、会话文档位置和尚未写入项目的术语与 ADR，请用户最后确认并选择是否落盘，在此之前不执行方案。

## 边界

- 不写业务代码，不创建 `SPEC.md`、`HLD.md`、交付任务或实现文档，那是 `to-spec`、`high-level-design` 和 `to-tickets` 的职责。
- 按适用 Profile 的 `requirement_authority` 查证需求事实：`external-manual` 模式下用户提供的快照视为待确认输入；用户引用但访问不到的需求来源不自行补全，把会改变行为、边界或验收的缺口交给用户。
- 重要路径超出当前会话能看清的范围时，说明依据并建议 `wayfinding`；实际行为违反已有权威来源定义的 expected behavior 时，停止本流程并建议 `debug`。对话和解释沿用用户的语言。
