# 以插件方式安装

仓库根目录就是一个插件 `calvin-skills`（marketplace `calvingit`），包含 `engineering/`、`backend/`、`documents/`、`work/` 下的全部 Skill。`.agents/skills/verify-engineering` 只用于维护本仓库，不在插件内。

| 工具 | 配置文件 |
| --- | --- |
| Claude Code | `.claude-plugin/plugin.json`、`.claude-plugin/marketplace.json` |
| Cursor | `.cursor-plugin/plugin.json` |
| Codex | `.codex-plugin/plugin.json`、`.agents/plugins/marketplace.json` |

## Claude Code

```text
/plugin marketplace add calvingit/skills
/plugin install calvin-skills@calvingit
```

CLI 等价命令：`claude plugin marketplace add calvingit/skills`、`claude plugin install calvin-skills@calvingit`。本地调试：`claude --plugin-dir /path/to/skills`。

## Cursor

- 个人本地：把仓库克隆或链接到 `~/.cursor/plugins/local/calvin-skills`，重启 Cursor。
- 团队（Teams / Enterprise）：Dashboard → Plugins → Import from Repo，填 `https://github.com/calvingit/skills`。
- 公开发布需提交到 <https://cursor.com/marketplace/publish> 审核。

## Codex

```bash
codex plugin marketplace add calvingit/skills
```

然后在 Plugins Directory 中安装 “Calvin Skills”；或在项目 `.codex/config.toml` 启用：

```toml
[plugins."calvin-skills@calvingit"]
enabled = true
```

## 尚未实测的点

以下行为官方文档没有写清楚，需要在真实安装中确认：

1. **Codex 多路径 skills**：`.codex-plugin/plugin.json` 的 `skills` 是否接受数组、是否把分类目录当作 Skill 父目录扫描。
2. **Cursor 目录扫描**：`skills` 填分类目录时，是否会扫描其下的 `<name>/SKILL.md`。不行就改为逐个列出 Skill 目录。
3. **相对路径是否保留**：Cursor 和 Codex 安装时是否整库复制，`engineering/*/SKILL.md` 到 `../shared/`（含 `engineering/shared/` 下脚本）的相对路径装好后是否仍然有效。
4. 确认 `.agents/skills/verify-engineering` 没有被任一工具带进插件。

旧的手动安装方式（链接单个 Skill 目录）见 README。
