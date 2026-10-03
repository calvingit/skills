# HTML 模板与内容稿

仅在已经选择 HTML 输出后读取。本模板借鉴 `answer-me-with-html` 的双版式、按信息形状选组件和内容／渲染分离思路，不依赖其 CLI 或自定义 Markdown 语法。

先判断模板是否适合表达目标。常规总览、顺序讲解和对比可以使用；空间布局、连续叙事、交互探索或特殊视觉结构需要不同页面组织时，直接写定制 HTML，不要求先试模板。不为节省输出而牺牲理解，也不用 `html` 块硬套外层布局。

## 使用

需要 Python 3.10+，仅使用标准库，无需安装包。将 `<show-me-dir>` 替换为本 Skill 的实际目录，从当前任务目录运行：

```bash
python3 <show-me-dir>/scripts/render.py content.json -o explanation.html
```

输出目录须存在，默认拒绝覆盖已有文件；确认需要替换时加 `--force`。`-` 可从标准输入读取稿件。保留 JSON 源稿，输出页也内嵌完整源稿，可复制或在剪贴板不可用时展开。模板位于 [explanation.html](explanation.html)，不要直接把带占位符的模板当成交付页。

## 版式

- `sheet`：默认总览。适合架构概览、方案对比和阶段总结；用 `span` 给重要图示或表格更大空间。
- `doc`：顺序讲解，桌面提供章节导航。适合原理、调用链和设计依据。

同一页面可以切换版式，内容与顺序保持一致。手机端按源稿顺序单栏阅读，不固定面板数量，也不为填满网格补写内容。结论、流程、对比不是必选章节，不能因为有组件就补造内容。

导航、编号和面板边框可以通过 `presentation` 关闭。短说明可只使用一个无标题正文区，避免切成卡片：

```json
{
  "title": "缓存复用的条件",
  "layout": "doc",
  "presentation": {"toc": false, "numbers": false, "cards": false},
  "sections": [{"blocks": [{"type": "text", "paragraphs": [
    "内容未变化时可以跳过重复写入，但缓存仍须有效才能复用。",
    "缓存无效则重新计算；内容变化则写入并使旧缓存失效。这是拟议规则，尚未实现。"
  ]}]}]
}
```

## 最小稿件

```json
{
  "title": "内容比较与缓存复用",
  "summary": "内容不变时可以跳过重复写入，缓存是否有效仍需单独判断。",
  "status": "拟议方案，尚未实现",
  "layout": "sheet",
  "sections": [
    {
      "title": "结论",
      "blocks": [{"type": "callout", "paragraphs": ["仅在缓存仍有效时复用结果。"]}]
    },
    {
      "title": "条件与动作",
      "span": 2,
      "blocks": [{
        "type": "table",
        "headers": ["内容", "缓存", "动作"],
        "rows": [
          ["未变化", "有效", "跳过写入，复用"],
          ["未变化", "无效", "跳过写入，重新计算"],
          ["已变化", "任意", "写入，使旧缓存失效"]
        ]
      }]
    }
  ]
}
```

## 字段与组件

页面必填 `title`、非空 `sections`。`summary`、`subtitle`、`status` 可省略，`layout` 默认为 `sheet`。每节必填非空 `blocks`，`title` 可省略，未命名的节不生成标题或导航项。`span` 为 1（默认）、2 或 3（整行）。一节可以组合多个块。

`presentation` 可省略，支持布尔字段 `toc`、`numbers`、`cards`。默认多节有标题内容生成导航，单节不生成；编号与卡片样式默认开启。`toc: false` 同时移除导航占位列，`numbers: false` 移除标题和导航中的编号，`cards: false` 移除面板背景与边框，保留表格结构和结论强调。字段控制排版，不限制内容的含义、数量或顺序。

| type | 字段 | 用途 |
| --- | --- | --- |
| `text` | `paragraphs: string[]` | 连续解释，按需补充条件和限制 |
| `callout` | `paragraphs: string[]` | 强调结论，该节获得强调边框 |
| `list` | `items: string[]` | 独立并列项 |
| `table` | `headers: string[]`、`rows: string[][]` | 精确比较，每行列数必须相同 |
| `diagram` | `svg: string`、可选 `caption` | 已由工具生成的内联 SVG |
| `html` | `html: string` | 现有组件无法表达的自定义内容或交互控件 |

普通文本按纯文本转义，不解析 Markdown。图示优先通过已有工具生成 SVG；本脚本只嵌入图形，不提供自动布局或 Mermaid 渲染。不要把 Mermaid 源码直接放进 `svg` 字段。

`html`、`svg` 和页面级可选 `script` 是原样嵌入入口，只放自行编写并检查过的内容，不能将网页抓取内容或用户原文直接作为代码嵌入。原始标记中的 ID 应唯一，并避开模板控制 ID 和自动生成的 `section-N`。需要定制交互时用 `html` 创建控件，在 `script` 写逻辑；只在交互帮助理解时增加。

完整缓存示例见 [html-example.json](html-example.json)，包含流程图、表格和场景探索：

```bash
python3 <show-me-dir>/scripts/render.py \
  <show-me-dir>/references/html-example.json -o cache-explanation.html
```

它是概念示例，缓存收益、并发和真实持久化尚未验证。布局、主题及模型推理速度没有统一改善保证。输出后检查桌面／手机显示、表格与图示、版式切换、复制源稿及相关交互；无法执行的检查明确报告未验证。渲染成功只证明脚本生成了文件。
