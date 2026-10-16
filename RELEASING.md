# 发版

版本号按 semver，从 v3.0.0 开始（插件版本与 Ticket schema 版本各自独立）。不兼容的改动升主版本，新增能力升次版本，修正升修订号。

1. 四个插件用同一个版本号。把下面这些 `version` 全改成新版本：
   - 每个分类目录（`engineering/`、`backend/`、`documents/`、`work/`）下的 `.claude-plugin/plugin.json`，共 4 个
   - `.claude-plugin/marketplace.json` 里四个 zstack-* 条目的 `version`（ZCode 拿它和已安装版本比较）

   `scripts/check_repo.py` 会检查这些版本号是否一致，漏改会报错。
2. 跑检查：

   ```bash
   claude plugin validate .
   for d in engineering backend documents work; do claude plugin validate $d; done
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

Claude Code 和 ZCode 只在版本号变化时才会更新，忘了改版本号，用户就收不到这次发布。Codex 不看版本号，更新时直接拿 main 的最新提交，所以推到 main 的改动不等发版就会到 Codex 用户手里。
