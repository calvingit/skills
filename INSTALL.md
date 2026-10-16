# 以插件方式安装

仓库按分类目录拆成四个插件，市场都是 `calvingit`：

| 插件 | 目录 |
| --- | --- |
| `zstack-engineering` | `Engineering/skills/`（含 `shared/`） |
| `zstack-backend` | `Backend/skills/` |
| `zstack-documents` | `Documents/skills/` |
| `zstack-work` | `Work/skills/` |

每个分类目录就是一个插件根，skill 都放在它下面的 `skills/` 里（`Engineering/skills/shared/` 是工程 skill 共用的契约和脚本，不是 skill）。插件根只放 `.claude-plugin/plugin.json`（Claude Code 格式，其他工具也读它）和一份 README，布局参照 [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins)。仓库根放市场文件和 INSTALL.md、RELEASING.md 等说明。`scripts/` 不属于任何插件。原来的整仓插件 `zstack` 已删除，装过的先卸载。

## 各工具读取的配置

| 工具 | 插件配置（每个分类目录下） | 市场配置（仓库根） |
| --- | --- | --- |
| Claude Code | `.claude-plugin/plugin.json` | `.claude-plugin/marketplace.json` |
| Codex | 找不到自己的 `.codex-plugin` 时读 `.claude-plugin/plugin.json` | 找不到 `.agents/plugins/marketplace.json` 时读 `.claude-plugin/marketplace.json` |
| ZCode | 依次找 `.zcode-plugin`、`.claude-plugin`、`.codex-plugin` | 同左，落到 `.claude-plugin/marketplace.json` |

外部引用里 React、Vue 两个上游没有插件清单，条目用 `strict: false` 加 `skills` 字段在市场文件里声明插件内容（插件根是上游的 `skills/` 目录）。ZCode 能装 `git-subdir` 来源（supply-chain-risk-auditor 可以装），但它的文档写明插件清单是必需文件，没有清单时能否靠 `strict: false` 安装未验证。

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

然后在 Plugins Directory 中安装 zstack-engineering，或在项目 `.codex/config.toml` 启用：

```toml
[plugins."zstack-engineering@calvingit"]
enabled = true
```

更新：

```bash
codex plugin marketplace upgrade calvingit
codex plugin add zstack-engineering@calvingit
```

## ZCode

安装：

1. 打开任意工作区，进入 设置 → 插件。
2. 点右上角 创建 → 添加插件市场，填 `calvingit/skills`。
3. 在 个人 分段找到需要的 zstack-* 插件，点 安装。

更新：在 设置 → 插件 的市场源面板里刷新 calvingit，再到 管理已安装 点 检查更新，有新版本时在插件详情页底部更新。ZCode 比较市场条目里的 `version` 和已安装插件的 `version`，只有发版才会提示更新。

## 版本与发版

Claude Code 和 ZCode 只在版本号变化时更新；Codex 更新时直接取 main 的最新提交。改版本号和发版步骤见 [releasing.md](./RELEASING.md)。

不用插件、手动链接单个 Skill 目录的方式见 [README](./README.md#手动安装)。
