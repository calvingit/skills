# Useful Behaviour Tests

## Observe the contract

For a confirmed rule that a valid checkout produces a confirmed order, exercise the production entry point and inspect its result:

```typescript
test("valid checkout confirms the order", async () => {
  const cart = createCart();
  cart.add(product);
  const result = await checkout(cart, paymentMethod);
  expect(result.status).toBe("confirmed");
});
```

This establishes only the exercised path. If payment is replaced by a fake, it does not prove the provider integration or the user interface.

An assertion that an internal helper was called usually protects incidental structure. But an assertion that a payment provider receives one charge can protect a real no-duplicate-charge contract. Judge the requirement and exercised boundary, not the presence of a call-count assertion.

Prefer reading a write back through its production interface when that is the behaviour under test. Direct database inspection is appropriate when testing persistence constraints or side effects that are themselves required; it cannot stand in for proving a separate retrieval API works.

## Establish the expected result independently

Suppose the confirmed pricing example says two items priced 10 and 5 total 15, with no tax or discount:

```typescript
test("totals the confirmed two-item pricing example", () => {
  expect(calculateTotal([{ price: 10 }, { price: 5 }])).toBe(15);
});
```

The worked example supplies the expectation. Merely reading the implementation and replacing its output with `15` would not establish an independent basis.

Copying a production reduction into the assertion risks reproducing its mistakes:

```typescript
const expected = items.reduce((sum, item) => sum + item.price, 0);
expect(calculateTotal(items)).toBe(expected);
```

This is not automatically incapable of failure: it could catch an implementation that omits an item. Its weakness is that shared assumptions may be wrong together. Independently justified formulas, properties or reference implementations can be useful; name their basis and what violation they detect.

A date-format assertion such as `expect(formatDate(date)).toBe("2026-09-25")` may protect an external format contract. Do not delete it because it is simple. Check relevant locale/time-zone requirements and whether another test retains the same protection.

## Keep meaningful failures

For a bug, reproduce the failing behaviour before the fix and rerun after it. For a new behaviour, check that Red comes from that missing behaviour, not broken setup. Keep assertions strong during Green and refactoring. A test that passes before implementation needs investigation; do not manufacture failure by breaking unrelated code.
