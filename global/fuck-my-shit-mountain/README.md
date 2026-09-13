# Fuck My Shit Mountain

给 AI coding agent 用的代码库审计 skill。它会按项目结构和你选的方向生成审计报告：风险、证据、影响、修复顺序和测试建议。

## 功能

- 审计代码库的 **26 个维度**（full 模式）：架构、安全、稳定性、性能、测试、可维护性、设计、发布、文档、配置、可观测性、数据完整性、隐私治理、可访问性、供应链、成本、AI/LLM 安全、降级、测试真实性、类型安全、前端状态、后端 API、依赖权重、代码一致性、注释覆盖率、**并发**
- **增量审计模式**：只审计 git diff 中的变更文件，适用于 PR review 和持续审计
- **按需评分**：明确要求评分时，根据证据和覆盖范围评价相关维度
- **审计范围控制**：支持路径模式、语义标签或 git 引用限定审计范围
- **多格式输出**：支持 Markdown、HTML、JSON（便于 CI/CD 集成）
- **按需历史追踪**：明确要求时，将元数据保存到用户指定或项目已有的审计位置
- 生成结构化发现项，包含严重程度、置信度、证据和修复建议
- 标注每个审计维度的覆盖置信度（High / Medium / Low / Not assessed）
- 请求评分时，对 **7 个核心维度** 打分（0.0–10.0），附带等级 S/A/B/C/D/F
- 区分**已确认**和**待确认**问题
- 按风险排序；请求修复计划时，再给出有依据的工作量估计
- 每个发现说明适合的验证方式，不机械要求新增测试

## 范围与输出

沿用用户指定的审计目标与范围。默认使用当前对话语言，在对话中返回简明 Markdown，不再为语言或格式单独发起问卷。明确要求全量审计时使用 `full`；指定关注点时选择对应模式，仅在范围或 Git 基线会改变结论时补充确认。

请求文件时支持 `md`、`html`、`json`、`both`。大型报告模板、评分和历史追踪按需启用，具体规则统一见 [报告规则](references/report-format.md)。普通变更、架构与复杂度审查复用已安装工程技能的判断标准；独立安装时使用本技能的证据与覆盖规则。

## 安装与使用

懒人版：把这个链接丢给你的 AI IDE，让它把 `fuck-my-shit-mountain/` 这个 skill 装到 Codex 里：

