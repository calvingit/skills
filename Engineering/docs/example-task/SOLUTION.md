# 订单导出 CSV — Solution Design

## Context

- Specification: [SPEC.md](SPEC.md)
- Baseline: `a1b2c3d`（示例仓库固定点）
- Scope: R1 / R2（AC1–AC3）
- Unverified: None

## Current State

后台已有 `AdminOrderController#index`（分页 JSON）与 `OrderRepository`（支持时间范围查询）；金额渲染统一走 `MoneyFormatter`（分 → 元）。仓库内无 CSV 设施。参考实现：`app/controllers/admin/order_controller.rb#index`（Observed）。

## Solution

在 `AdminOrderController` 增加 `export` 动作，经新增 `CsvOrderWriter` 流式写出；时间过滤复用现有 `DateRangeParser`。不引入 CSV 第三方库：字段量小，转义规则内聚在 writer 一处。

## Design Decisions

- **D1** — 导出经 `CsvOrderWriter` 流式生成，接口不整表载入内存
  - Change: New
  - Reference: None（沿袭 `#index` 的分页遍历思路）
  - Related: R1 / AC1；`AdminOrderController#index` 现有分页流
  - Affected: `AdminOrderController`、`CsvOrderWriter`
  - Reason: 订单量上限未知，整表载入有内存风险；流式与现有遍历方式一致。
  - Trade-offs: 行序按 `id` 稳定排序；不引入外部 CSV 库。
  - Evidence: R1；Observed `OrderRepository#each_in_range`
  - Consequences: 实现方必须经 writer 写行，不得自行拼接字符串。
- **D2** — `CsvOrderWriter` 拥有转义、空值与金额格式规则
  - Change: New
  - Related: 业务约束；Observed `MoneyFormatter#format`
  - Affected: 全部导出实现（API 与 CLI）
  - Caller usage: `CsvOrderWriter.new(stream).tap { |w| w.write_header; orders.each { |o| w.write_row(o) } }.close`
  - Reason: 转义与金额格式在多处实现必然漂移。
  - Consequences: 新导出面只能复用 writer，不得复制其逻辑；空值写空串、金额一律经 `MoneyFormatter`。
- **D3** — 时间过滤复用 `DateRangeParser`，错误沿用现有 400 错误体
  - Change: Reuse
  - Reference: `app/services/date_range_parser.rb`
  - Related: R2 / AC3
  - Affected: `AdminOrderController#export`
  - Reason: 与列表接口解析行为一致，不新造解析器。
  - Consequences: 解析器不支持的格式按 400 报告，不静默放宽。

## Modules and Ownership

- `CsvOrderWriter`：拥有 CSV 转义、空值、金额格式与 BOM 写出；不拥有数据查询与响应决策。

## Interfaces / Contracts

- `CsvOrderWriter#write_header` / `#write_row(order)` / `#close`；构造注入输出流。写出后出错由调用方决定响应，writer 不吞异常。

## Verification Seams

- `CsvOrderWriter` 集成测试：转义 / 空值 / 金额 / BOM — 关联 D2、AC1、AC2
- `export` 接口契约测试：表头、文件名、时间过滤、400 错误体 — 关联 D3、AC1–AC3
