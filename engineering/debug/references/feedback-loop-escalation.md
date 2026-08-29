# Feedback Loop 升级阶梯

`debug` skill 阶段 1 的下沉参考：构造反馈循环的完整方式、收紧反馈循环（tighten the loop）的纪律和非确定性 bug 策略。优先级从上到下：先用低成本方式拿到 red 信号，不够用再逐级升级。

## 构造方式（按优先级）

1. 真实调用路径的 seam上的失败测试
2. curl / HTTP 脚本直连运行中的服务
3. CLI + fixture 输入，stdout 与已知正确快照 diff
4. Playwright / Puppeteer 无头脚本，断言 DOM / console / network
5. 回放捕获的 trace（网络请求、payload、事件日志）
6. 最小临时 harness（单服务 + mock 依赖，一次调用触发 bug 路径）
7. property / fuzz loop：随机输入跑 1000 次找失败模式
8. bisection harness：两个已知状态间自动「boot、检查、重复」，供 `git bisect run`
9. differential loop：同一输入跑新旧版本或两份配置，diff 输出
10. HITL bash 脚本（[`scripts/hitl-loop.template.sh`](../scripts/hitl-loop.template.sh)）：必须人工点击时，用脚本提示人工操作并收集结果

## Tighten the loop

拿到循环后把它当产品打磨，直到同时满足：

- 更快：缓存 setup、跳过无关初始化、收窄测试范围
- 更精准：断言用户描述的具体症状，不是「不报错」
- 更确定：固定时间、固定随机种子、隔离文件系统、冻结网络

30 秒的 flaky loop 几乎等于没有；2 秒的确定性循环是调试利器。

## 非确定性 bug

目标不是干净复现，而是把复现率提到可调试：循环触发 100 次、并行加压、收窄时序窗口、注入 sleep。50% 复现率可调试，1% 不可调试；持续提高复现率直到进入可调试区间。

## 阶段 1 完成判据

能说出一条已经运行过至少一次的命令，且它同时满足：

- red-capable：驱动真实 bug 代码路径并断言用户的具体症状，修复后会变绿
- deterministic：每次运行结论一致（flaky bug 允许固定的高复现率）
- fast：秒级，不是分钟级
- agent-runnable：可无人值守运行

在该命令存在前不进入假设阶段；发现自己先在读代码建理论时，停下来回到本阶梯。
