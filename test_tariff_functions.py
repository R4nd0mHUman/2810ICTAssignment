from datetime import datetime, time # Provides datetime for test timestamps and time for testing time-of-use periods.
from pathlib import Path # Provides tools for locating the supplied test data files.

import pytest # Provides the testing framework used to run automated tests and check expected errors.
from openpyxl import Workbook # Allows temporary Excel workbooks to be created for testing Excel data imports.

# Imports the XPower functions that are being tested.
from tariff_functions import (
    calculate_flat_rate,
    calculate_flat_rate_breakdown,
    calculate_tiered_breakdown,
    calculate_tiered_tariff,
    calculate_tou_tariff,
    compare_tariffs,
    filter_usage_records,
    generate_saving_suggestions,
    load_total_consumption,
    load_usage_records,
)


HERE = Path(__file__).parent


def records(*items):
    """Create usage records from timestamp strings and kWh values."""
    return [
        {"timestamp": datetime.fromisoformat(stamp), "kWh": kwh}
        for stamp, kwh in items
    ]


# =========================================================
# DATA IMPORT TESTS
# =========================================================

def test_load_csv_and_total():
    """
    Positive integration test: Check that the supplied CSV file can be loaded and contains the expected number of
                                        records and total electricity consumption.
    """
    loaded = load_usage_records(HERE / "sample_usage_data_month.csv")

    assert len(loaded) == 720
    assert load_total_consumption(HERE / "sample_usage_data_month.csv") == 850.67


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


def test_load_excel(tmp_path):
    """Positive test: Check that usage can be loaded from an Excel file."""
    path = tmp_path / "usage.xlsx"
    book = Workbook()
    sheet = book.active

    sheet.append(["timestamp", "kWh"])
    sheet.append([datetime(2025, 1, 1, 0), 1.25])
    sheet.append([datetime(2025, 1, 1, 1), 2.75])

    book.save(path)

    assert load_total_consumption(path) == 4.0


@pytest.mark.parametrize(
    "filename",
    [
        "missing_column_full.csv",
        "invalid_kwh_full.csv",
        "negative_kwh_full.csv",
        "no_records.csv",
    ],
)
def test_invalid_usage_files_are_rejected(filename):
    """
    Negative test: Supplied invalid CSV files should be rejected.
    These include missing columns, invalid kWh values, negative consumption, and files with no records.
    """
    with pytest.raises(ValueError):
        load_usage_records(HERE / filename)


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

    test_file.write_text("timestamp,kWh\n")

    with pytest.raises(ValueError):
        load_total_consumption(test_file)


def test_unsupported_file_rejected(tmp_path):
    """Negative test: Unsupported file formats should be rejected."""
    path = tmp_path / "usage.txt"
    path.write_text("timestamp,kWh\n2025-01-01,1")

    with pytest.raises(ValueError):
        load_usage_records(path)


