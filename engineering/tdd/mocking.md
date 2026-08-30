# When to Mock

优先使用真实、快速、确定性的依赖。只有真实外部不确定性需要隔离时，才在对应 Seam 使用 mock Adapter，例如第三方 API、不可控网络、时间或随机源；数据库和文件系统优先使用项目已有 test database、emulator 或 in-memory Adapter。

不要 mock 自己控制的内部 Modules，也不要用 mock 复制当前 Implementation 的调用结构。一个 test double 应满足已确认 Interface，并返回独立于被测实现的结果。

外部依赖应通过具体、稳定的 Interface 注入。优先为每个真实操作定义明确入口，不要暴露一个需要在测试中编写条件分支的通用 fetcher。
