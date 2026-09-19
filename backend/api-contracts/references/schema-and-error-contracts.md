# Schema 与行为语义

## 对齐描述、序列化与运行时

确认 OpenAPI 版本、JSON Schema 方言，以及校验器和代码生成器是否支持。`required` 表示属性存在与否，不等于非 null；缺失、null、空字符串、空数组及默认值需按业务区分。JSON Schema 的 `default` 是注解，不保证校验器自动填值。`format` 的校验方式也依方言、词汇表及工具配置核对。

检查请求和响应的序列化：查询参数、数组、日期、时区、精确数值、标识符、联合类型和额外属性策略。通过类型检查并不证明实际客户端能正确解码，也不能静默进行有损转换。

示例必须符合已确认契约，但示例不是全部允许行为。字段描述中的单位、状态转换和权限若影响行为，须有需求依据，不能由实现者自行猜测。

## 资源、错误与副作用

- 区分身份认证、操作权限、资源归属和租户边界，覆盖列表、批量和导出。错误响应是否应隐藏资源的存在遵循项目约定，不机械固定为某个状态码。
- 保持错误码、协议状态、错误体与客户端处理一致。区分校验失败、冲突、不可重试的业务拒绝、依赖故障与结果未知；不能把所有非成功响应都声明可重试。
- 对写入明确何时算接受、何时算完成，以及重试是否复用同一业务操作标识。HTTP 方法名或响应状态本身不证明整个业务流程幂等。
- 分页需保持过滤、排序与并列项规则；稳定游标不自动提供并发更新期间的快照保证。
- Schema 中的鉴权声明不会执行授权；`readOnly`/`writeOnly` 等描述也不能替代实际输入输出过滤。

沿用项目错误格式。采用 Problem Details 时核对 RFC 9457 与现有客户端，但不要为统一风格替换已发布错误协议，也不泄露堆栈、凭证或内部依赖信息。

资料：[JSON Schema 注解](https://json-schema.org/understanding-json-schema/reference/annotations)、[JSON Schema 对象](https://json-schema.org/understanding-json-schema/reference/object)、[RFC 9457](https://www.rfc-editor.org/rfc/rfc9457.html)、[HTTP 语义](https://www.rfc-editor.org/rfc/rfc9110.html)。
