# 状态脚本验收边界

Skill 内的状态脚本只管理 tickets 和交付进度。Agent 的创建、等待、中断与会话恢复属于当前 Runtime；业务结果由 Loop 阅读并判断。

## 必须满足

- graph 查询和状态写入保留依赖、需求绑定、attempt、锁及事务校验。
- ticket complete 要求当前 attempt、全部本地 AC 证据、成功检查、调用方批准和空未验证范围；实际 review 原文可选。
- delivery-complete 仍要求最终独立 review、全部 SPEC AC 证据和有效快照；ticket done 只放行依赖。
- 审查字符串按原文存储，不解析标题、语言或严重性，不据此自动批准。
- 非法状态、缺少证据、过期 attempt、未协调需求或失效交付快照不得标为完成。
- 不提供 worker/provider/Agent CLI 命令，不启动 Agent 进程，不管理 session、heartbeat 或重试执行。
- `frontier` 和 delivery-prepare/complete 只查询或记录进度，不执行实现、测试或审查。

## 检查入口

从仓库根目录执行：

```bash
python3 engineering/shared/check.py
```

覆盖图状态、需求变更、任意 Markdown 原文存储、最终快照失效、CLI 参数错误和脱离仓库目录的脚本调用。Runtime subagent 行为由实际工作流验证，不用脚本测试代替。

## Loop 场景审查

以下场景用于工作流回放或静态规则审查；静态审查不证明 Runtime 实际行为。执行边界见 [Loop](../engineering/loop/SKILL.md)，原生执行生命周期遵循 Runtime。

| 场景 | 预期 |
| --- | --- |
| 共享模块的连续 tickets | 委派 native worker，可按实际能力复用上下文；每张 ticket 有独立 attempt 和全部本地 AC 证据。 |
| 真正独立的 tickets | 默认串行；并行前确认依赖、写入、共享设计及可变资源独立。 |
| Runtime 没有原生 subagent | 保持 Loop 未完成并报告阻塞，不回退到 Manager 自行实现。 |
| 最终审查发现已完成 ticket 的缺陷 | 按图约束 reopen 或创建修正 ticket，保留无关证据；修正后更新快照并重跑受影响验收。 |
| 连续等待窗口结束，未取得结果 | 使用 Runtime 原生状态/结果，不因窗口结束认定失败、停止或重复派发；不建立另一套超时协议。 |
| 中断、需求变更或替换写入 worker | 确认原 writer 和相关命令停止，保留部分修改后再接管；无法确认时保持阻塞。 |
| 替代执行开始后收到旧报告 | 按原 attempt 和候选版本判断适用性，不覆盖不适用的新结论。 |
| ticket 本地检查通过，最终独立报告缺失 | 可完成 ticket 并放行依赖；最终交付不可批准。 |
| 必需 AC 为 FAIL 或 NOT VERIFIED | 处理缺陷、契约或证据缺口，不能以其他绿色检查替代。 |
| tests / fixtures / snapshots / 验证配置变化 | 重新判断受影响证据，即使产品代码未变。 |
| tickets 已完成，最终角色无报告 | 保留已完成 tickets，最终验收保持未完成。 |
| simplify 改动代码或测试 | 更新快照，后续 verify/review 使用新版本。 |

快照测试使用隔离 Git fixture：准备快照后新建/更新 `.loop/` 报告及文件形式的 completion input 不改变指纹，完成写入后仍有效；产品文件新增、修改、删除、未跟踪内容变化及需求变化使旧快照失效。脚本可拒绝空报告、未批准或失败的检查记录，但不验证文字报告的独立性。
