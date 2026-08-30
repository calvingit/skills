---
name: wayfinding
description: "用于跨会话探索不确定技术路径，维护决策地图而不写代码。"
---

# Wayfinding

当 Destination 可以命名、但重要路径仍处于 **Fog of war**、且决策工作无法在单个会话内完成时使用本 skill。首次进入前向用户说明判断依据并取得确认。Wayfinding 解决决策，不执行最终任务；Map 完成的标志是通往 Destination 的关键决策已经清晰，可以进入 `to-spec` 落盘。

## 首次进入、接续与 Destination 变更

- **首次进入**：不存在当前 Destination 的 MAP.md 时，按「建立地图」创建 MAP.md 和当前可描述的 decision tickets。
- **跨会话接续**：先读取 MAP.md 的 low-resolution view、当前 frontier ticket 和必要依赖；不重新进行无目标的广度调查，不重复请求进入确认，也不覆盖已有 ticket 结论。
- **Destination 变更或用户请求冲突**：与用户重新划定 Destination。将不再适用的 tickets 标为 superseded 或移入 Out of scope，保留其依据但不得静默沿用旧结论。

## 本地工作文档

不使用在线 issue tracker。任务目录按 `to-spec` skill 定义的任务目录规则确定，并只在本流程下创建：

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

每个 decision ticket 解决一个决策或取得该决策所需的事实，对应的 Markdown 文件包含：

1. 问题
2. 类型
3. Blocked by
4. 事实依据
5. 结论

类型按解决方式选择：

**HITL** 表示必须由用户本人参与判断；**AFK** 表示 Agent 可以独立推进。不得由 Agent 代替用户完成 HITL 判断。

- **Grilling (HITL)**：需要用户判断。按 `grilling` skill 的 Design Tree / frontier / round 机制，对该节点建立局部 Design Tree 并批量提出当前局部 frontier。
- **Research (AFK)**：可以通过项目、文档或只读外部调查查明。
- **Prototype (HITL)**：仅靠讨论无法判断，需要用户明确授权的低成本分析原型。
- **Task (HITL or AFK)**：没有待决定或调查的内容，但必须先完成某项外部准备或人工动作才能继续决策。Task 只用于解除 decision ticket 的阻塞，不交付 Destination。

不得把 implementation ticket 伪装成 decision ticket。结论只回答问题，不包含最终代码实施步骤。

## 建立地图

1. 命名 Destination 并明确范围。
2. 广度优先调查，找出当前可准确描述的 decision tickets、blocking edges 和 Fog of war。
3. 向用户说明为何无法在当前会话内收敛，并取得进入确认。
4. 创建 MAP.md 和当前可描述的 decision ticket 文件。
5. 连接 blocking edges，计算 frontier。
6. 停止建图；同一会话不要继续解决多个 decision tickets。

如果调查后不存在 Fog of war，不创建 Map；决策可直接收敛时建议改用 `grilling` skill，需求本就清晰时直接建议 `to-spec`。

## 推进地图

每个会话只解决一个 decision ticket：

1. 先读取 MAP.md 的 low-resolution view，再读取选中的 frontier decision ticket 及必要依赖，不加载全部历史；只在需要时展开读取完整内容。
2. 开始解决前，检查工作区与该 ticket 文件是否已有未完成的并发修改；发现并发修改或冲突时停止，保留双方结论并交回用户处理，不静默覆盖。
3. 按类型解决问题；Grilling ticket 按 round 批量提出当前局部 frontier。
4. 同一 Grilling ticket 内，用户确认当前 round 后不单独询问是否继续：立即记录本 round 结论并重算局部 frontier；若仍有可问问题，直接给出推荐并提出下一 round。
5. 暂停点仅限于等待用户回答已提出的 round、当前 ticket 已完成、遇到阻塞，或需要收尾交接；不得把「是否继续」作为独立暂停点。
6. 当前 ticket 完成后，将事实依据和最终结论写入该 decision ticket 文件。
7. 在 Decisions so far 中增加相对链接和一句话结论，并从 Frontier 移除该 ticket。
8. 根据新结论创建已经可以精确表述的 decision tickets，并将对应内容从 Not yet specified 移出。
9. 重算 frontier；发现超出 Destination 的内容时移入 Out of scope；若 frontier 非空，在汇报中推荐下一个可处理 ticket，但不得在同一会话继续解决另一个 decision ticket。

MAP.md 和 decisions/ 可以在收敛前增量更新，但不得提前创建或修改正式 SPEC.md、PLAN.md。

## 退出

满足以下条件时退出：

- 当前 frontier 为空
- Not yet specified 中不再有指向 Destination 的 Fog of war
- 所有阻塞性决策都有可追溯结论

退出后汇总结论并请求用户最终确认；确认后建议调用 `to-spec` skill 一次性生成 SPEC.md 与 PLAN.md。工作文档保留为决策依据，不承担实现说明。
