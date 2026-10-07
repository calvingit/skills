# Kernel Migration Plan — 实施记录

冻结审计：667223419d70a33f3509663d71f8fd4df671c18d。接续实施基线：02e21c8f28bcdcb06dc758a1f17d133d5a4882e8。
规则台账见 [engineering-kernel-audit.md](engineering-kernel-audit.md)；最终不变量见 [ENGINEERING_KERNEL.md](ENGINEERING_KERNEL.md)。审计先分类，冻结源文件未修改；实施在独立工作树进行。

## Delete / Move / Merge / Automate / Simplify

| 动作 | 规则/问题与受影响 Skill | 结果 |
| --- | --- | --- |
| Delete | F01，project-audit prompts / principles：缺工具、数量阈值、历史不失败、snapshot/fallback 一概无效 | d289d78 已移除错误通用裁决；保留有效调查和可调整 severity 方法 |
| Delete | F02，codebase-design：新接口测试存在即删除全部旧测试 | 上游已修复；本轮统一入口与 DEEPENING 的 Adapter 数量判断，不删独有行为保护 |
| Move | PROJECT：AGENTS / Profile / 项目验证策略 | 保留具体仓库约定；不搬入 Kernel；通用 Skill 中“如何发现配置”仍是 METHOD |
| Move | RUNTIME：loop / quick-implement 的 worker 创建、等待、中断、恢复、上下文复用 | 已在现有 Runtime 层；方法仍保留调度前的工程条件与角色判断，不新增 runner 或 session 状态机 |
| Move | TOOLING：CLI、schema、fingerprint、锁、图事务与恢复 | 保留既有脚本/引用；schema 声明不冒称全部 CLI 已强制执行；不可达防御分支不作为现行授权机制 |
| Merge | 17 条跨 Skill 不变量 | 单一规范为 docs/ENGINEERING_KERNEL.md；AGENTS、职责说明、task-contract 导航统一；出现项映射在审计保留 |
| Merge | implement / verify / code-review / loop 共用 Evidence 族 | 只统一原则，不合并四种不同判断、角色停止点或证据要求；独立 Skill 安装的方法仍完整 |
| Automate | 格式、状态、依赖、锁与快照形式约束 | 既有 check.py / 手写 CLI / schema 各负责已实现范围；本轮不新增数百脚本、不用自动化代替授权与证据真伪判断 |
| Simplify | F03，debug：命令式 loop 与只读调查强度冲突 | 上游允许有标记的静态假设；本轮取消“无 loop 后续只能猜”的残留，明确 probe 需在授权内，并统一 escalation 引用中的修复门槛；保留修复前可区分证据及验证缺口 |
| Simplify | F04，quick-implement / loop 固定收尾角色 | 保留现行三角色；对照实验协议已存在，本轮没有据静态审计缩减角色 |
| Simplify | F05，verify-engineering state-tools | 已区分普通 ticket Manager 接受与 final delivery 显式 approved/unverified；不改字段或状态工具行为 |

已完成全部有明确依据的本轮迁移。MOVE 目标已正确的条目原位保留；DELETE 删错误裁决而非整个 Skill。没有确定的 OBSOLETE 删除，不为了台账分类重排全部仓库。

固定角色缩减属于另一项行为优化实验：[closeout-role-experiment.md](../.agents/skills/verify-engineering/references/closeout-role-experiment.md)。它需要真实局部、共享契约和 GUI 配对任务；本次四个独立 fixture 不能充当其 A/B 数据。现行门禁继续生效，未执行的对照不是已验证收益。

## 验证记录

- 冻结 181 文件 Git blob 校验；4951 条保留规则 ID/来源行范围/分类枚举/输入拆分对应关系/Kernel 来源关联通过。
- 候选：远端 02e21c8 加本轮受影响 docs、codebase-design 和 debug 修改；证据记录的是含未提交改动的候选，不能只用 Git HEAD 表示它。
- `PYTHONDONTWRITEBYTECODE=1 python engineering/shared/check.py`，工作目录为候选仓库：57 tests，6.608s，OK，exit 0。
- 已安装 skill-creator 的 quick_validate.py：codebase-design、debug 均 `Skill is valid!`；未修改 frontmatter 或 UI metadata 含义。
- `git diff --check` 通过；具体本地 Markdown 链接与锚点、YAML 元数据另作检查。
- 四个独立新上下文加载候选 Skill，收到原始 fixture 任务；不提供预期答案、审计结论或拟修复问题。原始输入与响应见下文。

静态/工具测试不证明真实 Runtime 加载与长期收益；文本 fixture 不证明产品服务、数据库、设备或 GUI 集成。没有创建外部 Agent CLI、生产写入、安装或凭据访问。

## 独立演练结果

| 场景 | 观察结果 | 限制 |
| --- | --- | --- |
| Debug，日志/代码可读但无运行环境 | 继续只读诊断并提出有标记、可证伪的机制；区分单 owner 字面契约与双成功响应语义 | 没有运行复现或修复，不把日志推断冒充验证 |
| 深模块与测试清理 | 单 Adapter 不能自动否定真实供应商边界；四类旧故障保护需逐项保留/迁移 | 只有题面，没有实际 BillingLedger 源码/测试执行 |
| 专项审计四片段 | 报金额单位违约、无界大 payload 两项；未把缺 race 工具或历史不失败算作缺陷 | 内存失败方式保留流式处理反证，没有压测 |
| verify，CLI 与真实付款两个 AC | 实际 CLI exit 0，AC1 PASS；真实服务不可用且无写授权，AC2 NOT VERIFIED | 本地替身不证明真实扣款或只扣一次 |

