# Graph Workflow 与 Runtime 的职责

Graph Workflow 是由当前 Agent 作为 Manager 执行的多 Agent 工作流 Skill。当前 Runtime 提供 subagents、等待、中断和会话恢复。Skill 内的状态脚本仅辅助维护 tickets 和交付进度，不启动外部 Agent CLI，也不管理 provider、进程、会话、heartbeat 或结果解析。

| 部件 | 职责 |
| --- | --- |
| Graph Workflow Manager | 准备任务上下文、派发 worker、判断 ticket 完成和最终交付 |
| Runtime | 创建、等待、中断和恢复原生 subagents |
| ticket-implement / verify / code-review | 分别负责实现及本地检查、最终独立验证和最终独立审查，返回可读文本或 Markdown |
| skill 内状态脚本 | 图查询、依赖与需求绑定检查、状态写入、事务恢复、最终交付快照 |

Graph Workflow 直接读取审查结果字符串并根据内容作判断，脚本不解析标题、严重性或通过措辞。JSON 仍用于确定的状态字段和命令输入，这不要求 subagent 返回 JSON。ticket 的 `complete` 命令表达 Graph Workflow 对本地验收的批准，最终交付的 `approved` 是 Graph Workflow 对独立报告与证据的明确判断，不是从报告中自动提取的结果。

## 执行上下文与委派

一次 Graph Workflow run 是逻辑上的 execution session。Manager 负责连续编排 tickets，所有实现和修正 attempt 都由 Runtime 原生 worker 执行，worker 上下文可按连续性需要复用或更换。Manager 通过状态命令写入 `.loop/state.json` 运行状态，worker 修改产品代码但不修改上游需求、tickets 或 Git 历史。

交接时提供当前任务、attempt、权威来源、基线、已有改动、验证入口和资源范围。优先复用已有上下文，必要时在任务 `.loop/` 中写简短的来源摘要，不强制 context 文件对、性能台账或另一套会话状态。摘要不替代代码、SPEC、技术方案和 ticket。复用同一 worker 时仍要重新交代当前 ticket、attempt、写入范围、验收来源和磁盘上已有的其他 ticket 变更，各 ticket 的 scope 与证据不合并。

普通实现必须委派给 Runtime 原生 worker，默认串行：同一时间最多一个实现 worker，并优先复用同一 worker 的上下文。并行只在用户明确要求 swarm 时使用，且必须来自当前 ready frontier、无直接依赖、写入范围不重叠、共享构建缓存/测试进程/外部可变资源无冲突、无未决共享技术契约；不满足条件的 ticket 等下一轮。串行与 swarm 共用同一套 Frontier、Lifecycle、Authority、Evidence、Delivery Snapshot 与收尾要求，模式不改变契约或验收标准。交接输入见[委派说明](../skills/graph-workflow/references/context-and-delegation.md)。

## 状态脚本与部署

| 目录 | 职责 |
| --- | --- |
| `Engineering/skills/to-tickets/scripts/` | 创建、校验、按上游变更协调执行图，以及 v3 任务的一次性本地转换 |
| `Engineering/skills/graph-workflow/scripts/` | 查询可执行任务、记录 attempt、状态流转和最终交付快照 |
| `Engineering/skills/shared/` | ticket 契约与 runtime state schema、图校验、文件锁、事务与恢复 |

使用 Python 3.10+，当前文件锁实现支持 macOS/Linux。没有第三方 Python 包、Codex 或 Claude Code 依赖，最终代码快照检查需要 Git。安装或复制相关 skill 时须保留兄弟目录 `shared/`，仅复制单个 SKILL.md 不足以运行脚本。脚本通过自身位置加载共享代码，调用时不要求当前目录位于 Skills 仓库。

从本仓库根目录调用的例子：

```bash
python3 Engineering/skills/to-tickets/scripts/create-graph create-batch /path/to/task --input /path/to/request.json
python3 Engineering/skills/to-tickets/scripts/validate-graph /path/to/task
python3 Engineering/skills/graph-workflow/scripts/frontier /path/to/task
python3 Engineering/skills/graph-workflow/scripts/update-status start /path/to/task T001 --input /path/to/start.json
python3 Engineering/skills/graph-workflow/scripts/update-status complete /path/to/task T001 --input /path/to/complete.json
```

输入定义见 [建图与协调](../skills/to-tickets/references/script-inputs.md)、[执行状态](../skills/graph-workflow/references/script-inputs.md)。

`.loop/` 仍位于任务目录，与 `SPEC.md`、`tickets/` 同级，并带有自己的 `.gitignore`：`state.json` 保存当前执行进度，报告、命令记录和交付输入也放在这里。现有图锁和临时事务目录也按任务隔离。脚本不建立项目级共享运行状态，也不支持跨机器或云端同步。

将示例中的 Skill 路径替换为已安装 Skill 的绝对路径，任务目录包含 SPEC 和 `tickets/*.md`。ticket 是稳定交付契约，执行状态在 `.loop/state.json`：读取时两者自动合并，写入时普通状态变化只替换该文件，涉及契约的协调（create / reconcile / migrate-v3）则在一个事务内同时切换契约与状态。v4 不兼容 v3 存储，也不读取旧 JSON Ticket：v3 任务用 `create-graph migrate-v3` 一次性本地转换，v2 任务在旧工具链执行完成并归档后再采用；可选的 ACCEPTANCE 和技术方案（`SOLUTION.md`）不作为额外前置要求。所有状态写入（start / retry / block / unblock / complete / reopen）、事务恢复和最终交付都走 `update-status`，每次写入都返回更新后的图，Graph Workflow 直接用它决定下一张 ticket，不必再跑一次 `frontier`。各输入的必需字段与示例由上面的参考资料维护。

