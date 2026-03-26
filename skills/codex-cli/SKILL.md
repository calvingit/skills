---
name: codex-cli
description: 当用户要求运行 Codex CLI（codex exec、codex resume）或提及 OpenAI Codex 进行代码分析、重构或自动编辑时使用。默认使用 GPT-5.4 模型，提供最先进的软件工程能力。
---

# Codex 技能指南

## 执行任务
1. 默认使用 `gpt-5.4` 模型。通过 `AskUserQuestion` 询问用户使用哪种推理强度（`xhigh`、`high`、`medium` 或 `low`）。用户可按需切换模型（参见下方「模型选项」）。
2. 根据任务需求选择沙箱模式；默认使用 `--sandbox read-only`，除非需要编辑文件或网络访问。
3. 使用以下选项组装命令：
   - `-m, --model <MODEL>`
   - `--config model_reasoning_effort="<high|medium|low>"`
   - `--sandbox <read-only|workspace-write|danger-full-access>`
   - `--full-auto`（等同于 `--sandbox workspace-write --ask-for-approval on-request`）
   - `-C, --cd <DIR>`
   - `--add-dir <PATH>`（授予额外目录写权限，可重复使用）
   - `-i, --image <PATH>`（附加截图或设计稿）
   - `--json`（exec 模式输出 JSONL 事件流）
   - `-o, --output-last-message <PATH>`（将最终回复写入文件）
   - `--search`（启用实时 Web 搜索，默认为缓存模式）
   - `--skip-git-repo-check`
4. 始终使用 --skip-git-repo-check。
5. 继续上一个会话时，使用 `codex exec --skip-git-repo-check resume --last` 或指定会话 ID `codex exec resume <SESSION_ID>`。Resume 支持全局标志（如 `--model`、`--sandbox`），按需传入。新提示可通过参数或 stdin 传递：`codex exec --skip-git-repo-check resume --last "继续修复" 2>/dev/null`。加 `--all` 可搜索所有目录的会话。所有标志必须插入在 exec 和 resume 之间。
6. **重要**：默认在所有 `codex exec` 命令后追加 `2>/dev/null` 以抑制思考 token（stderr）。仅在用户明确要求查看思考 token 或需要调试时才显示 stderr。
7. 运行命令，捕获 stdout/stderr（按需过滤），并向用户总结执行结果。
8. **Codex 完成后**，告知用户："你可以随时通过说 'codex resume' 或要求我继续分析或修改来恢复此 Codex 会话。"

### 快速参考
| 使用场景 | 沙箱模式 | 关键标志 |
| --- | --- | --- |
| 只读审查或分析 | `read-only` | `--sandbox read-only 2>/dev/null` |
| 应用本地编辑 | `workspace-write` | `--sandbox workspace-write --full-auto 2>/dev/null` |
| 允许网络或广泛访问 | `danger-full-access` | `--sandbox danger-full-access --full-auto 2>/dev/null` |
| 恢复最近会话 | 继承原始设置（可覆盖） | `codex exec --skip-git-repo-check resume --last "prompt" 2>/dev/null`（支持 `--model`、`--sandbox` 等全局标志） |
| 从其他目录运行 | 根据任务需求选择 | `-C <DIR>` 加其他标志 `2>/dev/null` |

## 模型选项

### 推荐模型

| 模型 | 定位 | 说明 |
| --- | --- | --- |
| `gpt-5.4` | **旗舰模型**（默认） | 融合 GPT-5.3-Codex 的编码能力与更强的推理、工具调用和智能体工作流 |
| `gpt-5.4-mini` | **轻量高效** | 快速、低成本，适合日常编码任务和子智能体 |
| `gpt-5.3-codex` ⭐ | **专业编码** | 业界领先的编码模型，其能力已融入 GPT-5.4 |
| `gpt-5.3-codex-spark` | **极速迭代**（研究预览） | 纯文本模型，近乎实时的编码迭代，仅限 ChatGPT Pro 用户 |

大多数任务直接使用 `gpt-5.4`。需要更快速、低成本时选择 `gpt-5.4-mini`。

### 推理强度级别

- `xhigh` - 超复杂任务（深度问题分析、复杂推理）
- `high` - 复杂任务（重构、架构设计、安全分析、性能优化）
- `medium` - 标准任务（代码组织、功能添加、Bug 修复）
- `low` - 简单任务（快速修复、格式化、文档编写）

## 后续跟进
- 每次执行 `codex` 命令后，立即使用 `AskUserQuestion` 确认下一步操作、收集澄清信息，或决定是否恢复会话。
- 恢复方式：`codex exec resume --last "新提示" 2>/dev/null`。恢复的会话默认沿用原始模型和沙箱设置，也可通过 `--model`、`--sandbox` 覆盖。
- 使用 `codex fork --last` 可从历史会话分叉出新线程，保留原始上下文。
- 在提议后续操作时，重申所选的模型、推理强度和沙箱模式。

## 错误处理
- 当 `codex --version` 或 `codex exec` 命令以非零状态退出时，立即停止并报告失败；在重试前请求用户指示。
- 在使用高影响标志（`--full-auto`、`--sandbox danger-full-access`、`--skip-git-repo-check`）之前，通过 AskUserQuestion 征求用户许可，除非已获得授权。
- 当输出包含警告或部分结果时，总结这些信息并通过 `AskUserQuestion` 询问如何调整。

## 其他实用功能
- **图片输入**：`codex -i screenshot.png "解释这个错误"` 附加截图辅助分析。
- **Web 搜索**：默认使用缓存搜索；`--search` 启用实时搜索；`-c web_search="disabled"` 关闭。
- **代码审查**：交互模式中使用 `/review` 对 diff 进行代码审查。
- **JSON 输出**：`codex exec --json` 输出 JSONL 事件流，便于 CI/脚本集成。
- **MCP 集成**：通过 `codex mcp add/list/remove` 管理 MCP 服务器，在 `~/.codex/config.toml` 中配置。
- **模型切换**：会话中使用 `/model` 命令，或在 `~/.codex/config.toml` 中设置默认模型。