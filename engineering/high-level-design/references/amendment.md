# HLD Amendment

已有 `HLD.md`，且 SPEC、代码库事实或已确认设计发生变化时读取本文件。判断是否需要 HLD，或首次创建 HLD 时不要加载本文件。只修订同一文件，不创建并行版本。

先比较旧 / 新 SPEC、当前 HLD、代码库事实和现有 tickets，把设计变化分类为 `added`、`changed`、`removed` 或 `no design effect`：

- 保留未受影响的 D ID；新增决定追加新 ID，不重新编号。
- 需求或外部行为变化先由 `to-spec` 修订 SPEC，再修订 HLD。
- 设计变化但需求不变时，只更新 HLD，不反向改写 SPEC。
- 已有 graph 时只读检查哪些 ticket 引用了受影响 D、哪些已实现行为仍有效，以及需要 amendment、correction、migration 或 replacement。不修改 ticket。
- 受影响 worker 仍在写入时，请求 `loop` 停止派发新任务、回收部分执行回执并确认不再写入。
- 向用户展示 design delta 与 ticket impact，确认后更新同一份 HLD，再交给 `to-tickets` 协调 graph。

实现中发现 HLD 无法成立时，worker 必须报告阻塞；不能自行改变共享设计约束后继续。修订 HLD 后再按实际影响恢复执行。

章节结构、写作规则和完成检查见 [hld-template.md](hld-template.md)。
