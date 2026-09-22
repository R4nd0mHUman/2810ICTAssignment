"""
                            Command-line demonstration of every XPower tariff model.
Not a test. This script demonstrates that the supplied electricity data can be imported, analysed, and used to
                                calculate the different XPower tariff options.
"""

from datetime import time # Provides the time type for defining peak and off-peak tariff periods.
from pathlib import Path # Provides tools for locating the supplied electricity usage data file.

# Imports the XPower functions used to calculate and compare the different tariffs.
from tariff_functions import (
    calculate_flat_rate_breakdown,
    calculate_tiered_breakdown,
    calculate_tou_tariff,
    compare_tariffs,
    generate_saving_suggestions,
    load_usage_records,
)


# Name and location of the electricity usage file supplied with the assignment.
# Path(__file__) ensures the file is found relative to this Python script.
DATA_FILE = Path(__file__).with_name("sample_usage_data_month.csv")


def main():
    # =========================================================
    # LOAD ELECTRICITY DATA
    # =========================================================

    # Load all electricity usage records from the supplied dataset.
    # Each record contains a timestamp and the corresponding kWh usage.
    records = load_usage_records(DATA_FILE)

    # Calculate the total electricity consumption from all records.
    # The supplied dataset contains 720 usage records.
    total_usage = round(sum(record["kWh"] for record in records), 2)

    # Fixed supply fee used by the tariff calculations.
    fixed_fee = 10.0

    print("XPower Household Tariff Analysis")
    print("=" * 34)
    print(f"Records: {len(records)}")
    print(f"Total usage: {total_usage:.2f} kWh\n")


    # =========================================================
    # FLAT RATE TARIFF
    # =========================================================

    # Calculate the flat-rate electricity bill.
    #
    # Flat rate:
    # $0.25 per kWh
    # Fixed fee: $10.00
    #
    # The breakdown function provides the energy charge, fixed fee,
    # and final total separately.
    flat = calculate_flat_rate_breakdown(
        total_usage,
        0.25,
        fixed_fee,
    )

    print(
        f"Flat Rate: energy ${flat['energy_fee']:.2f} "
        f"+ fixed ${flat['fixed_fee']:.2f} "
        f"= ${flat['total']:.2f}"
    )


    # =========================================================
    # TIME-OF-USE TARIFF
    # =========================================================

    # Calculate the Time-of-Use (TOU) electricity bill.
    #
    # Peak period:
    # 6:00 PM to 10:00 PM at $0.40/kWh
    #
    # Off-peak period:
    # 10:00 PM to 7:00 AM at $0.15/kWh
    #
    # Shoulder period:
    # The remaining hours at $0.25/kWh
    #
    # The individual usage records are required here because the price depends on the time at which electricity was
    #                                                   consumed.
    tou = calculate_tou_tariff(
        records,
        peak_rate=0.40,
        offpeak_rate=0.15,
        shoulder_rate=0.25,
        fixed_fee=fixed_fee,
        peak_start=time(18),
        peak_end=time(22),
        offpeak_start=time(22),
        offpeak_end=time(7),
    )

    print("Time-of-Use:")

    # Display the electricity usage and cost for each TOU period.
    for name in ("peak", "off_peak", "shoulder"):
        item = tou[name]

        print(
            f"  {name.replace('_', ' ').title()}: "
            f"{item['usage_kwh']:.2f} kWh x "
            f"${item['rate']:.2f} = "
            f"${item['cost']:.2f}"
        )

    print(
        f"  Energy ${tou['energy_fee']:.2f} "
        f"+ fixed ${tou['fixed_fee']:.2f} "
        f"= ${tou['total']:.2f}"
    )


    # =========================================================
    # TIERED TARIFF
    # =========================================================

    # Calculate the tiered electricity bill.
    #
    # Tier 1:
    # First 100 kWh at $0.20/kWh
    #
    # Tier 2:
    # Next 200 kWh (up to 300 kWh total) at $0.30/kWh
    #
    # Tier 3:
    # Any usage above 300 kWh at $0.40/kWh
    #
    # Fixed fee: $10.00
    tiered = calculate_tiered_breakdown(
        total_usage,
        100,
        0.20,
        300,
        0.30,
        0.40,
        fixed_fee,
    )

    print("Tiered:")

    # Display how much electricity was charged in each tier.
    for name in ("tier1", "tier2", "tier3"):
        item = tiered[name]

        print(
            f"  {name.title()}: "
            f"{item['usage_kwh']:.2f} kWh x "
            f"${item['rate']:.2f} = "
            f"${item['cost']:.2f}"
        )

    print(
        f"  Energy ${tiered['energy_fee']:.2f} "
        f"+ fixed ${tiered['fixed_fee']:.2f} "
        f"= ${tiered['total']:.2f}\n"
    )


    # =========================================================
    # COST COMPARISON
    # =========================================================

    # Compare the total cost of all three tariff options.
    comparison = compare_tariffs(
        {
            "Flat Rate": flat["total"],
            "Time-of-Use": tou["total"],
            "Tiered": tiered["total"],
        }
    )

    # Display the tariff with the lowest calculated total cost.
    print(
        f"Cheapest: {comparison['cheapest']} "
        f"(${comparison['cheapest_total']:.2f})"
    )


    # =========================================================
    # SAVING SUGGESTIONS
    # =========================================================

    # Generate suggestions based on the household's usage records, the Time-of-Use breakdown, and the tariff comparison.
    # These suggestions can identify opportunities to reduce costs, such as reducing electricity consumption during
    #                                               peak periods.
    for suggestion in generate_saving_suggestions(
        records,
        tou,
        comparison,
    ):
        print(f"- {suggestion}")


# Run the demonstration when this file is executed directly.
if __name__ == "__main__":
    main()