---
name: claude-coder
description: 将具体的编码任务（实现功能、修复 Bug、重构、补充测试）委托给 Claude Code 子agent执行。
---

# Claude Coder

将当前仓库中的编码任务委托给 Claude Code CLI 子智能体执行，并汇总结果。

## 适用场景

- 需要在当前仓库中编写、修改或修复代码
- 任务足够具体，可在一次调用中完成（功能开发、Bug 修复、重构、单测）
- **不适用于**架构讨论、技术方案决策，或中途需要用户确认的任务

## 调用方式

先确定 skill 目录 `$SKILL_PATH`，再执行脚本：

```bash
bash "$SKILL_PATH/scripts/claude-coder.sh" "<任务描述>"
```

任务描述用**单个引号括起的字符串**传入，尽量包含文件路径、函数名和验收条件。

## 任务描述示例

合适：
- `"在 src/users/service.ts 的 createUser 函数中添加入参校验，拒绝空 email 和空 name"`
- `"修复 lib/paginate.go 分页逻辑中的差一错误"`
- `"为 config/parser.py 的 parseConfig 函数补充单元测试"`

过于模糊（调用前先澄清）：
- `"修一下那个 bug"`
- `"优化一下代码"`

## 调用后

读取脚本输出，向用户汇报：
- 改了什么、为什么改
- 验证结果（通过 / 失败 / 未执行）
- 遗留风险或后续建议

验证失败时，针对失败点继续修复，而非重跑整个任务。