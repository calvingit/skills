# 默认结构

只保留有实际内容的章节，不强行补齐空章节。标题和正文语言应与仓库的主要文档保持一致。

```markdown
# Agent Instructions

## Repository
- [会影响 Agent 工作方式的项目定位或目录导航]

## Commands
| Task | Command |
| --- | --- |
| Focused test | `[已验证命令]` |
| Lint or typecheck | `[已验证命令]` |

## Working Rules
- [稳定且为当前仓库特有的要求]

## Verification
- [报告完成前必须检查的内容]

## References
- Architecture: `[仓库相对路径]`
```
