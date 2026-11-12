const { calculateTotal } = require('../src/cart_calculator');

describe('calculateTotal', () => {
  it('should_return_zero_when_cart_is_empty', () => {
    // Arrange
    const items = [];

    // Act
    const result = calculateTotal(items);

    // Assert
    expect(result).toBe(0);
  });

  it('should_return_zero_when_items_is_not_an_array', () => {
    // Arrange
    const items = { price: 10, quantity: 1 };

    // Act
    const result = calculateTotal(items);

    // Assert
    expect(result).toBe(0);
  });

  it('should_return_zero_when_items_is_null', () => {
    // Arrange
    const items = null;

    // Act
    const result = calculateTotal(items);

    // Assert
    expect(result).toBe(0);
  });

  it('should_return_zero_when_items_is_undefined', () => {
    // Arrange
    const items = undefined;

    // Act
    const result = calculateTotal(items);

    // Assert
    expect(result).toBe(0);
  });

  it('should_apply_default_tax_of_twenty_percent_when_tax_rate_is_omitted', () => {
    // Arrange
    const items = [{ price: 10, quantity: 2 }];

    // Act
    const result = calculateTotal(items);

    // Assert
    expect(result).toBe(24);
  });

  it('should_apply_no_discount_when_discount_is_omitted', () => {
    // Arrange
    const items = [{ price: 50, quantity: 1 }];

    // Act
    const result = calculateTotal(items);

    // Assert
    expect(result).toBe(60);
  });

  it('should_apply_custom_tax_rate_when_tax_rate_is_provided', () => {
    // Arrange
    const items = [{ price: 100, quantity: 1 }];
    const taxRate = 0.05;
    const discount = 0;

    // Act
    const result = calculateTotal(items, taxRate, discount);

    // Assert
    expect(result).toBe(105);
  });

  it('should_return_subtotal_when_tax_rate_is_zero', () => {
    // Arrange
    const items = [{ price: 12.5, quantity: 2 }];
    const taxRate = 0;
    const discount = 0;

    // Act
    const result = calculateTotal(items, taxRate, discount);

    // Assert
    expect(result).toBe(25);
  });

  it('should_subtract_discount_before_tax_when_discount_is_provided', () => {
    // Arrange
    const items = [{ price: 100, quantity: 1 }];
    const taxRate = 0.2;
    const discount = 20;

    // Act
    const result = calculateTotal(items, taxRate, discount);

    // Assert
    expect(result).toBe(96);
  });

  it('should_return_zero_when_discount_exceeds_subtotal', () => {
    // Arrange
    const items = [{ price: 10, quantity: 1 }];
    const taxRate = 0.2;
    const discount = 50;

    // Act
    const result = calculateTotal(items, taxRate, discount);

    // Assert
    expect(result).toBe(0);
  });

  it('should_return_zero_when_discount_equals_subtotal', () => {
    // Arrange
    const items = [{ price: 40, quantity: 1 }];
    const taxRate = 0.2;
    const discount = 40;

    // Act
    const result = calculateTotal(items, taxRate, discount);

    // Assert
    expect(result).toBe(0);
  });

  it('should_sum_every_line_when_cart_has_multiple_items', () => {
    // Arrange
    const items = [
      { price: 10, quantity: 2 },
      { price: 5, quantity: 3 },
      { price: 2.5, quantity: 4 },
    ];
    const taxRate = 0.2;
    const discount = 5;

    // Act
    const result = calculateTotal(items, taxRate, discount);

    // Assert
    expect(result).toBe(48);
  });

  it('should_default_quantity_to_one_when_quantity_is_missing', () => {
    // Arrange
    const items = [{ price: 15 }];
    const taxRate = 0.2;
    const discount = 0;

    // Act
    const result = calculateTotal(items, taxRate, discount);

    // Assert
    expect(result).toBe(18);
  });

  it('should_default_quantity_to_one_when_quantity_is_zero', () => {
    // Arrange
    const items = [{ price: 10, quantity: 0 }];
    const taxRate = 0.2;
    const discount = 0;

    // Act
    const result = calculateTotal(items, taxRate, discount);

    // Assert
    expect(result).toBe(12);
  });

  it('should_ignore_line_when_quantity_is_negative', () => {
    // Arrange
    const items = [
      { price: 10, quantity: -3 },
      { price: 8, quantity: 1 },
    ];
    const taxRate = 0.2;
    const discount = 0;

    // Act
    const result = calculateTotal(items, taxRate, discount);

    // Assert
    expect(result).toBe(9.6);
  });

  it('should_treat_price_as_zero_when_price_is_missing', () => {
    // Arrange
    const items = [{ quantity: 4 }];
    const taxRate = 0.2;
    const discount = 0;

    // Act
    const result = calculateTotal(items, taxRate, discount);

    // Assert
    expect(result).toBe(0);
  });

  it('should_treat_price_as_zero_when_price_is_negative', () => {
    // Arrange
    const items = [
      { price: -25, quantity: 2 },
      { price: 10, quantity: 1 },
    ];
    const taxRate = 0.2;
    const discount = 0;

    // Act
    const result = calculateTotal(items, taxRate, discount);

    // Assert
    expect(result).toBe(12);
  });

  it('should_round_to_two_decimal_places_when_total_has_extra_precision', () => {
    // Arrange
    const items = [{ price: 19.99, quantity: 3 }];
    const taxRate = 0.2;
    const discount = 5;

    // Act
    const result = calculateTotal(items, taxRate, discount);

    // Assert
    expect(result).toBe(65.96);
  });

  it('should_round_half_up_when_third_decimal_is_five', () => {
    // Arrange
    const items = [{ price: 10.335, quantity: 1 }];
    const taxRate = 0;
    const discount = 0;

    // Act
    const result = calculateTotal(items, taxRate, discount);

    // Assert
    expect(result).toBe(10.34);
  });

  it('should_keep_two_decimals_when_result_is_already_exact', () => {
    // Arrange
    const items = [{ price: 9.99, quantity: 1 }];
    const taxRate = 0.2;
    const discount = 0;

    // Act
    const result = calculateTotal(items, taxRate, discount);

    // Assert
    expect(result).toBe(11.99);
  });

  it('should_increase_subtotal_when_discount_is_negative', () => {
    // Arrange
    const items = [{ price: 10, quantity: 1 }];
    const taxRate = 0;
    const discount = -5;

    // Act
    const result = calculateTotal(items, taxRate, discount);

    // Assert
    expect(result).toBe(15);
  });

  it('should_reduce_total_when_tax_rate_is_negative', () => {
    // Arrange
    const items = [{ price: 100, quantity: 1 }];
    const taxRate = -0.1;
    const discount = 0;

    // Act
    const result = calculateTotal(items, taxRate, discount);

    // Assert
    expect(result).toBe(90);
  });
});
