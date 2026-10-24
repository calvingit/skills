---
schema_version: 4
id: T003
covers:
  requirements:
    - R1
  spec_acceptance:
    - AC1
referenced_design_decisions:
  - D1
  - D2
dependencies:
  - T001
---

# 运营 CLI 导出命令（复用 writer）

## Delivery

增加 ops CLI 导出命令：复用 CsvOrderWriter 把订单写出到本地文件路径参数，供脚本化对账；不改变 API 行为。含最小集成测试。

## Constraints

- 复用 CsvOrderWriter，不得复制其转义与金额格式逻辑（D2）

## Delivery Acceptance

- **AC1** — CLI 导出的文件内容与 API 导出同规则（转义 / 空值 / 金额 / BOM）
