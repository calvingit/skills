---
name: url-to-markdown
description: Convert public URLs into local Markdown files.
---

# URL To Markdown

把公开网页转换成干净的 Markdown 文件，方便后续 Agent 阅读、总结、改写或继续加工。

## 何时使用

当用户出现下面这些需求时，使用本 Skill：

- 给出一个或多个网页 URL，希望导出成 `.md`。
- 需要把网页正文转换成更适合 Agent 处理的文本。
- 想把博客、文档、文章、网页说明页保存为 Markdown。
- 想先抓取网页内容，再让 Agent 做总结、翻译、重写、归档。

如果用户只是想“看一下网页”，而不需要落地成文件，可以直接读取页面内容；但只要用户明确要保存、导出、交给后续流程使用，优先调用本 Skill。

## 处理流程

1. 确认输入 URL 是完整链接，保留原始 `http://` 或 `https://`。
2. 从当前加载的 Skill 路径确定安装目录，将其绝对路径记为 `$SKILL_DIR`，运行脚本；不要假设用户项目包含 `skills/` 目录：

```bash
bash "$SKILL_DIR/scripts/fetch_markdown.sh" "<URL>" "<输出文件路径>"
```

3. 如果用户没有指定输出路径，可以让脚本自动生成默认文件名。
4. 脚本会按以下顺序尝试服务：
   - `https://markdown.new`
   - `https://r.jina.ai`
   - `https://defuddle.md`
5. 每个服务单次超时为 10 秒。脚本跳过空白响应、明显的 HTML 页面和常见错误响应，接受有效候选后停止重试；已有输出文件不会被覆盖。
6. 读取输出文件，核对标题、来源和正文是否对应目标页面，排除验证码、登录页、限流提示和截断内容。脚本成功只表示通过基础检查，不证明正文完整。未确认正文有效时，不进入总结或改写，也不把错误页当作原文。

## 输入与输出

输入：

- 一个公开可访问的网页 URL。
- 可选的输出文件路径。

输出：

- 一个本地 Markdown 文件。

## 失败处理

- 若第一个服务失败，继续尝试下一个，不要停在单点失败。
- 若三个服务都失败，向用户报告失败，并附上脚本打印的错误摘要。
- 不要捏造网页内容；无法抓取时要明确说明失败。

## 示例

```bash
bash "$SKILL_DIR/scripts/fetch_markdown.sh" \
  "https://weekly.tw93.fun/posts/261" \
  "/tmp/post.md"
```

如果用户随后要总结、翻译、改写或入库，应基于生成的 Markdown 文件继续工作，而不是重新抓取原网页。
