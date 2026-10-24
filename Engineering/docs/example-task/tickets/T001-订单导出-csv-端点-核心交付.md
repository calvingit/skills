---
schema_version: 4
id: T001
covers:
  requirements:
    - R1
  spec_acceptance:
    - AC1
    - AC2
referenced_design_decisions:
  - D1
  - D2
dependencies: []
---

# 订单导出 CSV 端点（核心交付）

## Delivery

在后台增加 GET /admin/api/orders/export：落地 CsvOrderWriter（转义 / 空值 / 金额 / BOM），端点按 id 序流式写出全部订单，响应带 text/csv 与 orders-<yyyyMMdd>.csv 文件名。含 writer 集成测试与接口契约测试（happy path）。

## Constraints

- 金额格式经 MoneyFormatter，不得在端点内另行格式化（D2）
- 不得整表载入内存，必须经 writer 流式写出（D1）

## Delivery Acceptance

- **AC1** — 导出响应为 CSV，表头 order_id,created_at,amount,status，行内容与后台列表一致（writer 集成测试与接口契约测试通过）
- **AC2** — Content-Disposition 为 orders-<yyyyMMdd>.csv，编码 UTF-8 with BOM
