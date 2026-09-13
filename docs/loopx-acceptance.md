# 状态脚本验收边界

Skill 内的状态脚本只管理 tickets 和交付进度。Agent 的创建、等待、中断与会话恢复属于当前 Runtime；业务结果由 Loop 阅读并判断。

## 必须满足

- graph 查询和状态写入保留依赖、需求绑定、attempt、锁及事务校验。
- complete 要求当前 attempt、全部 AC 证据、成功验证、非空原始 review 字符串、调用方批准和空未验证范围。
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

以下场景用于工作流回放或静态规则审查；静态审查不证明 Runtime 实际行为。等待及终止的权威规则见 [Loop](../engineering/loop/SKILL.md) 和[恢复说明](../engineering/loop/references/wait-recovery.md)。

| 场景 | 预期 |
| --- | --- |
| 连续等待窗口结束；reviewer 没有 diff；状态未知 | 在原 10 分钟预算内继续等待或查询，不提前关闭或重复派发，不推断通道故障。 |
| 完成通知延迟；已发送进度询问 | 获取原执行结果，给询问留出响应机会。 |
| 明确命令失败或预算耗尽；写入 worker 取消 | 记录真实原因，确认停止后保留部分工作并恢复对应角色，无重叠执行。 |
| 替代执行开始后收到旧报告 | 按原执行与代码版本判断适用性，不覆盖新结论。 |
| 本地检查通过但缺少独立报告 | 不批准；有明确替代授权时保留依据和证据来源。 |
| tickets 已完成，最终角色无报告 | 保留 ticket 成果，最终验收仍未完成；无 simplify 报告不能视为无需简化。 |
| simplify 改动代码或测试 | 更新快照，后续 verify/review 使用新版本。 |

快照测试使用隔离 Git fixture：准备快照后新建/更新 `.loop/` 报告及文件形式的 completion input 不改变指纹，完成写入后仍有效；产品文件新增、修改、删除、未跟踪内容变化及需求变化使旧快照失效。脚本可拒绝空报告、未批准或失败的检查记录，但不验证文字报告的独立性。