最终独立 code-review 未发现剩余必修项；它检查了来源摘要/计数/lineage、17 条不变量、受影响方法和 80 个具体相对链接，并如实限制其全台账语义抽样范围。发现的 Debug 引用门槛已在最终候选修复。

## 原始任务与结果（评估留存）

以下为独立执行记录；题面事实不是实际产品运行结果。路径和执行时间保留为本次评估上下文，复现时使用对应仓库的候选 Skill。

### debug

#### 原始输入

请用指定 Debug Skill 只读诊断，不修改文件。

用户问题：有时两次请求都报告领取成功。生产环境当前不可访问，无本地数据库或可执行服务；仅提供以下生产路径和日志。
已确认契约：一个资源同一时刻最多有一个 owner。

```python
def claim(db, resource, user):
    if db.read_owner(resource) is None:
        db.write_owner(resource, user)
        return {'claimed': True}
    return {'claimed': False}
```
数据库 read_owner / write_owner 各自是独立事务；write_owner 不带条件或唯一领取约束。
日志（同一 resource=R7）：
10:00:00.001 request A read_owner -> None
10:00:00.002 request B read_owner -> None
10:00:00.003 request A write_owner -> U1 committed
10:00:00.004 request B write_owner -> U2 committed
10:00:00.005 request A response claimed=true
10:00:00.006 request B response claimed=true

返回诊断、依据、未知范围和下一步。不要假称运行过命令。

#### 原始响应

诊断：所给记录支持“检查与写入不原子”的并发竞态。A、B 都在 owner 为空时完成读取，各自进入成功分支；随后两次无条件写入均提交，各自返回 `claimed=true`。B 的写入覆盖了 A 的 owner。这个交错足以解释本次两次成功响应，尚未在可运行环境中独立复现。

预期来源是已确认契约“一个资源同一时刻最多有一个 owner”；实际是同一资源 R7 的两个请求都报告成功。日志没有证明数据库同时保存了两个 owner：一个单值字段可能始终只有一个值。若成功响应表示取得这一轮排他领取，则两个成功响应与这一语义不一致；成功响应具体承诺什么、owner 何时失效，还需要确认，可用 `grilling` 澄清这部分契约。无需等待这一澄清，也能解释为什么当前路径会返回两次 true。

依据：

- `.001`、`.002`：两个请求均读到 `None`，因此均通过分支判断。
- `.003`、`.004`：U1、U2 的写入分别提交。独立事务和无条件写入之间没有“仍为空才成功”的保护。
- `.005`、`.006`：两个响应均为 true；该返回值取决于此前的读取，而非原子领取结果。

主假设：**受给定代码与日志支持，运行验证未完成**——两个请求在检查后到写入前互相穿插，导致重复成功。预测：在真实调用路径上控制两个请求先读到空值再继续写入，应出现两次 true；若改为数据库原子地判定“为空才写入”，并按该操作的结果返回成功，同一交错应只有一次 true。没有必要为这条记录添加额外原因；也没有测试证据可以排除其他事件中的缓存、重试或其他写入路径。

反馈循环尚未建立。生产不可访问，且没有本地数据库或可执行服务，无法运行真实入口测试、HTTP 请求或数据库重放。我只读取并分析了提供的路径和日志，未执行复现命令、模拟测试、探针或修复。记录中有一次失败事件，但没有请求总量，无法给出复现率。

未知范围：数据库类型、隔离级别、其他写入和释放路径、日志是否完整、成功响应语义、发生频率及后续影响。若无其他写入，B 提交后 owner 应为 U2；没有最终查询和后续操作记录，不能把更晚状态或损失范围写成事实。

下一步：确认排他领取的响应契约；获得同种数据库和真实 `claim` 入口的可执行环境，用同步屏障重现上述交错，断言同一轮最多一次成功，且成功者与持久化 owner 一致，同时检查串行首次领取成功、已占用时失败。若暂时只能补充生产证据，优先获取按这两个请求关联的事务记录和 owner 变化并脱敏，无需全面加日志。

若以后授权修复，应让数据库原子地完成“为空时领取”，成功响应取决于真正获得领取权的操作结果。具体条件写入或锁方案需根据数据库与生命周期确定；仅将读写包在一个普通事务中不能自动保证这一性质。本次只读诊断至此停止，产品代码和日志均未改变；任何修复、回归和生产验证都尚未完成。

#### 加载与执行记录

# Debug rerun receipt

## Sources loaded for this rerun

- `skills-work/engineering/debug/SKILL.md`, complete.
  SHA-256: `4105b8204622f45db6252494fc47f0f96c8152c9d3adfcf8bdacae6886aec1ac`
- `skills-work/engineering/debug/references/feedback-loop-escalation.md`, complete updated reference.
  SHA-256: `dafa3bdc77e73cd557bdf8ce8c35a8408fe84e6ebcc8fc5471ae5ce7280920c4`
