# Deepening

说明如何根据依赖类型，把一组 shallow Modules 安全地收敛为更少、更 deep 的 Modules。术语以 [SKILL.md](SKILL.md) 为准。

## Dependency categories

### 1. In-process

纯计算或内存状态，没有 I/O。可以直接合并 Modules，并通过新 Interface 测试，不需要 Adapter。

### 2. Local-substitutable

这类依赖有可在测试中运行的本地替代物，例如 PGLite 或 in-memory filesystem。测试通过本地替代物运行；该 Seam 属于 Module 内部，不要把 port 暴露到外部 Interface。

### 3. Remote but owned

依赖是自己控制的远程服务。由 deep Module 拥有业务逻辑，在 Seam 上定义 port；生产使用 HTTP、gRPC 或 queue Adapter，测试使用 in-memory Adapter。

### 4. True external

依赖是无法控制的第三方服务。deep Module 接收外部 port，测试提供最小 mock Adapter，只模拟已确认的外部 contract。

## Seam discipline

- 一个 Adapter 只是 hypothetical Seam，至少两个有真实用途的 Adapter 才证明 Seam 成立。
- deep Module 可以有只供自身 Implementation 使用的 internal Seams，但不要因为测试使用它们就把它们暴露到外部 Interface。

## Testing strategy

- 新测试通过深化后 Module 的 Interface 验证可观察结果。
- 当 Interface 级测试已经覆盖原有行为时，删除只约束旧 shallow Modules 内部结构的测试，不叠加重复测试层。
- Implementation 重构但外部行为不变时，Interface 级测试应继续有效。
