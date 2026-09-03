---
name: wayfinding
description: "为跨 session 的技术或方案不确定性建立并推进决策地图；不把不可访问的需求来源误判为 Fog of war。"
---

# Wayfinding

当 Destination 可以命名、但重要路径仍处于 **Fog of war**，而且决策工作无法在单个会话内完成时使用本 skill。首次进入前向用户说明判断依据并取得确认。Wayfinding 默认只解决决策，不执行最终任务；Destination 可以是一份 SPEC、一个最终决定，也可以是 Notes 明确允许的直接变更。

## 首次进入、接续与 Destination 变更

- **首次进入**：不存在当前 Destination 的 MAP.md 时，按「建立地图」创建 MAP.md 和当前可描述的 decision tickets。
- **跨会话接续**：先读取 MAP.md 的 low-resolution view、当前 frontier ticket 和必要依赖；不重新进行无目标的广度调查，不重复请求进入确认，也不覆盖已有 ticket 结论。
- **Destination 变更或用户请求冲突**：与用户重新划定 Destination。将不再适用的 tickets 标为 superseded 或移入 Out of scope，保留其依据但不得静默沿用旧结论。

## Storage and claim

默认使用本地工作文档。如果适用的 `Engineering Skills Profile` 配置了 external issue tracker，就读取其中的 instructions，使用 tracker 原生的 child issue、blocking 和 assignment。没有这项配置也不阻塞流程，继续使用本地模式。

同时读取 Profile 的 `requirement_authority`，但只用它划分问题类型。外部需求不可访问、需求增量未提供或产品边界未确认属于 requirement gap，应交给用户或 `grilling`；只有目标已经成立而技术路径仍看不清时才属于 Fog of war。Wayfinding 不直接同步外部 PRD，也不把未验证需求写成 decision 结论。

本地任务目录优先采用用户本次指定，其次采用项目既有任务文档约定；仍不明确且位置会影响项目结构时询问用户。Wayfinding 只在本流程下创建：

    MAP.md
    decisions/
      01-<decision>.md
      02-<decision>.md

MAP.md 是 low-resolution index，不重复保存每项决策的完整内容。每个 decision ticket 只在对应 decisions/ Markdown 文件中详细记录；decision ticket 是逻辑工作单元，Markdown 文件只是本地存储形式。

## MAP.md

固定使用以下 headings，章节内容沿用项目语言：

1. **Destination**：完成分析时应达到的状态，同时固定范围。
2. **Notes**：后续会话都必须遵循的项目约束、适用 skill 和长期偏好。
3. **Decisions so far**：每个已解决 decision ticket 的名称、相对链接和一句话结论。
4. **Frontier**：所有 blocking edges 已解决、现在可以处理的 decision tickets。
5. **Not yet specified**：仍属于 Destination，但目前还无法精确表述为 decision ticket 的 Fog of war。
6. **Out of scope**：明确不属于当前 Destination 的内容。

Fog of war 是尚未看清的问题空间，Not yet specified 是 MAP.md 中记录它的区域，两者不是同义词。问题已经能够精确表述时，即使仍被 blocking edges 阻塞，也应创建 decision ticket；只有问题本身还不能精确表述时才留在 Not yet specified。Out of scope 不会随着 frontier 推进而转化为 decision ticket，除非用户重画 Destination。

## Decision tickets

每个本地 decision ticket 只处理一个决策，或收集做出该决策所需的事实。对应的 Markdown 文件包含：

1. 问题
2. 类型
3. Blocked by
4. Status：`open | in-progress | resolved | superseded`
5. Claimed by：`unclaimed | <runtime-id>`；Runtime 没有稳定 ID 时使用 `local-session-<UTC timestamp>`
6. 事实依据
7. 结论

本地 frontier 只包含 blockers 全部 resolved、Status 为 open 且 Claimed by 为 unclaimed 的 tickets。开始工作前先写入 claim，再重新读取 ticket 和工作区 diff；发现并发 claim、内容变化或冲突时停止，不覆盖另一会话。外部 tracker 则使用 assignment 作为 claim。

