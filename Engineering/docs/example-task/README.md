# 全链示例：订单导出 CSV

一个从需求到交付的样例任务目录，展示主链路各环节的真实产物形态。`tickets/` 由 `to-tickets` 的 `create-graph create-batch` 实际写入，`loop-state.example.json` 是 `graph-workflow` 的 `update-status` 在 T001 完成、T002 开始后的真实状态导出——不是手写示意。真实任务里运行态存放在任务目录的 `.loop/state.json`（Git 忽略），这里改名放在文档目录供查阅。

## 链路回放

1. **grilling** — 未收敛点（表头清单、文件名格式、Excel 兼容）经一轮 frontier 提问确认；本例决策在会话内确认，未建 session 目录。
2. **to-spec** — 确认后写入 [SPEC.md](SPEC.md)：R / AC 全覆盖、AC 各自可判定，Acceptance Seams 指向公开观察面（`GET /admin/api/orders/export`）。
3. **solution-design** — 三个需要多个实现共享的决策 D1–D3（writer 流式、转义/金额规则内聚、时间解析复用）落在 [SOLUTION.md](SOLUTION.md)；Design Review Gate 未触发（无新公共抽象、无长期方向分叉）。`to-spec` 消费其返回后推荐 Tickets 路线。
4. **to-tickets** — 三张票：T002（时间过滤）与 T003（CLI 复用 writer）都只依赖 T001（writer 契约在第一条端到端票落地），没有横向“先建所有接口”的预备票。见 [tickets/](tickets/)。
5. **graph-workflow** — T001 `start`（记录 baseline 与 allowed_write_scope）→ `complete`（evidence 逐 AC 带 result/summary，verification 带真实命令与退出码）→ T002 `start`。此刻 frontier 只剩 T003，见 [loop-state.example.json](loop-state.example.json)。
6. **收尾** — 全部票 done 且 `delivery_ready` 后：`delivery-prepare` 固定快照 → 按风险分级收尾。本例有共享契约（D1–D3、T003 复用 writer），走默认 full 档：`simplify`（Review）→ 独立 `verify` 逐 SPEC AC 给 PASS / FAIL / NOT VERIFIED → 独立 `code-review`（交付脚本强制非空 review）→ `delivery-complete`。分级规则见 closeout-roles。

## 看什么

- ticket 正文是稳定交付契约，frontmatter 是机读事实；执行态（phase / attempt / evidence / baseline）只存在于 `.loop`，两处不混写。
- `complete` 的 evidence 形态：每条本地 AC 一个 `result: passed` 加事实性 summary；verification 记录命令、退出码与关键结果——完成声明可追溯到证据。
- ticket 本地 AC（如 T002 的 AC1）与 SPEC AC 是不同命名空间，经 `covers` 追溯上游。
- T003 复用 T001 落地的 writer 契约（D2），体现“共享契约落在第一条实际使用它的端到端票上”。

本目录的 state 与 tickets 是 `shared/tests/test_example_task.py` 的回归输入：改动这里或 ticket/state 的形状约定，测试会拦截漂移。