- `audit-work/behavior/debug-input.md`, original raw task and supplied code/logs.

Skill-creator guidance was already loaded in the initial run. No audit reports or other conclusions were read. Prior response files were copied to `debug-output-v1.md` and `debug-receipt-v1.md` without loading them as diagnostic evidence.

## Actions actually executed

Source read and hash command:

```bash
cat skills-work/engineering/debug/SKILL.md; cat skills-work/engineering/debug/references/feedback-loop-escalation.md; cat audit-work/behavior/debug-input.md; sha256sum skills-work/engineering/debug/SKILL.md skills-work/engineering/debug/references/feedback-loop-escalation.md
```

This completed with exit code 0 and returned the requested sources and hashes. Preservation commands:

```bash
cp audit-work/behavior/debug-output.md audit-work/behavior/debug-output-v1.md
cp audit-work/behavior/debug-receipt.md audit-work/behavior/debug-receipt-v1.md
```

These completed with exit code 0. An attempted `apply_patch` replacement was rejected because delete/add operations targeted the same path; it made no changes. A Python file-write command then replaced only the designated response and receipt. No product/repository changes, instrumentation, runtime reproduction, regression checks, commit, or push were performed.

## Observations

The supplied independent read/write operations and logged interleaving support a check-then-write race explaining both true responses. This is recorded as supported artifact-based diagnosis, with empirical verification unavailable. The response distinguishes duplicate successful responses from simultaneously stored owners and identifies the missing success-response semantics. It provides a falsifiable real-path concurrent check and targeted evidence request. The updated reference permits useful read-only diagnosis from a distinguishing observation set; no unavailable execution is claimed, and no fix is executed or declared verified.

Final output: `audit-work/behavior/debug-output.md`.


### design

#### 原始输入

请用指定 codebase-design Skill 审查这次局部深模块方案，不修改文件。

BillingLedger 有一个生产 LedgerAdapter，封装供应商 SDK 的金额单位、错误码和事务顺序。暂无第二个实现，外部公开调用只使用 BillingLedger.charge/refund。
新接口测试覆盖 charge 成功、refund 成功（本地 provider 替身）；旧私有测试另覆盖供应商整数溢出、提交超时后查操作身份、refund 在 charge 未确认时拒绝、状态转换乱序。新测试尚未覆盖这些分支。
方案：合并内部三个模块为 BillingLedger，删除 LedgerAdapter port 和全部旧测试，只保留两个新接口测试。
要求判断接口/边界价值、测试保留或迁移依据和方案风险。

#### 原始响应

结论：可以合并内部三个模块，让 BillingLedger 的 charge/refund 成为统一调用接口；目前不支持同时删除 LedgerAdapter port 和全部旧测试。两条成功路径测试不足以替代四类独有的异常与不变量保护。

本次只判断 BillingLedger 这个局部模块的接口、供应商接缝及测试迁移，不扩展到全仓架构审查。

### 接口与边界价值

- **Observed（题面给定）**：生产调用者只使用 charge/refund；LedgerAdapter 隔离供应商金额单位、错误码和事务顺序；只有一个生产实现。
- **Inferred**：charge/refund 有形成深模块接口的条件，但接口不止方法名，还包括金额范围、失败语义、超时后的操作身份、charge/refund 顺序约束与状态转换。实际深度仍取决于调用者是否需要自行处理这些细节。
- **Inferred**：供应商是实际外部接缝。本地 provider 替身是测试手段，不会把供应商依赖变成“本地可替代”依赖。一个生产 Adapter 也能隔离真实复杂性，无需等待第二个实现来证明价值。
- **Unknown**：未提供源码，无法判断 port 的粒度是否合理、是否只是转发 SDK、核心是否泄漏供应商类型，以及三个模块是否确实适合合并。

删除测试：若绕过 LedgerAdapter 直接使用 SDK，金额换算、错误映射及事务顺序的理解成本会重新出现，那么 Adapter 正在提供价值。若只删 port 类型、保留私有 Adapter，这些价值不一定消失，但需证明依赖方向和可替换的内部接缝仍清楚。不能把“删 port”与“删 Adapter 的职责”混为一谈。

### 两个可行设计

| 设计 | 收益与成本 | 迁移及测试接缝 |
|---|---|---|
| **推荐：合并内部编排，保留私有稳定 port 与 LedgerAdapter** | BillingLedger 拥有账务不变量和流程；Adapter 隔离供应商协议。成本是保留一个有实际职责的内部接口。 | 外部仍是 charge/refund；组合入口注入生产 Adapter，测试注入替身。迁移唯一行为覆盖后再删重复旧测试。 |
| 保留模块组合，只统一对外入口 | 改动较小，适合尚未证明合并能改善局部性时；可能继续保留多层编排成本。 | 同样保留外部供应商接缝，先补行为测试，再按具体职责决定合并。 |

账务状态、charge 确认条件和 refund 规则应归 BillingLedger；供应商整数表示、SDK 错误映射及供应商事务协议应归 Adapter。port 应表达内部需要的稳定能力，不照抄整个 SDK，也不为了测试给 charge/refund 添加开关、回调或可变状态。

