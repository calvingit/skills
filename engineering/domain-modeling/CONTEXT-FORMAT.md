# CONTEXT Format

仅在项目没有既有领域文档格式时使用。

```markdown
# <Context name>

<一两句话说明这个 context 是什么、为什么存在。>

## Language

**Order**:
<一两句话说明它是什么。>
_Avoid_: Purchase, Transaction
```

规则：

- 同一概念有多个词时选择一个 canonical term，其余列入 `_Avoid_`。
- 定义只写“它是什么”，保持一两句，不写实现动作。
- 只记录项目领域特有概念，不记录 timeout、error type 或通用设计模式。
- 确实存在多个 context 时，可以使用根级 `CONTEXT-MAP.md` 指向各 context；无法判断归属时询问用户，不猜。
- 文件只在第一个术语确认且写入位置明确后创建，不预建空文档。
