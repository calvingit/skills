# loopx 验收协议 v1

本文件是 loopx 的完成门。修复、审查和发布只以本协议及其可执行检查为准，不通过临时增加审查范围来改变完成标准。

本文件只定义 loopx CLI 和运行时公开边界；任务验收按任务自身的 SPEC 和可选 ACCEPTANCE.md 执行。

## 公开边界

- `loop` 负责 ticket、attempt、scope、handoff、retry、block、complete 和 completion gate。
- `graph` 负责 graph contract 与 lifecycle mutation。

## 固定命令

```text
loopx version
loopx graph inspect <task-dir>
loopx loop status <task-dir>
loopx loop run <task-dir> --scope <path>
```

## 失败状态矩阵

| 输入/事件 | 结果 | 退出码 | 证据要求 |
| --- | --- | --- | --- |
| graph 缺少命令 | usage error | 2 | 标准 usage |
| graph command --help | usage | 0 | 不访问 task-dir |
| scope 越界 | rejected | 非 0 | graph 状态不被伪造完成 |
| completion gate 不满足 | 不得 done | 非 0 | 保留 evidence |

## 完成命令

从仓库根目录执行：

```bash
python3 tools/loopx/scripts/check.py all
```

该命令覆盖根目录测试、CLI 黑盒检查、compile/package smoke、干净虚拟环境安装和公开入口验证。
