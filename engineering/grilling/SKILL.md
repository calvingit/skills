---
name: grilling
description: "在实现前拷问方案、查证可访问事实、收敛需求或设计决策，并默认在临时目录沉淀术语、ADR 与决策记录。"
---

# Grilling

在实现前收敛需求、方案或预期行为中的未决选择，`grilling` 负责调查事实、维护 Design Tree、计算 frontier 和组织 round，决策由用户确认。

开始时读取 `domain-modeling`，按其规则发现适用的 `AGENTS.md`、Profile、领域文档和代码事实，说明 **Destination**（目标状态与边界），先将 `DOC_DIR` 设为 `${TMPDIR:-/tmp}/grilling-<UTC 时间戳>/` 并创建该目录。由 `wayfinding` 等 workflow 编排时则遵循编排方的落盘约定。

## 会话文档

- `decisions.md` 是 Design Tree 快照，用于记录已确认决策、主要放弃方案、默认假设和待解问题，并在每轮结束时更新。
- `glossary.md` 与 `adr/NNNN-*.md` 用于记录确认后的术语和通过 ADR gate 的长期决策，格式与编号规则沿用 `domain-modeling`。
- 文件按需创建并在用户确认后立即写入，术语冲突、歧义、与代码或公开 contract 冲突的新概念则作为 Design Tree 决策处理。
- 未指定项目文档目录时，所有文档都写入已创建的 `DOC_DIR` 而不写入目标仓库。
- 用户要求写入项目时，先沿用用户指定或已证实的项目位置。Profile 已配置 `domain_glossary`、`adr_root` 时使用该入口；未配置或为 `auto` 时按 `domain-modeling` 动态发现，不强制先跑 `project-setup`。只有无法确定写入位置时才询问。

## Interview 机制

把会改变方案的决策连成 **Design Tree** 并按 **round** 推进，其中 **frontier** 是依赖已解决、现在可以无猜测提问的决策集合，每轮一次问完当前 frontier 后等待用户回答并重算，相互依赖的问题留到下一轮，无依赖的问题合并提问。

每道题说明受影响的契约或范围、主要互斥方案、推荐项和依据，可从工作区、工具、文档、调用链或测试查到的事实由你调查，未查清的事实只阻塞依赖它的问题，其余照常提出，然后等待用户决定。

每轮按以下格式提问，题号、推荐和分隔符必须保留：

```markdown
❓ **Q1** - **<问题标题>**：<问题说明和候选>

➡️ <推荐答案及理由>

---
**回答格式：** `1A 2B`。需要保留边界时直接写明，例如 `3B（保留：……）`。
```

## Acceptance Frontier

对每个影响外部行为的决策确认行为、输入/输出、成功与失败语义（含取消、超时、权限和环境）、兼容策略、可观察结果及证据来源，任一项未确认都留在 frontier。

frontier 清空后：

1. 在 `${DOC_DIR}/acceptance-draft.md` 写入仅含 `R`、`AC`、场景、expected result 和 evidence source 的草稿，不写实现建议、mock、文件路径或内部调用顺序。
2. 汇总结论、会话文档位置，以及尚未写入项目的术语和 ADR，并请用户最终确认后建议交给 `to-spec` 落盘。

## 边界

- 不写业务代码，不创建 `SPEC.md`、`HLD.md`、交付任务或实现文档，因为这些不是本 Skill 的职责。
- 按适用 Profile 的 `requirement_authority` 查证需求事实，在 `external-manual` 模式下将用户提供的快照视为待确认输入，不自行补全用户引用但无法访问的需求来源，而是把会改变行为、边界或验收的缺口交给用户。
- 重要路径超出当前会话能看清的范围时，说明依据并建议 `wayfinding`。实际行为违反已有权威来源定义的 expected behavior 时则停止本流程并建议 `debug`，对话和解释沿用用户的语言。
