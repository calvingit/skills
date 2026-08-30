# Verification and Review

## Verification

实现过程中持续运行当前 slice 的定向测试和相关 typecheck。收尾时按仓库约定运行静态检查、构建、端到端验证和完整测试集。只有项目契约允许更窄 gate、完整测试不可用或成本明显不成比例时才能跳过，并记录原因、替代证据和未验证范围。每条实际命令、退出码和关键输出都要记录，不能用模型判断代替证据。

## Review

验证完成后调用 `code-review`，使用 `review_mode: implementation`，传入 baseline、既有改动、SPEC 与当前 ticket（如有）、实际范围、implementation receipts、simplification receipt 和 verification evidence。审查必须分别输出 Standards 与需求契约；修复 finding 后重新执行受影响的验证和审查。
