# Verification and Review

## Verification

根据变更风险选择仓库已有的测试、静态检查、类型检查、构建或人工验收。记录每条命令、退出码、关键输出和未验证项；无法运行时说明原因，不以模型判断替代证据。

## Review

验证完成后调用 `code-review`，使用 `review_mode: implementation`，传入 baseline、既有改动、SPEC/PLAN、实际范围、implementation receipts、simplification receipt 和 verification evidence。审查必须分别输出 Standards 与 Spec；修复 finding 后重新执行受影响的验证和审查。
