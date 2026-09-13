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

## 等待与执行恢复

每次原生子任务默认从派发起计时，执行预算为 **10 分钟（600 秒）**；用户或项目明确指定其他预算时沿用该值。Loop 在任务 `.loop/` 的现有记录中保留角色、句柄、attempt 或交付快照以及实际起止时间。单次等待窗口、命令自身的超时和子任务总预算分别处理：等待可以分成多个短窗口，窗口结束不能触发关闭，也不能重置或缩短总预算。没有可靠计时证据时，不宣称预算已耗尽。

未收到报告、没有 diff、无法查询状态或找不到本地进程，都不足以判定卡死。等待窗口结束后先查可用 Runtime 状态；尚未完成、没有新进度且预算未耗尽时，发送一次不中断工作的进度询问（软 ping），请求当前阶段、命令、已完成结果和阻塞原因。Runtime 显示 running 但没有新进度，以及状态未知，都适用；已有新进度时继续等待，保留之后询问的机会。已完成但结果未取得时，先获取原执行的报告。

每次子 Agent 执行最多一次软 ping，恢复上下文或再次进入未知状态都不重复发送。在现有 `.loop/` 记录中关联执行句柄、询问时间、请求和回复，或截至观察时未收到回复。按剩余预算给一个正常等待/状态查询周期作为响应机会，不增加 pong 截止时间，不续期。无回复仅表示缺少额外进度信息，不能否定 Runtime 已知的 running 状态，也不能触发关闭、重派或批准。Runtime 不支持运行中消息时记录限制，继续原有等待流程，不以中断代替询问，不阻塞验收。详细步骤以[等待与恢复规则](../engineering/loop/references/wait-recovery.md)为准。

预算耗尽或确有故障时，按上述恢复规则处理对应角色，不先额外发送软 ping。停止流程仍可请求部分结果，不受软 ping 次数限制；确认 Agent 和相关命令停止后再接管，保留部分修改，核对迟到报告对应的版本。判断同一次执行时同时考虑来源和时间，旧 running 状态不能覆盖较新的明确停止事实。verifier 活跃时不在同一环境重复运行相同检查。

必需的独立 verify 或 code-review 报告缺失时，阶段保持未完成，不能批准。主 Agent 补测只有在用户或项目明确授权替代时才能用于替代验收，且要保留授权依据、执行者和覆盖范围。`unverified` 记录未检查的范围；把流程缺口移到备注不构成批准依据。脚本检查 `approved` 等事实字段，无法证明报告的独立性。

## 需求变更与恢复

修改共享需求前，Loop 先停止派发，通过 Runtime 中断 subagents 并确认它们停止写入，保留部分结果，再 block 当前 attempts。脚本改变状态不会终止运行中的 Agent。

需求、设计、图分别由 to-spec、high-level-design、to-tickets 更新。`stale_authority` 表示旧证据需要影响分析；保留历史 done。仅对确认未受影响的契约及证据使用 `retain_contract`；变更行为通过修正/替换 tickets 表达，不以 reopen 冒充需求修订。

脚本保留图校验、锁、事务和 `scripts/update-status recover`，拒绝过期 attempt、未知 AC、非法依赖或未协调的需求。Runtime 中断后，Loop 根据原生任务状态和记录继续，不通过脚本重建 Agent 会话。

## Final delivery

`all_active_done` 是历史状态；`delivery_ready` 表示可以开始整体验收。Loop 按 simplify → verify → code-review 的顺序执行；simplify 改动代码或测试后，先重新准备快照，再进行后续验收。缺少任何必需结果时保留已完成 tickets，恢复未完成的最终验收，不能将最终交付标为 passed。完整步骤见[最终验收](../engineering/loop/references/delivery-review.md)。完成后记录判断：

```bash
python3 <loop-skill>/scripts/update-status delivery-prepare <task-dir> --workspace <repo-root>
python3 <loop-skill>/scripts/update-status delivery-complete <task-dir> --input <task-dir>/.loop/delivery-input.json
python3 <loop-skill>/scripts/frontier <task-dir>
```

最终输入使用上面的 complete 格式，将 `expected_attempt` 换成 prepare 返回的 `snapshot`，`evidence` 覆盖当前 SPEC 的所有 AC。review 仍是原始字符串。

快照记录当前需求、完整 ticket JSON、Git HEAD、文件内容/模式/链接和子模块代码，覆盖新增、未跟踪和删除的文件。仅当前任务的 `.loop/` 排除在快照之外，用于进度、报告及完成输入，不放需求、产品代码、测试或必要配置；最终验收记录不要写回已完成 ticket。无法读取的子模块不允许生成完整快照。代码、需求或图变动使原结论失效；外部服务变化由 Loop 重新判断证据适用性。

## 验证范围

仓库根目录执行 `python3 engineering/shared/check.py`，检查状态流转、需求协调、交付快照、CLI 和脱离仓库工作目录的脚本调用。不测试或承诺外部 Agent CLI、生产副作用、原生 Runtime 自身的会话恢复与持续运行。
