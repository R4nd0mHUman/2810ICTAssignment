import pytest
from pathlib import Path

from tariff_functions import load_total_consumption
from tariff_functions import calculate_flat_rate
from tariff_functions import calculate_tiered_tariff


# =========================================================
# CSV DATA IMPORT TESTS
# =========================================================

def test_load_total_consumption_positive(tmp_path):
    """
    Positive test: Check that electricity usage values are correctly added together from a CSV file.
    """

    test_file = tmp_path / "test_usage.csv"

    test_file.write_text(
        "timestamp,kWh\n"
        "2025-01-01 00:00:00,0.25\n"
        "2025-01-01 01:00:00,0.50\n"
        "2025-01-01 02:00:00,1.25\n"
    )

    result = load_total_consumption(test_file)

    assert result == 2.00


def test_load_total_consumption_missing_column(tmp_path):
    """
    Negative test: The file should be rejected if it does not contain the required kWh column.
    """

    test_file = tmp_path / "test_usage.csv"

    test_file.write_text(
        "timestamp,usage\n"
        "2025-01-01 00:00:00,0.25\n"
    )

    with pytest.raises(ValueError):
        load_total_consumption(test_file)


def test_load_total_consumption_invalid_kwh(tmp_path):
    """
    Negative test: A non-numeric electricity usage value should raise a ValueError.
    """

    test_file = tmp_path / "test_usage.csv"

    test_file.write_text(
        "timestamp,kWh\n"
        "2025-01-01 00:00:00,abc\n"
    )

    with pytest.raises(ValueError):
        load_total_consumption(test_file)


def test_load_total_consumption_negative_kwh(tmp_path):
    """
    Negative test: Electricity consumption should not be negative.
    """

    test_file = tmp_path / "test_usage.csv"

    test_file.write_text(
        "timestamp,kWh\n"
        "2025-01-01 00:00:00,-2.5\n"
    )

    with pytest.raises(ValueError):
        load_total_consumption(test_file)


def test_load_total_consumption_no_records(tmp_path):
    """
    Negative test: A CSV containing headings but no electricity usage records should be rejected.
    """

    test_file = tmp_path / "test_usage.csv"

    test_file.write_text(
        "timestamp,kWh\n"
    )

    with pytest.raises(ValueError):
        load_total_consumption(test_file)


# =========================================================
# FLAT RATE TARIFF TESTS
# =========================================================

def test_flat_rate_normal_usage():
    """
    Positive test: 300 kWh at $0.25/kWh plus $10 fixed fee.
    Expected: 300 * 0.25 + 10 = 85
    """

    result = calculate_flat_rate(
        300,
        0.25,
        10
    )

    assert result == 85.00


def test_flat_rate_zero_consumption():
    """
    Positive boundary test: No electricity usage means the customer should only pay the fixed fee.
    """

    result = calculate_flat_rate(
        0,
        0.25,
        10
    )

    assert result == 10.00


def test_flat_rate_without_fixed_fee():
    """
    Positive test: Check that the function works when there is no fixed fee.
    """

    result = calculate_flat_rate(
        100,
        0.30
    )

    assert result == 30.00


def test_flat_rate_decimal_consumption():
    """
    Positive test: Check decimal electricity consumption.
    """

    result = calculate_flat_rate(
        125.5,
        0.20,
        10
    )

    assert result == 35.10


def test_flat_rate_negative_consumption():
    """
    Negative test: Electricity consumption cannot be negative.
    """

    with pytest.raises(ValueError):
        calculate_flat_rate(
            -100,
            0.25,
            10
        )


def test_flat_rate_negative_rate():
    """
    Negative test: Electricity rate cannot be negative.
    """

    with pytest.raises(ValueError):
        calculate_flat_rate(
            100,
            -0.25,
            10
        )


def test_flat_rate_negative_fixed_fee():
    """
    Negative test: Fixed fee cannot be negative.
    """

    with pytest.raises(ValueError):
        calculate_flat_rate(
            100,
            0.25,
            -10
        )


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


# =========================================================
# PROVIDED XPOWER DATASET TESTS
# =========================================================

def test_provided_dataset_total_consumption():
    """
                                            Integration test:
    Check that the supplied XPower dataset can be read and produces the expected total electricity usage.
                            The supplied file contains 850.67 kWh in total.
    """

    csv_file = (
        Path(__file__).parent
        / "sample_usage_data_month.csv"
    )

    result = load_total_consumption(csv_file)

    assert result == 850.67


def test_flat_rate_with_provided_dataset():
    """
    Integration test: Calculate a flat-rate bill using the supplied electricity usage dataset.

    Total consumption: 850.67 kWh
    Flat rate: $0.25/kWh
    Fixed fee: $10

    Expected total: $222.67
    """

    csv_file = (
        Path(__file__).parent
        / "sample_usage_data_month.csv"
    )

    consumption = load_total_consumption(csv_file)

    result = calculate_flat_rate(
        consumption,
        0.25,
        10
    )

    assert result == 222.67


def test_tiered_tariff_with_provided_dataset():
    """
    Integration test: Calculate a tiered bill using the supplied electricity usage dataset.

    Total consumption: 850.67 kWh
    Tier 1: First 100 kWh at $0.20
    Tier 2: Next 200 kWh at $0.30
    Tier 3: Remaining usage at $0.40
    Fixed fee: $10

    Expected total: $310.27
    """

    csv_file = (
        Path(__file__).parent
        / "sample_usage_data_month.csv"
    )

    consumption = load_total_consumption(csv_file)

    result = calculate_tiered_tariff(
        consumption,
        100,
        0.20,
        300,
        0.30,
        0.40,
        10
    )

    assert result == 310.27