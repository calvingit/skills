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
