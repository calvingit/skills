# loopx 验收协议 v1

本文件是 loopx 的完成门。修复、审查和发布只以本协议及其可执行检查为准，不通过临时增加审查范围来改变完成标准。

## 公开边界

- `worker` 只执行外部 prompt；不负责 implement、verify、review 编排。
- `loop` 负责 ticket、attempt、scope、handoff、retry、block、complete 和 completion gate。
- `graph` 负责 graph contract 与 lifecycle mutation。
- provider、model、session 和 raw output 不进入 ticket contract。

## 固定命令

```text
loopx version
loopx graph inspect <task-dir>
loopx loop status <task-dir>
loopx loop run <task-dir> --scope <path>
loopx worker run <workspace> --prompt <prompt>
loopx worker run <workspace> --provider <provider> --model <model> --prompt <prompt>
```

## 失败状态矩阵

| 输入/事件 | 结果 | 退出码 | 证据要求 |
| --- | --- | --- | --- |
| 空 prompt | contract error | 1/2（CLI 约定） | 无 provider 启动 |
| provider 未指定 | 当前 Runtime 或可用 provider | 0/失败 | routing reason |
| provider 不可用 | blocked/failed，字段完整 | 非 0 | 不泄漏 raw |
| 普通文本输出 | completed | 0 | text payload + artifact |
| malformed JSON | prompt mode 可作为文本 | 0 | artifact |
| provider 非零退出 | failed | 非 0 | raw 只进 artifact |
| SIGINT/heartbeat stale | interrupted | 非 0 | 有界清理 |
| workspace 不存在 | workspace_invalid | 非 0 | 不创建目录 |
| graph 缺少命令 | usage error | 2 | 标准 usage |
| graph command --help | usage | 0 | 不访问 task-dir |
| scope 越界 | rejected | 非 0 | graph 状态不被伪造完成 |
| completion gate 不满足 | 不得 done | 非 0 | 保留 evidence |

## 完成命令

从仓库根目录执行：

```bash
python3 tools/loopx/scripts/check.py all
```

该命令覆盖根目录测试、CLI 黑盒检查、compile/package smoke、干净虚拟环境安装和公开入口验证。真实 provider 的 live execution 仍需单独标记，不得用 fake provider 结果代替。