类型按解决方式选择：

**HITL** 表示必须由用户本人参与判断；**AFK** 表示 Agent 可以独立推进。不得由 Agent 代替用户完成 HITL 判断。

- **Grilling (HITL)**：需要用户判断。使用 `grilling` 的 Design Tree / frontier / round 机制，其中的领域术语与必要 ADR 由 `grilling` 编排的 domain-modeling discipline 同步维护。
- **Research (AFK)**：可以通过项目、文档或只读外部调查查明。只有 Runtime 支持且当前授权允许时才并行委派，否则作为普通 frontier ticket 处理。
- **Prototype (HITL)**：仅靠讨论无法判断，需要用户明确授权的低成本分析原型。
- **Task (HITL or AFK)**：没有待决定或调查的内容，但必须先完成某项外部准备或人工动作才能继续决策。Task 只用于解除 decision ticket 的阻塞，不交付 Destination。

不得把 implementation ticket 伪装成 decision ticket。结论只回答问题，不包含最终代码实施步骤。

## 建立地图

1. 命名 Destination 并明确范围。
2. 广度优先调查，找出当前可准确描述的 decision tickets、blocking edges 和 Fog of war。
3. 向用户说明为何无法在当前会话内收敛，并取得进入确认。
4. 创建 MAP.md 和当前可描述的 decision ticket，初始 Status 为 open、Claimed by 为 unclaimed。
5. 连接 blocking edges，计算 frontier。
6. 停止建图；同一会话不要继续解决多个 decision tickets。

如果调查后不存在 Fog of war，不创建 Map；决策可直接收敛时建议改用 `grilling` skill，需求本就清晰时按用户目标直接进入后续工作。

## 推进地图

每个会话只解决一个 decision ticket：

1. 先读取 MAP.md 的 low-resolution view，再读取选中的 frontier decision ticket 及必要依赖，不加载全部历史；只在需要时展开读取完整内容。
2. 开始前先 claim ticket，再重新读取文件和工作区 diff；发现并发 claim、修改或冲突时停止，保留双方结论并交回用户处理。
3. 按类型解决问题；Grilling ticket 按 round 批量提出当前局部 frontier。
4. 同一 Grilling ticket 内，用户确认当前 round 后不单独询问是否继续：立即记录本 round 结论并重算局部 frontier；若仍有可问问题，直接给出推荐并提出下一 round。
5. 暂停点仅限于等待用户回答已提出的 round、当前 ticket 已完成、遇到阻塞，或需要收尾交接；不得把「是否继续」作为独立暂停点。
6. 当前 ticket 完成后，将事实依据和最终结论写入 ticket，Status 改为 resolved；超出 Destination 时改为 superseded。
7. 在 Decisions so far 中增加相对链接和一句话结论，并从 Frontier 移除该 ticket。
8. 根据新结论创建已经可以精确表述的 decision tickets，并将对应内容从 Not yet specified 移出。
9. 重算 frontier；发现超出 Destination 的内容时移入 Out of scope；若 frontier 非空，在汇报中推荐下一个可处理 ticket，但不得在同一会话继续解决另一个 decision ticket。

MAP.md 和 decisions/ 可以在收敛前增量更新，但不得提前创建或修改下游 `to-spec` 生成的 SPEC、`high-level-design` 生成的 HLD 或 `to-tickets` 生成的 delivery tickets/。

## 退出

满足以下条件时退出：

- 当前 frontier 为空
- 所有 decision tickets 已 resolved 或 superseded，不存在仍 active 的 claim
- Not yet specified 中不再有指向 Destination 的 Fog of war
- 所有阻塞性决策都有可追溯结论

退出后汇总结论并请求用户最终确认，再按 Destination 选择出口：需要构建契约时交给 `to-spec`；Destination 只是一个最终决定时输出 decision handoff；Notes 明确允许直接变更时交给对应执行流程。MAP.md 与 decisions/ 保留为决策依据，不承担实现说明。