### 测试保留或迁移依据

| 旧覆盖 | 应保护的行为及迁移方式 | 当前决定 |
|---|---|---|
| 供应商整数溢出 | 输入触及供应商表示范围时，按既有契约失败，并避免错误金额的副作用。优先经 charge/refund 触发实际换算；若 provider 替身绕过生产换算，保留 Adapter 私有接缝测试。 | 保留，直到等价保护经验证存在。 |
| 提交超时后查询操作身份 | 通过接缝模拟提交结果不明及身份查询，验证既有返回/失败语义与副作用，避免回归为盲目重提。 | 迁移到 BillingLedger 接口测试；迁移完成前保留。 |
| charge 未确认时拒绝 refund | 经公开接口构造未确认场景，断言 refund 拒绝及无退款副作用。 | 迁移到接口测试。 |
| 状态转换乱序 | 模拟乱序供应商结果，经接口验证不接受非法状态或产生错误副作用；具体期待结果取自已有契约。 | 能观察则迁移；若只保护独有内部不变量，保留有价值的私有接缝测试。 |

不能按“私有测试”标签批量删除。逐项比较输入、可观察结果、失败模式、独有回归保护及反馈成本：等价迁移后删除重复测试；只锁定实现细节、无独有行为保护的测试可以删除；仍提供独有保护的测试继续保留。测试可以使用模块内部接缝，但不因此扩大生产公共接口。

当前方案的风险是丢失金额边界、超时恢复及状态不变量的回归保护，并可能把供应商协议带进核心。两个成功测试只能证明各自成功路径，不能证明上述分支安全。建议先确认所有权与既有契约，保留供应商接缝，补齐或迁移独有行为保护，再合并并删除已证实重复的测试。这里没有源码和测试运行证据，不能断言方案已引入某个实际缺陷，也不能证明保留原 port 原样就是最佳设计。

#### 加载与执行记录

# Validation receipt

## Loaded files

- skills-work/engineering/codebase-design/SKILL.md — read in full.
- skills-work/engineering/codebase-design/DEEPENING.md — read in full because dependency classification and test migration determine this local design judgement.
- audit-work/behavior/design-input.md — read in full as the requested task.
- File inventory under skills-work/engineering/codebase-design — names only. DESIGN-IT-TWICE.md was not loaded: the task did not request a distinct interface-comparison exercise and the main workflow plus DEEPENING provided sufficient guidance.

## Observations

- Task asks for a local BillingLedger design judgement and prohibits modifying repository files.
- Single production Adapter isolates vendor units, errors and transaction ordering.
- Public callers use charge/refund; only new success cases exist.
- Four old coverage categories are not represented by those new success cases.
- Response explicitly separates scenario observations, inference and unknown implementation facts.
- Response does not equate a local provider stand-in with a local-substitutable production dependency.
- Response recommends preserving the real external seam; single adapter count alone does not justify deletion.
- Response distinguishes removal of a port from removal of Adapter responsibilities.
- Response maps each unique old coverage category to migration or retention and acknowledges Adapter conversion tests may require an internal seam.
- No repository implementation was read or changed; only the requested audit response and receipt were written.
- No audit conclusions were read.

## Evidence limits

Only the supplied scenario and named skill guidance were inspected. No actual BillingLedger implementation, callers, composition/configuration files, provider implementation or tests were provided or executed. Behaviour assertions therefore reflect task premises or explicitly labelled inference, not code-level confirmation. The response does not establish that any particular current port shape is necessary, or that an actual defect has occurred.


### audit

#### 原始输入

请按指定 Project Audit Skill 只读审查下列提供的项目片段，模式 backend-api、concurrency、code-consistency、testing-authenticity。范围仅提供代码、配置、已确认契约；不创建报告文件。所有片段属于同一服务。

1. list_documents(): SELECT payload FROM documents WHERE tenant_id=?；无 limit。当前每租户通常 800 条，每条 payload 5MB；单响应内存上限 128MB，租户可继续上传，无条数上限。
2. nightly_counter.py 是 cron 每日独占运行的单进程计数任务，无线程/协程/跨进程调用；以数据库事务更新计数。有成功和 rollback 集成测试，未配置 race detector 或 stress test。
3. 两个公共余额入口使用同一字段 balance，其中 GET /balance 返回 cents，GET /statement 返回 dollars；公开契约规定两个都返回 cents，调用方按 cents 展示。项目测试只覆盖 /balance。
4. parse_currency 的单元测试三年没有失败；断言来自公开金额单位契约及人工算例，验证 0.01, 1.00 和超限拒绝，负向对照把实现乘100改成乘10时断言失败。

返回有依据的 findings、反证和未覆盖范围。不要编造未提供源码的位置；使用片段编号定位。

#### 原始响应

结论：提供片段支持两项需优先修正的问题：余额接口违反金额单位契约，以及文档列表无界读取超大 payload。未发现有依据的并发缺陷或 `parse_currency` 测试失真。范围仅片段 1–4 及已确认契约；未取得源码、Git 基线或运行环境。

## Findings

