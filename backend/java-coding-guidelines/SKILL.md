---
name: java-coding-guidelines
description: "用于编写、修改或审查 Java 代码时，按项目约定和《Java 开发手册（黄山版）》检查编码规约。"
---

# Java Coding Guidelines

用于 Java 代码实现与审查。目标是让 Agent 按任务主题加载《Java 开发手册（黄山版）》中的相关章节，而不是把整本手册长期放进上下文。

## Source

参考来源是用户提供的《Java 开发手册（黄山版）》。PDF 附录标注版本号为 `1.7.1`，发布日期为 `2022.02.03`。

## Authority

规范优先级从高到低：

1. 当前任务的明确要求；
2. 当前仓库已有规范、架构约定、静态检查和格式化配置；
3. 《Java 开发手册（黄山版）》中的规约。

若 PDF 规约与项目现状冲突，不擅自为了“符合手册”进行大范围重构；优先保持项目一致性，并在确有影响时指出差异。

## Workflow

1. 先读取目标代码及相邻模块，确认项目现有写法和约束。
2. 根据任务涉及的主题，只加载对应 `references/` 文档；不要默认读取全部参考资料。
3. 实现任务时，只应用与本次改动直接相关的规约。
4. 审查任务时，保留 PDF 的【强制】、【推荐】、【参考】等级，不把建议级规则升级成无条件要求。
5. 修改后运行项目已有 formatter、lint、静态检查和相关测试；没有可用验证方式时明确说明。

## Load references on demand

按 PDF 原目录加载：

- 一、编程规约：`references/programming-conventions.md`
- 二、异常日志：`references/exception-and-logging.md`
- 三、单元测试：`references/unit-testing.md`
- 四、安全规约：`references/security.md`
- 五、MySQL 数据库：`references/mysql.md`
- 六、工程结构：`references/project-structure.md`
- 七、设计规约：`references/design-guidelines.md`

一次任务只读取实际需要的文件和章节。若项目自身已有更具体的规范，以项目规范为准。

## Boundaries

- 不机械执行规范，不把【推荐】或【参考】当成【强制】。
- 不因为规范检查扩大当前任务范围。
- 不为了规避某条规则引入额外抽象、依赖或无业务价值的代码。
- 不把本 Skill 当作 Java 语言、框架或 API 的事实来源；涉及 JDK、Spring、第三方库版本行为时，应查对应官方文档。
