---
name: codex-reviewer
description: 只要用户提到 codex、Codex CLI、codex exec、codex resume，或者想用 AI 命令行工具分析、重构、自动编辑代码，就使用此技能。也适用于"继续上次的 codex 会话"、"让 codex 帮我改代码"等场景。
---

# Codex 技能指南

## 执行任务

1. 在回复中向用户确认以下两点（一条消息里问完）：使用哪个模型（`gpt-5.5`、`gpt-5.4`、`gpt-5.4-mini`、`gpt-5.3-codex-spark`、`gpt-5.3-codex`，模型列表可能随版本更新，以官方文档为准），以及推理力度（`xhigh`、`high`、`medium`、`low`）。

2. 根据任务选择沙箱模式，默认用 `--sandbox read-only`，只有需要写文件或访问网络时才升级。

3. 组装命令，可用的选项：
   - `-m <MODEL>` 或 `--model <MODEL>`
   - `-c model_reasoning_effort=<xhigh|high|medium|low>`
   - `-s <read-only|workspace-write|danger-full-access>` 或 `--sandbox <...>`
   - `--full-auto`
   - `-C, --cd <DIR>`
   - `--skip-git-repo-check`
   - `"你的提示词"` （作为最后一个位置参数）

4. 始终加 `--skip-git-repo-check`。

5. 默认在所有 `codex exec` 命令末尾加 `2>/dev/null` 以屏蔽思考 token（stderr）。只有用户明确要求查看，或需要调试时才去掉。

6. 执行命令，捕获输出，向用户总结结果。

7. **Codex 完成后**，告知用户："随时可以说'codex resume'继续这个会话，或者让我继续分析和修改。"

### 快速参考

| 场景 | 沙箱模式 | 关键标志 |
| --- | --- | --- |
| 只读分析 | `read-only` | `--sandbox read-only 2>/dev/null` |
| 本地写文件 | `workspace-write` | `--sandbox workspace-write --full-auto 2>/dev/null` |
| 需要网络或广泛权限 | `danger-full-access` | `--sandbox danger-full-access --full-auto 2>/dev/null` |
| 继续上次会话 | 继承原会话 | `echo "提示词" \| codex exec --skip-git-repo-check resume --last 2>/dev/null` |
| 切换到其他目录 | 按任务定 | `-C <DIR>` 加其他标志 `2>/dev/null` |

---

## 继续会话

继续时通过 stdin 传入新提示词：

```bash
echo "新的提示词" | codex exec --skip-git-repo-check resume --last 2>/dev/null
```

resume 会自动沿用原会话的模型、推理力度和沙箱设置，**不要**再传入配置标志，除非用户明确要求更换。

---

## 批判性评估 Codex 输出

Codex 由 OpenAI 模型驱动，有自己的知识截止日期和局限性。把 Codex 当同事，不是权威。

- **相信自己的判断**。如果 Codex 说了你确定有误的东西，直接指出来。
- **有分歧时查资料**，用搜索或文档验证，然后通过 resume 把结论反馈给 Codex。
- **留意时效性**。近期发布的版本、API 变更，Codex 可能不知道。
- **特别注意这几类错误**：模型名称与能力、库版本或 API 变更、已更新的最佳实践。

### 如果 Codex 判断有误

1. 向用户说明分歧所在。
2. 给出依据（自己的知识、搜索结果、文档链接）。
3. 需要时 resume 会话与 Codex 讨论。自我介绍用真实模型名，例如：
   ```bash
   echo "这里是 Claude Code，我对 [X] 有不同看法，原因是 [依据]。你怎么看？" | codex exec --skip-git-repo-check resume --last 2>/dev/null
   ```
4. 以讨论而非纠错的方式表达，两边都可能有盲区。
5. 如果真的存在不确定性，让用户自己决定。

---

## 错误处理

- `codex --version` 或 `codex exec` 非零退出时，停下来报告，等用户指示再重试。
- 遇到参数错误获取其他错误时，调用`codex --help`获取最新的参数列表和用法说明，确认命令格式正确。
- 使用高风险标志（`--full-auto`、`--sandbox danger-full-access`、`--skip-git-repo-check`）前，先在回复中征得用户同意，除非已经授权过。
- 输出含警告或结果不完整时，摘要说明情况，请用户告知如何调整。