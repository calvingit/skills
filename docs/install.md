# 以插件方式安装

仓库按分类目录拆成四个插件，市场都是 `calvingit`：

| 插件 | 目录 |
| --- | --- |
| `zstack-engineering` | `engineering/`（含 `shared/`） |
| `zstack-backend` | `backend/` |
| `zstack-documents` | `documents/` |
| `zstack-work` | `work/` |

每个分类目录就是一个插件根，各自带四个工具的清单，`skills` 都指向 `./`。根目录只放市场文件。`docs/`、`scripts/` 不属于任何插件。原来的整仓插件 `zstack` 已删除，装过的先卸载。

## 各工具读取的配置

| 工具 | 插件配置（每个分类目录下） | 市场配置（仓库根） |
| --- | --- | --- |
| Claude Code | `<分类>/.claude-plugin/plugin.json` | `.claude-plugin/marketplace.json` |
| Codex | `<分类>/.codex-plugin/plugin.json` | `.agents/plugins/marketplace.json` |
| Cursor | `<分类>/.cursor-plugin/plugin.json` | `.cursor-plugin/marketplace.json` |
| ZCode | `<分类>/.zcode-plugin/plugin.json` | `.zcode-plugin/marketplace.json` |

下面的命令以 `zstack-engineering` 为例，其他插件换名字即可。

## Claude Code

安装：

```text
/plugin marketplace add calvingit/skills
/plugin install zstack-engineering@calvingit
```

命令行等价写法：`claude plugin marketplace add calvingit/skills`、`claude plugin install zstack-engineering@calvingit`。

更新：

```bash
claude plugin marketplace update calvingit
claude plugin update zstack-engineering@calvingit
```

更新后重启会话，或在会话里运行 `/reload-plugins`。Claude Code 按 `version` 判断有没有新版本，只有发版改了版本号才会更新，平时推到 main 的提交不会到达已安装的用户。想自动更新，在 `/plugin` → Marketplaces 里选中 calvingit，打开 Enable auto-update；第三方市场默认关闭。

## Codex

安装：

```bash
codex plugin marketplace add calvingit/skills
```

然后在 Plugins Directory 中安装 “ZStack Engineering”，或在项目 `.codex/config.toml` 启用：

```toml
[plugins."zstack-engineering@calvingit"]
enabled = true
```

更新：

```bash
codex plugin marketplace upgrade calvingit
codex plugin add zstack-engineering@calvingit
```

## Cursor

安装：

```bash
cursor-agent plugin marketplace add https://github.com/calvingit/skills
```

然后在 `cursor-agent` 交互界面的 `/plugins` → Marketplace 里安装需要的插件（命令行没有安装子命令）。团队（Teams / Enterprise）可以在 Dashboard → Plugins → Import from Repo 填仓库地址；公开发布需提交到 <https://cursor.com/marketplace/publish> 审核。

更新：个人市场不会自动更新，重启、`cursor-agent plugin marketplace update` 或在 `/plugins` 里重装都还停在原来的提交。只能删掉市场再加回来：

```bash
cursor-agent plugin marketplace remove calvingit
cursor-agent plugin marketplace add https://github.com/calvingit/skills
```

删市场会同时卸载插件，加回来后要在 `/plugins` → Marketplace 里再装一次。团队市场可以在 Dashboard → Plugins & MCPs → Marketplace Settings 里打开 Enable Auto Refresh；仓库需要装 Cursor GitHub App，推送后最多 10 分钟同步到最新提交。

## ZCode

安装：

1. 打开任意工作区，进入 设置 → 插件。
2. 点右上角 创建 → 添加插件市场，填 `calvingit/skills`。
3. 在 个人 分段找到需要的 zstack-* 插件，点 安装。

更新：在 设置 → 插件 的市场源面板里刷新 calvingit，再到 管理已安装 点 检查更新，有新版本时在插件详情页底部更新。ZCode 比较市场条目里的 `version` 和已安装插件的 `version`，只有发版才会提示更新。

## 版本与发版

Claude Code 和 ZCode 只在版本号变化时更新；Codex 和 Cursor 更新时直接取 main 的最新提交。改版本号和发版步骤见 [releasing.md](./releasing.md)。

不用插件、手动链接单个 Skill 目录的方式见 [README](../README.md#手动安装)。
