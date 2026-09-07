# Design It Twice

只有用户要求探索多个 Interface，或单一方案不足以形成可靠设计判断时使用。开始前读取 [SKILL.md](SKILL.md) 与 [DEEPENING.md](DEEPENING.md)。

## Process

1. 向用户说明所有候选必须满足的约束、依赖类别和 Seam。可以用最小代码草图帮助理解，但草图不是候选方案。
2. 只比较有实际取舍的候选，通常两个即可。不要为凑数量增加没有真实用途的方向。常见取舍包括更小的 Interface、更简单的默认调用路径，以及已有真实扩展需求时的灵活性；存在远程依赖时，ports-and-adapters 可以作为一个候选，不是必选项。
3. 是否并行委派由问题规模与当前授权决定。运行环境支持且用户授权并行 Agent 时可以并行，否则在当前会话中按相同约束分别生成候选。后一个方案不能只是前一个方案的改名版本。
4. 每个候选必须给出 Interface、调用示例、隐藏在 Seam 后的 Implementation、依赖 / Adapter 策略，并说明 Leverage 在哪里强、在哪里薄。
5. 依次展示候选，再按 Depth、Locality、Seam placement 和迁移成本比较，最后给出明确推荐。不同方案确有互补价值时，可以提出 hybrid。
