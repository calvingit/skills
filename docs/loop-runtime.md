# Loop 与 Runtime 的职责

Loop 是由当前 Agent 执行的工作流 Skill。当前 Runtime 提供 subagents、等待、中断和会话恢复。Skill 内的状态脚本仅辅助维护 tickets 和交付进度，不启动外部 Agent CLI，也不管理 provider、进程、会话、heartbeat 或结果解析。

| 部件 | 职责 |
| --- | --- |
| Loop | 选票、交接、阅读结果、判断修复/阻塞/完成、继续下一项任务 |
| Runtime | 创建、等待、中断和恢复原生 subagents |
| implement / verify / code-review | 实现、验证、审查；返回可读文本或 Markdown |
| skill 内状态脚本 | 图查询、依赖与需求绑定检查、状态写入、事务恢复、最终交付快照 |

审查结果直接作为字符串使用。Loop 根据内容作判断；脚本不解析标题、严重性或通过措辞。JSON 仍用于确定的状态字段和命令输入，这不要求 subagent 返回 JSON。`approved` 是 Loop 对已读证据的明确判断，不是从报告中自动提取的结果。

## State commands

将 `<loop-skill>` 替换为已安装 skill 的绝对路径；目录依赖见[状态脚本说明](./workflow-scripts.md)。从目标仓库根目录运行，`<task-dir>` 包含 SPEC 和 `tickets/*.json`。可选 ACCEPTANCE/HLD 不作为额外前置要求。

- `python3 <loop-skill>/scripts/frontier <task-dir>`：查询图状态和最终交付状态。
- `python3 <loop-skill>/scripts/graph-query show <task-dir> <ticket-id>`：读取任务、当前 attempt 和已记录证据。
- `python3 <loop-skill>/scripts/update-status --help`：查看状态命令参数；写操作用 `--input <path|->` 接收 JSON。

正常状态流转是 open → in_progress → done；ready、blocked 是计算结果。`superseded` 由需求协调产生。Loop 在执行期间拥有状态写权限；subagents 不写票据。

`start` 输入：

```json
{
  "baseline": {"reference": "<actual commit or recorded baseline>", "staged": [], "unstaged": [], "untracked": []},
  "existing_changes": {"included": [], "excluded": []},
  "allowed_write_scope": ["src/"]
}
```

路径与既有改动必须由 Loop 实际检查，不能把示例空列表当成事实。`retry` 使用相同字段，另加 `expected_attempt` 和 `findings`（原始问题文本），原子校验 attempt 并递增编号。原始基线和排除的用户改动仍须保留供后续审查。

`complete` 输入：

```json
{
  "expected_attempt": 1,
  "evidence": {"AC1": {"result": "passed", "summary": "<observed result and evidence source>"}},
  "verification": [{"command": "<actual command>", "exit_code": 0, "summary": "<actual output>"}],
  "review": "<original Markdown report, unchanged>",
  "approved": true,
  "unverified": []
}
```

Loop 用 JSON 序列化器保存多行字符串，避免手工转义。脚本要求当前 attempt、全部本地 AC 的有效证据、实际成功的验证记录、非空 review、明确批准和空 unverified；不检查报告语言或格式。原文保存到 `execution.review`，重开时移除失效的当前审查。完整报告、命令日志和输入可保存在 `.loop/` 供交接。脚本无法判断文字中是否仍有阻断问题，也无法证明命令确实运行过，这些由 Loop 对原始证据负责。

`block` 输入为 `blocker`（category、reason、release_condition）和已接受的 `evidence`；类别为 requirement、design、dependency、environment、permission 或 external。`unblock` 需要 `release_evidence`，必须先核实释放条件。`reopen` 需要 `review_finding`、失效的本地 AC 列表 `invalidated_acceptance` 和 `upstream_unchanged: true`，只用于原需求下的缺陷。

## 需求变更与恢复

修改共享需求前，Loop 先停止派发，通过 Runtime 中断 subagents 并确认它们停止写入，保留部分结果，再 block 当前 attempts。脚本改变状态不会终止运行中的 Agent。

需求、设计、图分别由 to-spec、high-level-design、to-tickets 更新。`stale_authority` 表示旧证据需要影响分析；保留历史 done。仅对确认未受影响的契约及证据使用 `retain_contract`；变更行为通过修正/替换 tickets 表达，不以 reopen 冒充需求修订。

脚本保留图校验、锁、事务和 `scripts/update-status recover`，拒绝过期 attempt、未知 AC、非法依赖或未协调的需求。Runtime 中断后，Loop 根据原生任务状态和记录继续，不通过脚本重建 Agent 会话。

## Final delivery

`all_active_done` 是历史状态；`delivery_ready` 表示可以开始整体验收。Loop 用原生 verify / code-review subagents 完成后，记录其判断：

```bash
python3 <loop-skill>/scripts/update-status delivery-prepare <task-dir> --workspace <repo-root>
python3 <loop-skill>/scripts/update-status delivery-complete <task-dir> --input <task-dir>/.loop/delivery-input.json
python3 <loop-skill>/scripts/frontier <task-dir>
```

最终输入使用上面的 complete 格式，将 `expected_attempt` 换成 prepare 返回的 `snapshot`，`evidence` 覆盖当前 SPEC 的所有 AC。review 仍是原始字符串。

快照记录当前需求、图、Git HEAD、文件内容/模式/链接和子模块代码。`.loop/` 仅放进度和证据，不放产品代码。无法读取的子模块不允许生成完整快照。代码、需求或图变动使原结论失效；外部服务变化由 Loop 重新判断证据适用性。

## 验证范围

仓库根目录执行 `python3 engineering/shared/check.py`，检查状态流转、需求协调、交付快照、CLI、脱离仓库工作目录的脚本调用与迁移。不测试或承诺外部 Agent CLI、生产副作用、原生 Runtime 自身的会话恢复与持续运行。
