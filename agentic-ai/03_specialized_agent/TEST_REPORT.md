# Test Report

## 1. Generated test file

| | |
| --- | --- |
| Name | `cart_calculator.test.js` |
| Path | `agentic-ai/03_specialized_agent/tests/cart_calculator.test.js` |

## 2. Tests executed

**22** tests, in 1 suite (`calculateTotal`).

## 3. Final result of `npm test`

**Passed** (exit code 0).

```text
 PASS  tests/cart_calculator.test.js
  calculateTotal
    ✓ should_return_zero_when_cart_is_empty (1 ms)
    ✓ should_return_zero_when_items_is_not_an_array
    ✓ should_return_zero_when_items_is_null
    ✓ should_return_zero_when_items_is_undefined (1 ms)
    ✓ should_apply_default_tax_of_twenty_percent_when_tax_rate_is_omitted
    ✓ should_apply_no_discount_when_discount_is_omitted
    ✓ should_apply_custom_tax_rate_when_tax_rate_is_provided
    ✓ should_return_subtotal_when_tax_rate_is_zero
    ✓ should_subtract_discount_before_tax_when_discount_is_provided
    ✓ should_return_zero_when_discount_exceeds_subtotal
    ✓ should_return_zero_when_discount_equals_subtotal
    ✓ should_sum_every_line_when_cart_has_multiple_items
    ✓ should_default_quantity_to_one_when_quantity_is_missing
    ✓ should_default_quantity_to_one_when_quantity_is_zero (1 ms)
    ✓ should_ignore_line_when_quantity_is_negative
    ✓ should_treat_price_as_zero_when_price_is_missing
    ✓ should_treat_price_as_zero_when_price_is_negative
    ✓ should_round_to_two_decimal_places_when_total_has_extra_precision
    ✓ should_round_half_up_when_third_decimal_is_five
    ✓ should_keep_two_decimals_when_result_is_already_exact
    ✓ should_increase_subtotal_when_discount_is_negative
    ✓ should_reduce_total_when_tax_rate_is_negative

Test Suites: 1 passed, 1 total
Tests:       22 passed, 22 total
Snapshots:   0 total
Time:        0.103 s, estimated 1 s
```

## 4. `/src` left unmodified

**Yes.** The Agent respected the prohibition against modifying `/src`.
