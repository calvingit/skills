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

```bash
cursor-agent plugin marketplace add https://github.com/calvingit/skills
```

然后在 `cursor-agent` 交互界面的 `/plugins` → Marketplace 里安装 Calvin Skills（命令行没有安装子命令）。也可以：

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

## 更新

插件按安装时的版本缓存，仓库推送后不会自己更新。发版流程见 [releasing.md](./releasing.md)。

**Claude Code**

```bash
claude plugin marketplace update calvingit
claude plugin update calvin-skills@calvingit
```

更新后重启会话，或在会话里运行 `/reload-plugins`。Claude Code 按 `version` 判断有没有新版本，只有发版改了版本号才会更新，平时推到 main 的提交不会推给已安装的用户。想自动更新，在 `/plugin` → Marketplaces 里选中 calvingit，打开 Enable auto-update；第三方市场默认是关的。

**Codex**

```bash
codex plugin marketplace upgrade calvingit
codex plugin add calvin-skills@calvingit
```

**Cursor**

个人市场不会自动更新，重启、`cursor-agent plugin marketplace update` 或在 `/plugins` 里重装都还停在原来的提交。要更新只能先删掉市场再加回来，然后重新安装：

```bash
cursor-agent plugin marketplace remove calvingit
cursor-agent plugin marketplace add https://github.com/calvingit/skills
```

删市场会同时卸载插件，所以加回来后要在 `/plugins` → Marketplace 里再装一次 Calvin Skills。

团队市场（Teams / Enterprise）可以在 Dashboard → Plugins & MCPs → Marketplace Settings 里打开 Enable Auto Refresh。仓库需要装 Cursor GitHub App，推送后最多 10 分钟同步到最新提交。

## 实测结果

三个工具都实测过：45 个 Skill 都能识别，`engineering/shared/` 装好后仍在原来的相对位置，`.agents/skills/verify-engineering` 没有被带进插件，`create-graph` 和 `frontier` 能从安装目录直接运行。

旧的手动安装方式（链接单个 Skill 目录）见 README。