def test_missing_file_rejected():
    """Negative test: A missing input file should raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_usage_records(HERE / "missing.csv")


def test_total_consumption_rejects_invalid_file():
    """Negative test: Total consumption should reject invalid usage data."""
    with pytest.raises(ValueError):
        load_total_consumption(HERE / "negative_kwh_full.csv")


# =========================================================
# PERIOD FILTERING TESTS
# =========================================================

def test_filter_period_inclusive():
    """
    Positive boundary test: Both the start and end dates should be included when filtering usage records.
    """
    data = records(
        ("2025-01-01 00:00:00", 1),
        ("2025-01-02 00:00:00", 2),
        ("2025-01-03 00:00:00", 3),
    )

    result = filter_usage_records(
        data,
        "2025-01-02",
        "2025-01-03",
    )

    assert [item["kWh"] for item in result] == [2, 3]


def test_filter_invalid_period_rejected():
    """
    Negative test: The start date cannot be later than the end date.
    """
    with pytest.raises(ValueError):
        filter_usage_records(
            records(("2025-01-01 00:00:00", 1)),
            "2025-01-02",
            "2025-01-01",
        )


def test_filter_empty_and_no_matching_period_rejected():
    """
    Negative tests: Empty input and a date range containing no matching records should both be rejected.
    """
    with pytest.raises(ValueError):
        filter_usage_records([])

    with pytest.raises(ValueError):
        filter_usage_records(
            records(("2025-01-01 00:00:00", 1)),
            "2025-02-01",
            "2025-02-02",
        )


# =========================================================
# FLAT RATE TARIFF TESTS
# =========================================================

@pytest.mark.parametrize(
    "usage,rate,fee,expected",
    [
        (300, 0.25, 10, 85),
        (0, 0.25, 10, 10),
        (125.5, 0.20, 10, 35.1),
        (1_000_000, 0.25, 10, 250010),
        (300, 0, 0, 0),
    ],
)
def test_flat_rate_positive(usage, rate, fee, expected):
    """Positive and boundary tests for flat-rate calculations."""
    assert calculate_flat_rate(usage, rate, fee) == expected


def test_flat_rate_without_fixed_fee():
    """
    Positive test: Check that the function works when there is no fixed fee.
    """
    result = calculate_flat_rate(100, 0.30)

    assert result == 30.00


@pytest.mark.parametrize(
    "args,error",
    [
        ((-1, 0.25, 10), ValueError),
        ((100, -0.25, 10), ValueError),
        ((100, 0.25, -10), ValueError),
        (("bad", 0.25, 10), TypeError),
        ((100, None, 10), TypeError),
    ],
)
def test_flat_rate_negative(args, error):
    """Negative tests for invalid flat-rate inputs."""
    with pytest.raises(error):
        calculate_flat_rate(*args)


def test_flat_breakdown():
    """Positive test: Check the detailed flat-rate cost breakdown."""
    assert calculate_flat_rate_breakdown(
        300,
        0.25,
        10,
    ) == {
        "usage_kwh": 300.0,
        "energy_fee": 75.0,
        "fixed_fee": 10.0,
        "total": 85.0,
    }


def test_flat_breakdown_invalid():
    """Negative test: A negative fixed fee should be rejected."""
    with pytest.raises(ValueError):
        calculate_flat_rate_breakdown(300, 0.25, -1)


# =========================================================
# TIME-OF-USE TARIFF TESTS
# =========================================================

def test_tou_assignment_example():
    """
    Positive test: Check that records are assigned to peak, shoulder, and off-peak periods using the default periods.
    """
    data = records(
        ("2025-01-01 18:00:00", 100),
        ("2025-01-01 12:00:00", 120),
        ("2025-01-01 23:00:00", 80),
    )

    result = calculate_tou_tariff(
        data,
        0.40,
        0.15,
        0.25,
        10,
    )

    assert result["peak"] == {
        "usage_kwh": 100.0,
        "rate": 0.4,
        "cost": 40.0,
    }
    assert result["shoulder"]["cost"] == 30.0
    assert result["off_peak"]["cost"] == 12.0
    assert result["total"] == 92.0


def test_tou_boundaries_and_midnight_crossing():
    """
    Boundary test: Check the exact start and end times of each time-of-use period, including the midnight crossing.
    """
    data = records(
        ("2025-01-01 17:59:00", 1),
        ("2025-01-01 18:00:00", 1),
        ("2025-01-01 21:59:00", 1),
        ("2025-01-01 22:00:00", 1),
        ("2025-01-02 06:59:00", 1),
        ("2025-01-02 07:00:00", 1),
    )

    result = calculate_tou_tariff(
        data,
        0.4,
        0.15,
        0.25,
    )

    assert result["peak"]["usage_kwh"] == 2
    assert result["off_peak"]["usage_kwh"] == 2
    assert result["shoulder"]["usage_kwh"] == 2


def test_tou_custom_periods():
    """Positive test: Check that custom TOU periods are supported."""
    data = records(("2025-01-01 16:00:00", 5))

    result = calculate_tou_tariff(
        data,
        0.5,
        0.1,
        0.2,
        peak_start=time(15),
        peak_end=time(17),
        offpeak_start=time(0),
        offpeak_end=time(6),
    )

    assert result["peak"]["cost"] == 2.5


@pytest.mark.parametrize(
    "records_arg,rates,error",
    [
        ([], (0.4, 0.15, 0.25, 10), ValueError),
        (
            records(("2025-01-01 18:00:00", 1)),
            (-0.4, 0.15, 0.25, 10),
            ValueError,
        ),
        (
            records(("2025-01-01 18:00:00", 1)),
            ("bad", 0.15, 0.25, 10),
            TypeError,
        ),
    ],
)
def test_tou_invalid_inputs(records_arg, rates, error):
    """Negative tests for invalid time-of-use inputs."""
    with pytest.raises(error):
        calculate_tou_tariff(records_arg, *rates)


def test_tou_overlap_rejected():
    """
    Negative test: Overlapping peak and off-peak periods should be rejected.
    """
    with pytest.raises(ValueError):
        calculate_tou_tariff(
            records(("2025-01-01 18:00:00", 1)),
            0.4,
            0.15,
            0.25,
            peak_start=time(18),
            peak_end=time(23),
            offpeak_start=time(22),
            offpeak_end=time(7),
        )


def test_tou_malformed_record_rejected():
    """
    Negative test: A usage record missing the kWh value should be rejected.
    """
    with pytest.raises(ValueError):
        calculate_tou_tariff(
            [{"timestamp": datetime(2025, 1, 1, 18)}],
            0.4,
            0.15,
            0.25,
        )


# =========================================================
# TIERED TARIFF TESTS
# =========================================================

@pytest.mark.parametrize(
    "usage,expected",
    [
        (80, 26),
        (100, 30),
        (200, 60),
        (300, 90),
        (350, 110),
        (0, 10),
    ],
)
def test_tiered_positive(usage, expected):
    """Positive and boundary tests for tiered tariff calculations."""
    assert calculate_tiered_tariff(
        usage,
        100,
        0.20,
        300,
        0.30,
        0.40,
        10,
    ) == expected


@pytest.mark.parametrize(
    "args,error",
    [
        ((-1, 100, 0.2, 300, 0.3, 0.4, 10), ValueError),
        ((350, 100, -0.2, 300, 0.3, 0.4, 10), ValueError),
        ((350, 300, 0.2, 100, 0.3, 0.4, 10), ValueError),
        ((350, 100, 0.2, 300, 0.3, 0.4, -10), ValueError),
        (("bad", 100, 0.2, 300, 0.3, 0.4, 10), TypeError),
    ],
)
def test_tiered_negative(args, error):
    """Negative tests for invalid tiered tariff inputs."""
    with pytest.raises(error):
        calculate_tiered_tariff(*args)


def test_tiered_breakdown():
    """
    Positive test: Check the detailed tier allocation.

    100 kWh -> Tier 1
    200 kWh -> Tier 2
    50 kWh -> Tier 3
    """
    result = calculate_tiered_breakdown(
        350,
        100,
        0.2,
        300,
        0.3,
        0.4,
        10,
    )

    assert [
        result[key]["usage_kwh"]
        for key in ("tier1", "tier2", "tier3")
    ] == [100, 200, 50]

    assert result["energy_fee"] == 100
    assert result["total"] == 110


def test_tiered_breakdown_invalid():
    """Negative test: Invalid tier thresholds should be rejected."""
    with pytest.raises(ValueError):
        calculate_tiered_breakdown(
            350,
            300,
            0.2,
            100,
            0.3,
            0.4,
            10,
        )


# =========================================================
# COMPARISON AND SAVINGS SUGGESTION TESTS
# =========================================================

def test_compare_tariffs_and_savings():
    """Positive test: Check tariff comparison and savings calculation."""
    result = compare_tariffs(
        {
            "Flat": 85,
            "TOU": 92,
            "Tiered": 110,
        }
    )

    assert result["cheapest"] == "Flat"
    assert result["savings"] == {
        "Flat": 0.0,
        "TOU": 7.0,
        "Tiered": 25.0,
    }


@pytest.mark.parametrize(
    "value",
    [
        {},
        {"Only": 10},
        {"A": 10, "B": -1},
    ],
)
def test_compare_invalid(value):
    """Negative test: Invalid tariff comparisons should be rejected."""
    with pytest.raises(ValueError):
        compare_tariffs(value)


def test_suggestions_positive_and_negative():
    """
    Positive and negative tests for saving suggestions.
    The test checks that a cheaper tariff is mentioned and that peak usage is identified as a possible source of savings.
    """
    data = records(
        ("2025-01-01 18:00:00", 3),
        ("2025-01-01 12:00:00", 7),
    )

    tou = calculate_tou_tariff(
        data,
        0.4,
        0.15,
        0.25,
    )

    comparison = compare_tariffs(
        {
            "Flat": 3,
            "TOU": 4,
        }
    )

    suggestions = generate_saving_suggestions(
        data,
        tou,
        comparison,
    )

    assert "Flat" in suggestions[0]
    assert any("Peak usage" in item for item in suggestions)

    with pytest.raises(ValueError):
        generate_saving_suggestions([], tou, comparison)

    with pytest.raises(ValueError):
        generate_saving_suggestions(data, tou, {})


# =========================================================
# PROVIDED XPOWER DATASET / INTEGRATION TESTS
# =========================================================

def test_provided_dataset_total_consumption():
    """
    Integration test: Check that the supplied XPower dataset can be read and produces the expected total electricity
                                                        usage.
    The supplied file contains 850.67 kWh in total.
    """
    csv_file = HERE / "sample_usage_data_month.csv"

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
    csv_file = HERE / "sample_usage_data_month.csv"

    consumption = load_total_consumption(csv_file)

    result = calculate_flat_rate(
        consumption,
        0.25,
        10,
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
    csv_file = HERE / "sample_usage_data_month.csv"

    consumption = load_total_consumption(csv_file)

    result = calculate_tiered_tariff(
        consumption,
        100,
        0.20,
        300,
        0.30,
        0.40,
        10,
    )

    assert result == 310.27


def test_supplied_dataset_all_tariffs():
    """
    Integration test: Verify all supported tariff calculations against the supplied monthly dataset.
    """
    data = load_usage_records(HERE / "sample_usage_data_month.csv")
    total = sum(item["kWh"] for item in data)

    assert calculate_flat_rate(total, 0.25, 10) == 222.67
    assert calculate_tiered_tariff(
        total,
        100,
        0.2,
        300,
        0.3,
        0.4,
        10,
    ) == 310.27

    tou = calculate_tou_tariff(
        data,
        0.4,
        0.15,
        0.25,
        10,
    )

    assert tou["total"] == 244.16


# =========================================================
# FULL-LENGTH INVALID DATASET TESTS
# =========================================================

def test_missing_column_full_length():
    """
    Negative test: A full-length 720-row file with the wrong column name ('usage' instead of 'kWh') should still be
                                                        rejected.
    """
    csv_file = HERE / "missing_column_full.csv"

    with pytest.raises(ValueError):
        load_total_consumption(csv_file)


def test_invalid_kwh_full_length():
    """
    Negative test: A full-length file with one non-numeric kWh value buried partway through should still be rejected.
    """
    csv_file = HERE / "invalid_kwh_full.csv"

    with pytest.raises(ValueError):
        load_total_consumption(csv_file)


def test_negative_kwh_full_length():
    """
    Negative test: A full-length file with one negative kWh value buried partway through should still be rejected.
    """
    csv_file = HERE / "negative_kwh_full.csv"

    with pytest.raises(ValueError):
        load_total_consumption(csv_file)


def test_no_records_rejected():
    """
    Negative test: A CSV with headers but zero usage records should be rejected.
    """
    csv_file = HERE / "no_records.csv"

    with pytest.raises(ValueError):
        load_total_consumption(csv_file)