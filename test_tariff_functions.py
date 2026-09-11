import pytest

from tariff_functions import calculate_flat_rate
from tariff_functions import calculate_tiered_tariff


# =========================================================
# FLAT RATE TARIFF TESTS
# =========================================================

def test_flat_rate_normal_usage():
    """
    Positive test: 300 kWh at $0.25/kWh plus $10 fixed fee.
    Expected: 300 * 0.25 + 10 = 85
    """
    result = calculate_flat_rate(300, 0.25, 10)

    assert result == 85.00


def test_flat_rate_zero_consumption():
    """
    Positive boundary test:
    No electricity usage means the customer should only pay the fixed fee.
    """
    result = calculate_flat_rate(0, 0.25, 10)

    assert result == 10.00


def test_flat_rate_without_fixed_fee():
    """
    Positive test: Check that the function works when there is no fixed fee.
    """
    result = calculate_flat_rate(100, 0.30)

    assert result == 30.00


def test_flat_rate_decimal_consumption():
    """
    Positive test: Check decimal electricity consumption.
    """
    result = calculate_flat_rate(125.5, 0.20, 10)

    assert result == 35.10


def test_flat_rate_negative_consumption():
    """
    Negative test: Electricity consumption cannot be negative.
    """
    with pytest.raises(ValueError):
        calculate_flat_rate(-100, 0.25, 10)


def test_flat_rate_negative_rate():
    """
    Negative test: Electricity rate cannot be negative.
    """
    with pytest.raises(ValueError):
        calculate_flat_rate(100, -0.25, 10)


def test_flat_rate_negative_fixed_fee():
    """
    Negative test: Fixed fee cannot be negative.
    """
    with pytest.raises(ValueError):
        calculate_flat_rate(100, 0.25, -10)


# =========================================================
# TIERED TARIFF TESTS
# =========================================================

def test_tiered_tariff_tier1_only():
    """
    Positive test: 80 kWh is entirely inside Tier 1.

    80 * 0.20 = 16
    Fixed fee = 10

    Total = 26
    """
    result = calculate_tiered_tariff(
        80,
        100,
        0.20,
        300,
        0.30,
        0.40,
        10
    )

    assert result == 26.00


def test_tiered_tariff_tier2():
    """
    Positive test: 200 kWh crosses from Tier 1 into Tier 2.

    First 100 kWh: 100 * 0.20 = 20
    Next 100 kWh: 100 * 0.30 = 30
    Fixed fee: 10

    Total = 60
    """
    result = calculate_tiered_tariff(
        200,
        100,
        0.20,
        300,
        0.30,
        0.40,
        10
    )

    assert result == 60.00


def test_tiered_tariff_tier3():
    """
    Positive test using the example from the assignment.

    Consumption = 350 kWh

    First 100 kWh: 100 * 0.20 = 20
    Next 200 kWh: 200 * 0.30 = 60
    Remaining 50 kWh: 50 * 0.40 = 20

    Fixed fee: 10

    Total = 110
    """
    result = calculate_tiered_tariff(
        350,
        100,
        0.20,
        300,
        0.30,
        0.40,
        10
    )

    assert result == 110.00


def test_tiered_tariff_exact_tier1_boundary():
    """
    Positive boundary test: Exactly 100 kWh should all be charged at Tier 1.
    """
    result = calculate_tiered_tariff(
        100,
        100,
        0.20,
        300,
        0.30,
        0.40,
        10
    )

    assert result == 30.00


def test_tiered_tariff_exact_tier2_boundary():
    """
    Positive boundary test: Exactly 300 kWh should use Tier 1 and Tier 2, but no Tier 3 electricity.
    """
    result = calculate_tiered_tariff(
        300,
        100,
        0.20,
        300,
        0.30,
        0.40,
        10
    )

    assert result == 90.00


def test_tiered_tariff_zero_consumption():
    """
    Positive boundary test: No usage means only the fixed fee is charged.
    """
    result = calculate_tiered_tariff(
        0,
        100,
        0.20,
        300,
        0.30,
        0.40,
        10
    )

    assert result == 10.00


def test_tiered_tariff_negative_consumption():
    """
    Negative test: Consumption cannot be negative.
    """
    with pytest.raises(ValueError):
        calculate_tiered_tariff(
            -50,
            100,
            0.20,
            300,
            0.30,
            0.40,
            10
        )


def test_tiered_tariff_negative_rate():
    """
    Negative test: Tariff rates cannot be negative.
    """
    with pytest.raises(ValueError):
        calculate_tiered_tariff(
            350,
            100,
            -0.20,
            300,
            0.30,
            0.40,
            10
        )


def test_tiered_tariff_invalid_thresholds():
    """
    Negative test: Tier 2 limit must be greater than Tier 1 limit.
    """
    with pytest.raises(ValueError):
        calculate_tiered_tariff(
            350,
            300,
            0.20,
            100,
            0.30,
            0.40,
            10
        )


def test_tiered_tariff_negative_fixed_fee():
    """
    Negative test: Fixed supply fee cannot be negative.
    """
    with pytest.raises(ValueError):
        calculate_tiered_tariff(
            350,
            100,
            0.20,
            300,
            0.30,
            0.40,
            -10
        )