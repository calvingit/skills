# Design It Twice

只有用户要求探索多个 Interface，或单一方案不足以形成可靠设计判断时使用。开始前读取 [SKILL.md](SKILL.md) 与 [DEEPENING.md](DEEPENING.md)。

## Process

1. 向用户说明所有候选必须满足的约束、依赖类别和 Seam。可以用最小代码草图帮助理解，但草图不是候选方案。
2. 在运行环境支持且用户授权并行 Agent 工作时，至少委派三个彼此独立的候选设计：
   - 最小 Interface：最多 1–3 个入口，优先 Leverage；
   - 最大灵活性：覆盖多个真实用例和扩展点；
   - 最常见调用方：让默认路径最简单；
   - 存在远程依赖时，可增加 ports-and-adapters 方案。
3. 每个候选必须给出 Interface、调用示例、隐藏在 Seam 后的 Implementation、依赖/Adapter 策略，并说明 Leverage 在哪里强、在哪里薄。
4. 依次展示候选，再按 Depth、Locality、Seam placement 和迁移成本比较，最后给出明确推荐。不同方案确有互补价值时，可以提出 hybrid。

无法使用独立 Agent 时，在当前会话中按相同约束分别生成候选，并避免让后一个方案只是前一个方案的改名版本。
