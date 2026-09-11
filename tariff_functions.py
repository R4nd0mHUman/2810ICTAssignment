def calculate_flat_rate(consumption, rate, fixed_fee=0):
    """
    Calculate an electricity bill using a flat rate tariff.

    Parameters:
        - consumption (float): Electricity consumed in kWh.
        - rate (float): Price per kWh.
        - fixed_fee (float): Fixed supply fee.

    Returns:
        - float: Total electricity bill.

    Raises:
        - ValueError: If consumption, rate, or fixed_fee is negative.
    """

    if consumption < 0:
        raise ValueError("Consumption cannot be negative.")

    if rate < 0:
        raise ValueError("Rate cannot be negative.")

    if fixed_fee < 0:
        raise ValueError("Fixed fee cannot be negative.")

    energy_cost = consumption * rate
    total_bill = energy_cost + fixed_fee

    return round(total_bill, 2)


def calculate_tiered_tariff(
    consumption,
    tier1_limit,
    tier1_rate,
    tier2_limit,
    tier2_rate,
    tier3_rate,
    fixed_fee=0
):
    """
    Calculate an electricity bill using a three-tier tariff.

    - Tier 1: Usage from 0 kWh up to tier1_limit.
    - Tier 2: Usage above tier1_limit up to tier2_limit.
    - Tier 3: Usage above tier2_limit.

    Parameters:
        - consumption (float): Total electricity consumption in kWh.
        - tier1_limit (float): Upper limit of Tier 1.
        - tier1_rate (float): Price per kWh for Tier 1.
        - tier2_limit (float): Upper limit of Tier 2.
        - tier2_rate (float): Price per kWh for Tier 2.
        - tier3_rate (float): Price per kWh for Tier 3.
        - fixed_fee (float): Fixed supply fee.

    Returns:
        - float: Total electricity bill.

    Raises:
        - ValueError: If input values are invalid.
    """

    if consumption < 0:
        raise ValueError("Consumption cannot be negative.")

    if tier1_limit < 0 or tier2_limit < 0:
        raise ValueError("Tier limits cannot be negative.")

    if tier2_limit <= tier1_limit:
        raise ValueError("Tier 2 limit must be greater than Tier 1 limit.")

    if tier1_rate < 0 or tier2_rate < 0 or tier3_rate < 0:
        raise ValueError("Tariff rates cannot be negative.")

    if fixed_fee < 0:
        raise ValueError("Fixed fee cannot be negative.")

    # Tier 1 only
    if consumption <= tier1_limit:
        energy_cost = consumption * tier1_rate

    # Tier 1 + Tier 2
    elif consumption <= tier2_limit:
        tier1_cost = tier1_limit * tier1_rate

        tier2_usage = consumption - tier1_limit
        tier2_cost = tier2_usage * tier2_rate

        energy_cost = tier1_cost + tier2_cost

    # Tier 1 + Tier 2 + Tier 3
    else:
        tier1_cost = tier1_limit * tier1_rate

        tier2_usage = tier2_limit - tier1_limit
        tier2_cost = tier2_usage * tier2_rate

        tier3_usage = consumption - tier2_limit
        tier3_cost = tier3_usage * tier3_rate

        energy_cost = tier1_cost + tier2_cost + tier3_cost

    total_bill = energy_cost + fixed_fee

    return round(total_bill, 2)