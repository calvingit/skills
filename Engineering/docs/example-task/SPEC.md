# 订单导出 CSV

## Problem

运营目前只能在后台一页页翻订单、手工抄表，无法批量拿到表格数据做对账。

## Requirement Authority

- Mode: repository
- Source: 会话确认（2026-10-24，运营方提出并确认表头与文件名）
- Snapshot boundary: 本会话输入
- Unverified: None

## Goal

运营可以在后台把订单导出为 CSV 文件，并可按下单时间范围过滤。

## Scope

后台 HTTP 导出接口与页面入口；包含时间范围过滤。不包含其他筛选维度、异步任务和权限模型变更。

## Requirements

1. **R1** — 运营人员调用导出接口，得到包含订单号、下单时间、金额、状态的 CSV 文件。
2. **R2** — 导出可按下单时间范围（from/to）过滤；参数非法时返回明确的字段级错误，不产生文件。

## Business Constraints

- 金额格式与后台列表一致：分转元、两位小数（MoneyFormatter）。来源：运营确认。
- 文件编码 UTF-8 with BOM（Excel 兼容）。来源：运营确认。

## Acceptance Seams

- `GET /admin/api/orders/export` 响应体（text/csv 附件）— R1 / AC1 / AC2
- 同接口查询参数 `from`、`to` — R2 / AC3

## Acceptance Criteria

- **AC1** — Covers: R1. 导出响应为 CSV，表头固定为 `order_id,created_at,amount,status`，每行对应一笔订单，字段含义与后台列表一致。Expected source: 运营确认的表头清单。
- **AC2** — Covers: R1. `Content-Disposition` 文件名为 `orders-<yyyyMMdd>.csv`，编码 UTF-8 with BOM。Expected source: 业务约束。
- **AC3** — Covers: R2. `from`/`to` 均为合法 ISO 8601 时间时，仅返回该范围内订单；任一参数非法时返回 400 与字段级错误信息。Expected source: R2。

## Out of Scope

- 其他筛选维度（状态、渠道等）
- 异步 / 分页导出
- 权限模型变更

## Open Questions

- None