1. **High：`GET /statement` 返回的余额单位错误（片段 3；置信度 High，基于提供的已确认行为）。** 两个公共入口约定 `balance` 都为 cents，但 `/statement` 实际返回 dollars。调用方按 cents 展示时，100 dollars 的余额会收到 100 并显示为 1 dollar，金额缩小 100 倍。这既是 API 契约违约，也是相同字段语义不一致；合并为一项，不另报风格问题。`/balance` 正确返回 cents 是反证边界，不能保护 `/statement`；仅覆盖前者的测试也无法捕获后者的错误。最小修正是让 `/statement` 按公开契约返回 cents，并验证两个入口对同一余额输出一致。补充 `/statement` 的契约断言应直接观察响应金额单位，不要求全面重构或新增通用转换框架。

2. **High：文档列表无界读取与响应资源预算不相容（片段 1；无界数据量置信度 High，具体内存失败方式置信度 Medium）。** 查询读取租户全部 payload，没有 limit，且租户上传无条数上限。当前通常 800 × 5 MB，即约 4,000 MB 的原始 payload，约为 128 MB 单响应内存预算的 31 倍；约 26 条即超过该预算，尚未计入对象及序列化开销。正常租户发起列表请求即可触发这一规模；若完整加载或序列化在内存中，会突破预算、请求失败或被终止。未提供结果读取与响应发送实现，因此不能声称已复现 OOM，也不能排除流式处理降低峰值内存。流式处理即使存在，仍不限制单次响应总量和随上传增长的工作量。最小修正是设置服务端强制分页与单页字节预算，或让列表仅返回轻量元数据、单独获取 payload；页大小须由 5 MB 单条体积和实际开销决定。验证应使用代表性大 payload 检查页界限及峰值内存；本次没有执行该验证。

## 反证与未成立的疑点

- **片段 2：不报告 race detector/stress test 缺失为问题。** 任务每日独占、单进程、无线程/协程/跨进程调用，没有可达并发交错。数据库事务及成功、rollback 集成测试为原子性提供正向证据。不能凭“计数”推断 lost update，也没有证据要求新增锁。测试执行情况仅来自提供描述，未独立核验。
- **片段 4：不报告“三年未失败”意味着测试无效。** 断言来自公开单位契约和人工算例，包含 0.01、1.00 与超限拒绝；将乘 100 改为乘 10 的负向对照确实使断言失败，支持其识别单位回归的能力。保留这些保护。该对照仅证明所述变异的捕获能力，不证明覆盖所有解析错误。

## 覆盖与验证限制

| 维度 | 覆盖置信度 | 已审证据 | 未覆盖范围 |
|---|---|---|---|
| backend-api | Low | 片段 1 的查询、体积及预算；片段 3 的金额接口契约 | 实际读取/缓冲/序列化方式、授权、输入校验、其他接口及错误处理 |
| concurrency | Low | 片段 2 的独占执行条件、事务与集成测试描述 | 实际事务实现及服务其他并发路径；不将该任务结论推广至全服务 |
| code-consistency | Low | 片段 3 的同名字段单位及统一公开契约 | 命名、导入、风格配置和其他实现模式 |
| testing-authenticity | Low | 片段 2–4 的测试范围、断言来源及负向对照结果描述 | 测试源码、真实运行结果、mock 范围及其他金额边界 |

这是提供材料的静态审查，未执行项目测试、压测、race detector、数据库查询或内存测量。两项 findings 均定位到片段编号，没有推造源码路径或行号。未提出额外低置信度缺陷，也未给分数或发布就绪结论。

#### 加载与执行记录

# Audit receipt

Task: perform `audit-input.md` with the named Project Audit skill using supplied artifacts only. The response is captured in `audit-output.md` at the parent task's explicit request; the simulated audit itself requested conversation-only output and created no project report, metadata, or code changes. These two files are evaluation capture artifacts.

## Loaded task evidence

- `audit-work/behavior/audit-input.md` — all four supplied fragments, their stated runtime conditions, API contract and test evidence.

## Loaded guidance

- `skills-work/engineering/fuck-my-shit-mountain/SKILL.md`
- `skills-work/engineering/fuck-my-shit-mountain/prompts/backend-api-audit.md`
- `skills-work/engineering/fuck-my-shit-mountain/prompts/concurrency-audit.md`
- `skills-work/engineering/fuck-my-shit-mountain/prompts/code-consistency-audit.md`
- `skills-work/engineering/fuck-my-shit-mountain/prompts/testing-authenticity-audit.md`
- `skills-work/engineering/fuck-my-shit-mountain/rubrics/evidence.md`
- `skills-work/engineering/fuck-my-shit-mountain/rubrics/severity.md`
- `skills-work/engineering/fuck-my-shit-mountain/rubrics/confidence.md`
- `skills-work/engineering/fuck-my-shit-mountain/rubrics/coverage.md`
- `skills-work/engineering/fuck-my-shit-mountain/references/report-format.md`
- System-provided `skill-creator` guidance was read for task context; tool output was truncated and no full-read claim is made. No skill was edited or installed.

A filename inventory of `audit-work/behavior` and `skills-work/engineering` was viewed. No other behavior input, audit report, expected answer, or prior conclusion was read. No sibling review workflow applies: this is neither a diff review, architecture assessment nor simplification request.

## Evidence and verification limits

