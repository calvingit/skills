---
name: codex-reviewer
description: 只要用户提到 codex、Codex CLI、codex exec、codex resume，或者想用 AI 命令行工具分析、重构、自动编辑代码，就使用此技能。也适用于"继续上次的 codex 会话"、"让 codex 帮我改代码"等场景。
---

# Codex 技能指南

## 默认模型

- 固定使用 `gpt-5.5`，不要再询问或推荐其他模型。
- 推理力度默认用 `medium`。延迟敏感任务可用 `low`；复杂、多步、工具密集的编码任务可用 `high`；只有最难的异步代理任务或边界评测才用 `xhigh`。
- 不要假设推理力度越高越好。只有任务复杂度或用户明确要求支持时才升级。

## 执行任务

1. 判断任务是否需要写文件或联网：只读分析默认 `--sandbox read-only`；需要本地修改用 `--sandbox workspace-write --full-auto`；需要网络或广泛权限用 `--sandbox danger-full-access --full-auto`。
2. 组装命令：
   - `-m gpt-5.5`
   - `-c model_reasoning_effort=<low|medium|high|xhigh>`
   - `--sandbox <read-only|workspace-write|danger-full-access>`
   - `-C <DIR>`（需要切换目录时）
   - `--skip-git-repo-check`
   - `"你的提示词"`（最后一个位置参数）
3. 始终加 `--skip-git-repo-check`。
4. 默认在所有 `codex exec` 命令末尾加 `2>/dev/null` 以屏蔽思考 token（stderr）。只有用户明确要求查看，或需要调试时才去掉。
5. 执行命令，捕获输出，向用户总结结果。
6. Codex 完成后，告知用户：`随时可以说 "codex resume" 继续这个会话，或者让我继续分析和修改。`

### 快速参考

| 场景 | 命令 |
| --- | --- |
| 只读分析 | `codex exec -m gpt-5.5 -c model_reasoning_effort=medium --sandbox read-only --skip-git-repo-check "提示词" 2>/dev/null` |
| 本地写文件 | `codex exec -m gpt-5.5 -c model_reasoning_effort=medium --sandbox workspace-write --full-auto --skip-git-repo-check "提示词" 2>/dev/null` |
| 需要网络或广泛权限 | `codex exec -m gpt-5.5 -c model_reasoning_effort=high --sandbox danger-full-access --full-auto --skip-git-repo-check "提示词" 2>/dev/null` |
| 切换到其他目录 | `codex exec -m gpt-5.5 -c model_reasoning_effort=medium -C <DIR> --sandbox read-only --skip-git-repo-check "提示词" 2>/dev/null` |

## 继续会话

继续时通过 stdin 传入新提示词：

```bash
echo "新的提示词" | codex exec --skip-git-repo-check resume --last 2>/dev/null
```

`resume` 会自动沿用原会话的模型、推理力度和沙箱设置，不要再传入配置标志，除非用户明确要求更换。

## 编写给 Codex 的提示词

根据 OpenAI 的 `gpt-5.5` 官方提示词指南，提示词应短、目标明确，避免把旧模型需要的过程型脚手架原样搬过来。

- **结果优先**：说明要达成什么、成功标准、约束、可用证据、最终输出形态。不要写不必要的逐步流程，除非路径本身是产品要求。
- **停止条件清晰**：说明什么时候可以回答、什么时候必须继续检查、缺少关键证据时只询问最小必要信息。
- **工具任务先给简短进度**：多步或工具密集任务开始前，让 Codex 先发 1-2 句可见说明，说明已理解请求和第一步。
- **格式按需指定**：普通回答默认自然简洁；需要稳定产物时再指定表格、JSON、章节、字数或字段。
- **检索有预算**：要求 Codex 用足够证据回答核心问题后停止，不为润色、非必要例子或可泛化措辞重复搜索。
- **编码任务必须验证**：要求 Codex 修改后运行最相关的验证，例如目标单测、类型检查、lint、构建或最小烟测；不能运行时说明原因和替代检查。
- **复用和验收要写明**：复杂编码任务要明确复用现有代码、不要无关重构、验收标准、测试期望、何时继续、何时向用户求助。

示例提示词骨架：

```text
你在 <项目目录> 工作。目标：<要完成的结果>。

约束：
- 只改与目标直接相关的文件
- 复用现有模式，不新增不必要抽象
- 不处理无关历史问题

成功标准：
- <可验证标准 1>
- <可验证标准 2>

验证：
- 修改后运行 <具体命令>
- 如果无法运行，说明原因并给出下一步可执行检查

输出：
- 简要说明改了什么
- 列出验证结果
- 列出仍需用户处理的阻塞项
```

## 批判性评估 Codex 输出

Codex 由 OpenAI 模型驱动，有自己的知识截止日期和局限性。把 Codex 当同事，不是权威。

- 如果 Codex 说了你确定有误的东西，直接指出来。
- 近期发布的版本、API 变更，优先查官方文档验证。
- 特别注意模型名称与能力、库版本或 API 变更、已更新的最佳实践。

### 如果 Codex 判断有误

1. 向用户说明分歧所在。
2. 给出依据。
3. 需要时 resume 会话与 Codex 讨论。自我介绍用真实模型名，例如：

```bash
echo "这里是 Claude Code，我对 [X] 有不同看法，原因是 [依据]。你怎么看？" | codex exec --skip-git-repo-check resume --last 2>/dev/null
```

## 错误处理

- `codex --version` 或 `codex exec` 非零退出时，停下来报告，等用户指示再重试。
- 遇到参数错误或其他未知错误时，调用 `codex --help` 获取最新参数列表和用法说明。
- 使用高风险标志（`--full-auto`、`--sandbox danger-full-access`、`--skip-git-repo-check`）前，先在回复中征得用户同意，除非已经授权过。
- 输出含警告或结果不完整时，摘要说明情况，请用户告知如何调整。

## 官方依据

- https://developers.openai.com/api/docs/guides/latest-model
- https://developers.openai.com/api/docs/guides/prompt-guidance?model=gpt-5.5
