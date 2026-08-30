# Good and Bad Tests

## Good

好的测试通过公开 Interface 验证调用方关心的行为，使用真实生产构造，预期值来自独立事实，并能在内部重构后继续有效。

```typescript
test("user can checkout with valid cart", async () => {
  const result = await checkout(validCart, paymentMethod);
  expect(result.status).toBe("confirmed");
});
```

## Implementation-coupled

不要把内部 collaborator 的调用次数、private method 或当前调用顺序当作行为契约。

```typescript
// Bad: refactor-safe behavior is not being tested.
expect(mockPayment.process).toHaveBeenCalledWith(cart.total);
```

验证写入后的结果时，也应通过生产 Interface 重新读取，而不是绕过 Interface 直接查询内部数据库，除非数据库本身就是公开 contract。

## Tautological

不要在测试中用与实现相同的算法重新计算 expected value。使用已确认 literal、worked example、公开 contract 或其他独立来源。

```typescript
expect(calculateTotal([{ price: 10 }, { price: 5 }])).toBe(15);
```
