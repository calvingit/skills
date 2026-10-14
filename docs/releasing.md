# 发版

版本号按 semver，从 v3.0.0 开始（对应 Ticket v3）。不兼容的改动升主版本，新增能力升次版本，修正升修订号。

1. 把三个插件配置里的 `version` 改成同一个新版本：
   - `.claude-plugin/plugin.json`
   - `.cursor-plugin/plugin.json`
   - `.codex-plugin/plugin.json`
2. 跑检查：

   ```bash
   claude plugin validate .
   python3 engineering/shared/check.py
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

Claude Code 只在版本号变化时才会更新，忘了改版本号，用户就收不到这次发布。