Only the supplied prose/SQL fragment was evidence. There was no source checkout review, runtime observation, independent test execution, dependency check, external research, or Git-baseline validation. Listed tests and mutation outcome are supplied evidence, not tests run by this agent. Payload volume calculation is 800 × 5 MB = 4,000 MB; exact peak-memory behavior depends on buffering/streaming absent from the input and is explicitly qualified.

Two distinct findings are reported. Unit mismatch is combined across backend-api/code-consistency rather than counted twice. The concurrency and never-failed-test cues were evaluated against explicit counterevidence and did not become findings. Coverage remains Low in all selected dimensions because the artifact is intentionally narrow.

Validation performed: semantic review for evidence locations, realistic triggers, impact, minimal correction, counterevidence, selected-mode coverage, matching finding count, and absence of invented runtime/test claims. The legacy detailed report linter was not run because the response uses a compact custom structure. No automated project checks were run. No audited repository file, configuration, test, or Git state was modified.


### verify

#### 原始输入

请按指定 verify Skill 对当前候选独立逐条验收，只读执行。
已确认 AC1：public CLI quote.py --cents 123 输出 JSON，cents=123,currency=USD。
已确认 AC2：真实付款服务完成扣款，并能从服务查询记录确认只扣款一次。
公开 CLI 在 audit-work/behavior/quote.py，无依赖。
真实服务凭据和环境当前不可用。现有本地替身测试模拟返回 successful，已有报告称 AC1/AC2 全部 PASS；该报告没有真实服务调用或查询记录。
允许调用本地 CLI 并在 audit-work/behavior 保存证据；不允许安装、登录、网络写入或变更产品代码。逐 AC 输出 PASS / FAIL / NOT VERIFIED，列实际观察和解除条件。

#### 原始响应

# 当前候选独立验收

结论：AC1 **PASS**；AC2 **NOT VERIFIED**。当前证据不足以宣称全部验收通过。

验收依据是 `audit-work/behavior/verify-input.md` 中已确认的 AC；未读取或采纳既有报告。范围仅为公开 CLI 的指定输入及真实付款/服务查询要求。候选为 `audit-work/behavior/quote.py` 当前文件，SHA-256：`0e395d3b4433133041ab387f2cca38b4e03916f02fb93e295d2cd33def7dd2e2`。未提供基线、修订号或 ticket/attempt，不能作版本差异声明。

| AC | 确认要求 | 判定 | 实际观察和覆盖限制 | 解除条件 |
| --- | --- | --- | --- | --- |
| AC1 | public CLI `quote.py --cents 123` 输出 JSON，`cents=123,currency=USD` | PASS | 独立执行 `python3 audit-work/behavior/quote.py --cents 123`，退出码 0，stdout 为 `{"cents": 123, "currency": "USD"}`；再次捕获运行并用 JSON 解析确认字段。仅覆盖该输入、当前文件和本地 Python 环境。 | 当前指定 AC 已获得充分证据；候选改变后需重新验收。 |
| AC2 | 真实付款服务完成扣款，且从服务查询记录确认只扣款一次 | NOT VERIFIED | 未执行真实服务调用或服务记录查询。任务声明真实凭据和环境不可用，并禁止登录、安装、网络写入。本地 CLI 源码只解析参数并输出 JSON，没有付款或服务查询路径。任务提到的 successful 替身结果无法证明真实扣款或次数；本次未运行替身，也未读取旧报告。 | 提供可用真实服务环境、凭据及明确授权的隔离付款与查询方法，再保留真实交易标识和对应查询记录，证明扣款完成且只发生一次。当前授权不允许自行解除环境或网络写入限制。 |

无任务声明的独立强制门禁，也未发现适用 AGENTS.md；未把 CLI 检查映射为付款验收。AC2 是证据/能力缺口，不是已观察到的产品失败。

实际执行环境：cwd `/workspace/scratch/b1e7c26f48f0`，Python 3.12.14。本地 CLI 两次运行均退出 0；第二次运行的原始 stdout、stderr、退出码、时间、候选哈希和解析结果保存在 `audit-work/behavior/verify-cli-evidence.json`。命令和加载记录见 `audit-work/behavior/verify-receipt.md`。

未安装、登录、发起网络写入、修改产品代码或仓库测试。只写入获准目录中的验收输出和证据；无待清理服务状态或临时测试资源。

#### 加载与执行记录

# Verify 执行凭据

## 加载的文件

- `skills-work/engineering/verify/SKILL.md`
- `skills-work/engineering/shared/task-contract.md`
- `skills-work/engineering/verify/references/evidence.md`
- `skills-work/engineering/project-setup/references/profile.md`
- `audit-work/behavior/verify-input.md`
- `audit-work/behavior/quote.py`
- `skill://flora-skills/root/.codex/skills/oai/skill-creator/SKILL.md`（通过 `skills.read`；用于本次 realistic validation 指示）

未读取其他报告、旧验收结论或替身测试。仅以输入文件的已确认 AC 为要求来源。

## 实际命令及结果

所有 shell 命令 cwd 均为 `/workspace/scratch/b1e7c26f48f0`，exec_command 默认 shell。

