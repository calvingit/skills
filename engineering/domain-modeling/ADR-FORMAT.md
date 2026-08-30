# ADR Format

仅在项目没有既有 ADR 或 decision-record 格式时使用。

```markdown
# <Short decision title>

<用一到三句话记录背景、决定和理由。>
```

只有同时满足以下条件才记录 ADR：改变决定的成本明显、缺少上下文会让后续维护者意外、当时存在真实可行的替代方案。Status、Considered Options 和 Consequences 只在确实增加长期价值时加入。

目录和编号沿用项目约定。项目没有约定时，不自动采用固定 `docs/adr/`。先确定写入位置，再按该目录已有编号递增。
