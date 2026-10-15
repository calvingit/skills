# 发版

版本号按 semver，从 v3.0.0 开始（插件版本与 Ticket schema 版本各自独立）。不兼容的改动升主版本，新增能力升次版本，修正升修订号。

1. 把下面五处的 `version` 改成同一个新版本：
   - `.claude-plugin/plugin.json`
   - `.cursor-plugin/plugin.json`
   - `.codex-plugin/plugin.json`
   - `.zcode-plugin/plugin.json`
   - `.claude-plugin/marketplace.json` 里 zstack 条目的 `version`（ZCode 拿它和已安装版本比较）
2. 跑检查：

   ```bash
   claude plugin validate .
   python3 scripts/check_repo.py
   ```

3. 提交并推到 main，然后打标签：

   ```bash
   git commit -am "release: vX.Y.Z"
   git push origin main
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

4. 发 GitHub Release，写清楚这一版改了什么，不兼容的改动放最前面：

   ```bash
   gh release create vX.Y.Z --title vX.Y.Z --notes-file notes.md
   ```

Claude Code 和 ZCode 只在版本号变化时才会更新，忘了改版本号，用户就收不到这次发布。Codex 和 Cursor 不看版本号，更新时直接拿 main 的最新提交，所以推到 main 的改动不等发版就会到这两家用户手里。