[https://github.com/XiNian-dada/Fuck_My_Shit_Mountain](https://github.com/XiNian-dada/Fuck_My_Shit_Mountain)

它要是问怎么装，告诉它：clone 仓库，然后把里面的 `fuck-my-shit-mountain/` 目录复制到对应 skills 目录。

### 手动安装

```bash
git clone https://github.com/XiNian-dada/Fuck_My_Shit_Mountain.git
mkdir -p ~/.codex/skills
rm -rf ~/.codex/skills/fuck-my-shit-mountain
cp -R Fuck_My_Shit_Mountain/fuck-my-shit-mountain ~/.codex/skills/
```

然后重启 Codex，或者新开一个对话。其他工具就把 `fuck-my-shit-mountain/` 复制到对应位置：

| 工具 | 个人安装目录 | 项目安装目录 | 备注 |
|------|--------------|--------------|------|
| Codex | `~/.codex/skills/fuck-my-shit-mountain/` | - | 复制后重启 Codex |
| Claude Code | `~/.claude/skills/fuck-my-shit-mountain/` | `.claude/skills/fuck-my-shit-mountain/` | 可通过 `/fuck-my-shit-mountain` 或自然语言触发 |
| GitHub Copilot（CLI / VS Code Agent / Cloud Agent） | `~/.copilot/skills/fuck-my-shit-mountain/` 或 `~/.agents/skills/fuck-my-shit-mountain/` | `.github/skills/fuck-my-shit-mountain/`、`.claude/skills/fuck-my-shit-mountain/` 或 `.agents/skills/fuck-my-shit-mountain/` | 安装后执行 `/skills reload` |
| Gemini CLI | `~/.gemini/skills/fuck-my-shit-mountain/` 或 `~/.agents/skills/fuck-my-shit-mountain/` | `.gemini/skills/fuck-my-shit-mountain/` 或 `.agents/skills/fuck-my-shit-mountain/` | 安装后执行 `/skills reload`，工作区安装前先 trust |

通用示例提示词：

```text
请使用 fuck-my-shit-mountain skill 审计当前项目
模式：full
报告语言：中文
输出格式：html
```

增量审计（PR review）示例：

```text
使用 fuck-my-shit-mountain 审计本次 PR 的变更
模式：incremental
范围：main...HEAD（相对分叉点的 PR 变更）
报告语言：中文
输出格式：json
```

指定范围审计示例：

```text
审计支付模块
模式：security, data-integrity
范围：src/payments/**
报告语言：中文
输出格式：md
```

### 模式选择

| 命令 | 范围 |
|------|------|
| `run full-audit` | 全部 26 个审计维度 |
| `run incremental-audit` | **增量审计**：只审计 git diff 中的变更文件（需配合 scope 参数） |
| `run concurrency-audit` | **并发审计**：竞态条件、死锁、原子性、共享状态、锁策略 |
| `run architecture-audit` | 架构边界、依赖方向、状态所有权 |
| `run security-audit` | 仅安全审查 |
| `run stability-audit` | 可靠性和错误处理 |
| `run performance-audit` | 真实性能瓶颈 |
| `run testing-audit` | 测试质量和覆盖率缺口 |
| `run maintainability-audit` | 代码复杂度和耦合 |
| `run design-audit` | 工程原则和设计风险 |
| `run release-audit` | 发布和部署就绪度 |
| `run documentation-audit` | 文档准确性、设置、运维/开发指南 |
| `run observability-audit` | 日志、指标、追踪、健康检查、告警 |
| `run configuration-audit` | 配置校验、默认值、环境隔离、功能开关 |
| `run data-integrity-audit` | 事务、幂等、迁移、一致性、备份恢复 |
| `run privacy-audit` | PII、数据最小化、保留、删除、导出 |
| `run accessibility-audit` | 键盘、焦点、语义、响应式和 UX 状态 |
| `run supply-chain-audit` | 依赖来源、可复现构建、CI 完整性、签名 |
| `run cost-audit` | 资源经济性、预算、外部 API 和 LLM 成本 |
| `run ai-safety-audit` | Prompt injection、工具授权、RAG 泄露、eval |
| `run fallback-audit` | 静默降级、空 catch、防御性猜测 |
| `run testing-authenticity-audit` | 真实测试信心 vs 绿色勾号 |
| `run type-safety-audit` | Unsafe 块、类型断言、边界类型 |
| `run frontend-state-audit` | 组件大小、状态管理、副作用 |
| `run backend-api-audit` | API 设计、校验、数据访问模式 |
| `run dependency-weight-audit` | 过重依赖、构建工具链 |
| `run code-consistency-audit` | 命名、导入、模式、风格统一性 |
| `run comment-coverage-audit` | 文档质量、过期注释、缺失文档 |

> 组合模式：`security, stability, type-safety` — AI 会合并各模式的审计范围。

## 报告与验证

默认报告包含结论、范围与基线、按影响排序的问题、证据、最小修正建议和覆盖限制。评分、详细模板和修复计划只在需要时使用。输出格式与验证要求见 [报告规则](references/report-format.md)，避免在这里维护第二份契约。

## 文件结构

```
fuck-my-shit-mountain/
  SKILL.md              技能入口 — 工作方式和规则
  README.md             本文件
  agents/               UI metadata（openai.yaml）
  prompts/              审计提示词模板（28 种模式，含 full、incremental 和 concurrency）
  references/           公共报告格式、HTML、coverage、lint、工具参考
  rubrics/              严重程度、置信度、证据、原则、评分
  scripts/              项目画像、生成报告后的 lint / 校验脚本
  templates/            报告、发现卡、修复计划模板（含 JSON schema）
  examples/             不同项目类型的使用示例
```

## 可选评分体系

每个维度 0.0–10.0 分，等级 S/A/B/C/D/F：

```
Security        ████████░░  8.0  A   No auth on WS, hardcoded secret in config
Stability       ██████░░░░  6.0  B   3 unwrap on hot path, no retry on DB
Performance     ██████████  10.0 S   No issues found
Testing         ████░░░░░░  4.0  C   9 integration tests real, but unit is weak
Maintainability ███████░░░  7.0  A   3 files over 800 lines, SRP violated in 2 modules
Design          █████░░░░░  5.0  B   DRY violated 5x, fail-fast missing at API boundary
Release         ██████░░░░  6.0  B   No CI on Windows, no rollback plan
─────────────────────────────────────
Overall         ██████░░░░  6.6  B
```

评分基于**判断**而非公式。**越高越好（10 = 干净，0 = 屎山）。** AI 根据证据整体评估，每个维度附一句话理由。详见 `rubrics/scoring.md`。

## 规则

- 每个发现必须有**具体证据**
- 禁止情绪化语言和人身攻击
- 禁止对代码质量的泛泛抱怨
- 禁止默认建议重写
- 区分**已确认**和**待确认**问题
- 每个发现附带**回归测试建议**
- 每个发现预估**修复工作量**
- 系统化覆盖一方源代码、测试、配置、依赖和发布文件，并在报告中说明排除项
- 发现密钥、令牌或私钥时必须脱敏报告，不输出完整敏感值
