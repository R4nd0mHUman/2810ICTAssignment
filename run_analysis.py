"""
Not a test. Just to prove that the supplied electricity data is being imported and analysed.
"""
from tariff_functions import load_total_consumption
from tariff_functions import calculate_flat_rate
from tariff_functions import calculate_tiered_tariff


# Name of the electricity usage file supplied with the assignment.
file_name = "sample_usage_data_month.csv"


# =========================================================
# LOAD ELECTRICITY DATA
# =========================================================

total_consumption = load_total_consumption(file_name)

print("XPower Household Tariff Analysis")
print("--------------------------------")
print(f"Total electricity usage: {total_consumption:.2f} kWh")


# =========================================================
# FLAT RATE TARIFF
# =========================================================

flat_rate = 0.25
flat_fixed_fee = 10

flat_bill = calculate_flat_rate(
    total_consumption,
    flat_rate,
    flat_fixed_fee
)

print()
print("Flat Rate Tariff")
print(f"Rate: ${flat_rate:.2f}/kWh")
print(f"Fixed fee: ${flat_fixed_fee:.2f}")
print(f"Total bill: ${flat_bill:.2f}")


# =========================================================
# TIERED TARIFF
# =========================================================

tiered_bill = calculate_tiered_tariff(
    total_consumption,
    100,
    0.20,
    300,
    0.30,
    0.40,
    10
)

print()
print("Tiered Tariff")
print("Tier 1: First 100 kWh at $0.20/kWh")
print("Tier 2: 101-300 kWh at $0.30/kWh")
print("Tier 3: Above 300 kWh at $0.40/kWh")
print("Fixed fee: $10.00")
print(f"Total bill: ${tiered_bill:.2f}")


# =========================================================
# COST COMPARISON
# =========================================================

difference = abs(flat_bill - tiered_bill)

print()
print("Tariff Comparison")

if flat_bill < tiered_bill:
    print("The Flat Rate Tariff is cheaper.")
    print(f"Savings: ${difference:.2f}")

elif tiered_bill < flat_bill:
    print("The Tiered Tariff is cheaper.")
    print(f"Savings: ${difference:.2f}")

else:
    print("Both tariffs cost the same.")