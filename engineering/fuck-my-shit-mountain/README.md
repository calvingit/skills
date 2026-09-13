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

本仓库维护的是本地适配版本，安装时使用当前 checkout 中的 `engineering/fuck-my-shit-mountain/`，不要用重新下载的上游副本覆盖本地规则。完整目录包含 prompts、rubrics、templates 和 scripts，不能只复制 `SKILL.md`。

来源记录：[Fuck_My_Shit_Mountain](https://github.com/XiNian-dada/Fuck_My_Shit_Mountain)。此链接用于追溯来源，不是本地适配版本的安装入口。

按运行环境已配置的 Skill 发现方式接入本目录。已有同名目录或链接时，先核对目标和本地修改，不删除覆盖。技能名称保持 `fuck-my-shit-mountain`，当前调用策略仍是显式调用。

需要分发包时，在本仓库根目录运行：

```bash
python3 engineering/fuck-my-shit-mountain/scripts/package_skill.py --output /tmp/project-audit-skill.zip
```

安装位置和是否支持目录链接由目标运行环境决定；文件可访问不等于已加载，安装后应核对发现结果。

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

模式清单与调查范围统一见 [SKILL.md 的模式表](SKILL.md#modes)。模式名是调用时传给 Agent 的审计范围，不是独立的 `run` CLI 命令。可组合 `security, stability, type-safety` 等模式。

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

## 验证本地改动

在仓库根目录运行离线脚本测试：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s engineering/fuck-my-shit-mountain/tests -p 'test_report_lint.py'
```

JSON Schema 回归测试使用 `jsonschema`；环境已提供该依赖时运行 `test_report_schema.py`。评分、证据、覆盖范围和报告格式以 Skill 入口引用的规则为准，这里不另列第二份强制要求。