| 动作 | 结果 |
| --- | --- |
| `cat skills-work/engineering/verify/SKILL.md` | 退出 0，读取验收方法。 |
| `cat audit-work/behavior/verify-input.md` | 退出 0，读取 AC 和授权限制。 |
| `cat skills-work/engineering/shared/task-contract.md skills-work/engineering/verify/references/evidence.md skills-work/engineering/project-setup/references/profile.md` | 退出 0，读取相关边界及方法定位规则。 |
| `pwd; rg --files -g AGENTS.md -g '*Profile*' -g '*profile*' -g 'quote.py' -g '*test*' audit-work/behavior skills-work/engineering` | 退出 0；找到 quote.py 和 Skill 内方法参考文件，未发现行为目录的测试或 AGENTS.md。未加载列出的无关测试。 |
| 逐个 `test -f` 检查并在存在时 `cat` `/AGENTS.md`、`/workspace/AGENTS.md`、`/workspace/scratch/AGENTS.md`、cwd 根、`audit-work`、`audit-work/behavior` 下的 AGENTS.md | 未发现这些路径的 AGENTS.md；整组 shell 退出 0。 |
| `cat audit-work/behavior/quote.py` | 退出 0，代码仅解析 cents 并输出 JSON。 |
| `python3 --version` | 退出 0，Python 3.12.14。 |
| `sha256sum audit-work/behavior/quote.py` | 退出 0；哈希 `0e395d3b4433133041ab387f2cca38b4e03916f02fb93e295d2cd33def7dd2e2`。 |
| `python3 audit-work/behavior/quote.py --cents 123` | 退出 0，stdout `{"cents": 123, "currency": "USD"}`。以上五项在一个 shell 调用中顺序执行，总退出 0，各项观察无错误。 |
| `python3 - <<'PY'` 独立捕获并断言 CLI 输出 | 父命令退出 0；内部 subprocess argv 为 `['python3','audit-work/behavior/quote.py','--cents','123']`，退出 0，stderr 空。`json.loads` 成功；断言退出码、cents、currency 成功。已将完整结果保存为 `verify-cli-evidence.json`。 |
| here-doc 写入 `verify-output.md` 和本凭据 | 仅保存被允许的行为验收输出；无产品或仓库测试改动。 |

## 环境、权限与限度

验收代理独立运行当前本地候选；候选身份以 SHA-256 固定，未给出 Git revision、baseline 或 ticket/attempt。AC1 证据仅覆盖指定 CLI 输入。未执行付款、真实服务查询、网络写入、登录或安装；真实服务不可用是任务提供的环境事实，未探测凭据。successful 替身不能建立真实集成或只扣一次，故 AC2 NOT VERIFIED。

未创建新测试、缓存或外部状态。保留三个 run-owned 文件：`verify-output.md`、`verify-receipt.md`、`verify-cli-evidence.json`。不需清理；没有清理失败。


### verify CLI 原始文件与运行证据

```python
import argparse,json
p=argparse.ArgumentParser();p.add_argument('--cents',type=int,required=True);x=p.parse_args()
print(json.dumps({'cents':x.cents,'currency':'USD'}))
```

```json
{
  "cwd": "/workspace/scratch/b1e7c26f48f0",
  "timestamp_utc": "2026-10-07T01:26:11.466591+00:00",
  "executor": "forward_verify agent via exec_command",
  "python": "3.12.14",
  "candidate": "audit-work/behavior/quote.py",
  "sha256": "0e395d3b4433133041ab387f2cca38b4e03916f02fb93e295d2cd33def7dd2e2",
  "command": [
    "python3",
    "audit-work/behavior/quote.py",
    "--cents",
    "123"
  ],
  "exit_code": 0,
  "stdout": "{\"cents\": 123, \"currency\": \"USD\"}\n",
  "stderr": "",
  "parsed_json": {
    "cents": 123,
    "currency": "USD"
  },
  "assertions": "exit=0; cents=123; currency=USD"
}

```

### 最终审查原文

# 最终独立审查

结论：截至本次复读的候选，未发现需要修复的现存问题。最初发现的 Debug 引用冲突已修复；此前缺失的迁移计划文件已补齐。

## 范围与基线

按 `engineering/code-review/SKILL.md` 及其报告契约执行，只读检查 `skills-work` 相对本地 HEAD `aa5d7e88b1818162007f6428a8b46c535274c56d` 的文档与 Skill 改动，并纳入新增 `docs/ENGINEERING_KERNEL.md`、`docs/engineering-kernel-audit.md`、`docs/kernel-migration-plan.md`。授权范围来自调用方；没有重新推断原始用户需求的完整性。

全读修改段落与相关 Debug / codebase-design 方法和引用；长审计通过生成器 `audit-work/complete_audit.py`、完整规则 JSON、台账前言、计数、来源映射及源文抽样检查，未全读约 3MB 台账，也未读取父代理既有结论。

## 已解决问题

- 原候选 Debug 主文允许环境无法复现时以可区分竞争假设的观察集支持获准修复，但 `references/feedback-loop-escalation.md` 末段仍禁止没有 red-capable loop 时作修复决策。生产独有故障会触发相反指令。最终引用明确了同样的证据与授权条件、不可复现及回归检查的验证限制；也允许宿主原生 HITL 捕获。已复读实际修改，冲突消除。
- 审计与复核记录最初链接尚未生成的 `kernel-migration-plan.md`；最终该文件存在。不是最终候选缺陷。