正常状态流转是 open → in_progress → done，ready / blocked 是计算结果，`superseded` 由需求协调产生。Graph Workflow 在执行期间写运行状态，不重写 ticket、worker 不写票据。默认串行，只有用户明确要求才用 swarm；`start` 在没有 `mode: swarm` 时拒绝第二个并行 attempt。ticket complete 表示 Graph Workflow 已确认全部本地 AC 有充分证据、本地检查实际成功，且没有未解决的阻断问题或必需的未验证范围，实际 review 原文可选。ticket done 不代表最终交付通过。

`.loop/state.json` 是当前进度的唯一来源，不进入 Git。tickets 存在而该文件丢失或不可读时，图会以 `missing_runtime_state` / `invalid_runtime_state` 停止，不会把已完成的 ticket 当作未执行；只有用户明确确认进度已丢失后，才用 `update-status init-state` 重新初始化（全部 ticket 回到 open、无证据）。

本地检查由实现者记录实际命令、退出码、摘要和未验证范围，Graph Workflow 核对原始证据并决定状态，不重复执行 worker 的命令。状态脚本不能证明命令确实运行过或文字中没有阻断问题，真实性由 Graph Workflow 判断。

## 等待与执行恢复

创建、等待、取消、超时和会话恢复遵循 Runtime 能力及调用方配置，Graph Workflow 不设置默认无活动时限，不维护 soft-ping 次数或活动时间台账。等待窗口结束只表示尚未取得结果，不能据此认定失败或停止。

恢复执行前检查原生执行状态，确认旧 writer 和相关命令停止后才开始重叠工作，保留部分修改。结果绑定其原 attempt 和候选版本，迟到报告不能覆盖不适用的新结论，无法确认停止时报告阻塞。最终独立 verify 或 code-review 报告缺失时保持未完成，只有明确授权的替代才可改变执行者，并保留授权和覆盖证据。ticket 的本地检查不得声称为独立验证。

## 需求变更与恢复

修改共享需求前，Graph Workflow 先停止派发，通过 Runtime 中断 subagents 并确认它们停止写入，保留部分结果，再 block 当前 attempts。脚本改变状态不会终止运行中的 Agent。

需求、设计、图分别由 to-spec、solution-design、to-tickets 更新。`stale_authority` 表示旧证据需要影响分析，历史 done 仍保留。仅对确认未受影响的契约及证据使用 `retain_contract`，变更行为通过修正/替换 tickets 表达，不以 reopen 冒充需求修订。

脚本保留图校验、锁、事务和 `scripts/update-status recover`，拒绝过期 attempt、未知 AC、非法依赖或未协调的需求。Runtime 中断后，Graph Workflow 根据原生任务状态和记录继续，不通过脚本重建 Agent 会话。

## 最终交付

`all_active_done` 是历史状态，`delivery_ready` 表示可以开始整体验收。Graph Workflow Manager 按 closeout-roles 的风险分级委派专用 `simplify` worker（低风险层级可省略并记录）并准备最终快照，再分别调用独立 verify 和 code-review（交付脚本强制非空 review），代码停止变化后才能验收。必要修正通过图允许的 reopen 或修正 ticket 处理，保存原报告后更新快照，默认转入 targeted closeout：独立重验受影响 SPEC AC、原 regression 和项目 mandatory gates，独立审查累积修正及相关路径，确认其余证据仍适用。只有实际影响扩大、原 broad review 依据失效时才升级 broad review，不因再次 delivery_ready 自动重跑全套收尾。缺少任何必需结果时保留已完成 tickets，恢复未完成的最终验收，不能将最终交付标为 passed。完整步骤见[最终验收](../skills/graph-workflow/references/delivery-review.md)。完成后记录判断：

```bash
python3 <graph-workflow-skill>/scripts/update-status delivery-prepare <task-dir> --workspace <repo-root>
python3 <graph-workflow-skill>/scripts/update-status delivery-complete <task-dir> --input <task-dir>/.loop/delivery-input.json
python3 <graph-workflow-skill>/scripts/frontier <task-dir>
```

最终输入以 ticket 的 complete 格式为基础，将 `expected_attempt` 换成 prepare 返回的 `snapshot`，`evidence` 覆盖当前 SPEC 的所有 AC，并额外提供 `approved: true`、`unverified: []` 和 `review`。`review` 是最新独立审查的原始字符串；targeted report 引用保留的 broad report/候选，说明定向范围、finding 处理与原审查覆盖的适用性。ticket review 可选也不会降低这个要求。

快照记录当前需求、完整 ticket 契约（frontmatter 与正文）、当前运行状态、Git HEAD、文件内容/模式/链接和子模块代码，覆盖新增、未跟踪和删除的文件。仅当前任务的 `.loop/` 排除在文件扫描之外，用于进度、报告及完成输入；追加报告或命令记录不会让候选失效，而 reopen、重写证据或改契约正文会。`.loop/` 不放需求、产品代码、测试或必要配置，也不要将最终验收记录写回已完成 ticket。无法读取的子模块不允许生成完整快照。代码、需求或图变动使原结论失效，外部服务变化由 Graph Workflow 重新判断证据适用性。

## 仓库验证

仓库根目录执行 `python3 Engineering/skills/shared/check.py`，检查契约与运行状态分离、状态流转、需求协调、交付快照、串行/swarm 派发约束、CLI 和脱离仓库工作目录的脚本调用。不测试或承诺外部 Agent CLI、生产副作用、原生 Runtime 自身的会话恢复与持续运行。

Runtime 行为需真实工作流证据。