## 执行证据

- `git diff --check`：通过。
- 已安装 skill-creator 的 quick_validate.py 对 debug 与 codebase-design：均通过。
- 修改/新增 Markdown 的 80 个具体相对链接：全部目标存在。未逐个验证外部 GitHub URL 可联网访问；扫描不认证锚点内容。
- 原 Kernel 与最终 Kernel 的 17 条 K01–K17 不变量逐行相同；最终使用边界保留项目契约、角色、门禁和行为依据要求。
- 181 个冻结文件：Git blob 摘要与 manifest 一致，行数一致；manifest 全部匹配保留的未截断冻结 Git tree。177 项另匹配原始 connector 返回的 SHA 与冻结显示 URL。冻结提交不在本地 Git 对象库，不能通过本地 `git show` 再认证；未伪称其命令成功。
- 4951 保留规则 ID 唯一，197 排除项与之不相交；八组候选都有保留/拆分/排除 lineage 覆盖；全部保留项来源行范围合法；17 条 Kernel 的来源 ID 映射与完整规则 JSON 一致；报告分类/disposition 计数及全部 4951 台账 ID/行范围行匹配。
- 语义抽样核对 K05/K06/K11/K12/K14 的 31 个源文见证、F02/F03 改动及 15 个 DELETE 候选；未发现样本把源文条件扩张成无条件授权，或适配器数量判定残留在修改的两个入口中。

## 覆盖限制

上述 lineage 检查证明候选被记录，不证明静态候选覆盖了完整源文件的全部行为规则；没有独立逐项重审 4951 项分类。未重跑状态工具套件、独立行为 fixture 或真实 Runtime / GUI / 跨模型对照；迁移计划中的这些执行声明不由本次代码审查独立认证。未审所有外部工程域或独立安装宿主。无发现不等于完成全部原始需求验收。

### 被演练指导文件的最终 SHA-256

| Source | SHA-256 |
| --- | --- |
| engineering/codebase-design/DEEPENING.md | `71c9dc04af2458fc9e7db662d1b4b7ca75dc7f09b178903c3f3c983f44e92550` |
| engineering/codebase-design/SKILL.md | `87dee52ce1e141cef7521e3e7933079427a6563bd5f193187f29f959ac21ed68` |
| engineering/debug/SKILL.md | `4105b8204622f45db6252494fc47f0f96c8152c9d3adfcf8bdacae6886aec1ac` |
| engineering/debug/references/feedback-loop-escalation.md | `dafa3bdc77e73cd557bdf8ce8c35a8408fe84e6ebcc8fc5471ae5ce7280920c4` |
| engineering/fuck-my-shit-mountain/SKILL.md | `b0492318839a0bddc754680df4e602b7708273512214cf34de14ecf72e5c5dd4` |
| engineering/fuck-my-shit-mountain/prompts/backend-api-audit.md | `12d249d01b9b301c54ea706230373aca033f160632b5316d1f01e7fcc9f0f1c2` |
| engineering/fuck-my-shit-mountain/prompts/code-consistency-audit.md | `cc097af8540137a207084b621c4e98cc45bc4a7e72d07941cb514e931f8ace82` |
| engineering/fuck-my-shit-mountain/prompts/concurrency-audit.md | `b93748e0c19191c181d7a0edfc87aca0bc82cbf29ffb761c0c3334536d3355f9` |
| engineering/fuck-my-shit-mountain/prompts/testing-authenticity-audit.md | `45d690dd152068792120c2d00264f81c8bd3d29e5ba8961600205942613a113f` |
| engineering/fuck-my-shit-mountain/references/report-format.md | `c16254bae5981f658dae94bb7dddb749b20339bdde674fe9a2cf5984a6bc07bd` |
| engineering/fuck-my-shit-mountain/rubrics/confidence.md | `c4bb5ac220f9533ab2157c57b560be5d1e3eff8eb1c520a0eeebbc7ad9b9a283` |
| engineering/fuck-my-shit-mountain/rubrics/coverage.md | `b5123fcb1932bb2656dde9ff63a00a6b02ffe8b5712e7fb2bfdb59ea7f4d1992` |
| engineering/fuck-my-shit-mountain/rubrics/evidence.md | `e0597aa3517f4a4c148ebd400553587a5714847b4962849b817683e0fcc5839d` |
| engineering/fuck-my-shit-mountain/rubrics/severity.md | `7ee2be55bcfa5955307ac36515812db6866dc8358bf9e89d96e7f3ab65fa1f14` |
| engineering/project-setup/references/profile.md | `cb9bb1d93af38971110a4ccff16e9e5e5c60b0e5e6c16bec71ac8cb9c44d616f` |
| engineering/shared/task-contract.md | `eabbc71efa400751f12f1a9b01021d5b50da02fb16a99d8da19b1b0d5178200d` |
| engineering/verify/SKILL.md | `25a10d4482f11a48d6c087f13f22f3d85cd3fb03e22e2a71c511b5ed3476d9c2` |
| engineering/verify/references/evidence.md | `3507d036c4da79a87fcca8b9f56f5b67b0f59efd95c9eafe1549b6dc6ad84297` |
