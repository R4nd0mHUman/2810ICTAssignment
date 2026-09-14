import csv


def load_total_consumption(file_path):
    """
    Read household electricity usage from a CSV file and return the total electricity consumption in kWh.

    The CSV file must contain:
        - timestamp
        - kWh

    Parameters:
        - file_path (str): Path to the electricity usage CSV file.

    Returns:
        - float: Total electricity consumption in kWh.

    Raises:
        - ValueError: If the required columns are missing.
        - ValueError: If a kWh value is not a valid number.
        - ValueError: If a kWh value is negative.
        - ValueError: If the file contains no usage records.
    """

    total_consumption = 0.0
    record_count = 0

    with open(file_path, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        # Check that the CSV has a header row.
        if reader.fieldnames is None:
            raise ValueError("CSV file is empty or has no header row.")

        required_columns = {"timestamp", "kWh"}

        # Check that the required columns exist.
        if not required_columns.issubset(reader.fieldnames):
            raise ValueError("CSV file must contain 'timestamp' and 'kWh' columns.")

        # Read each electricity usage record.
        for row in reader:
            try:
                consumption = float(row["kWh"])
            except (TypeError, ValueError):
                raise ValueError("All kWh values must be valid numbers.")

            if consumption < 0:
                raise ValueError("Electricity consumption in the CSV cannot be negative.")

            total_consumption += consumption
            record_count += 1

    # Make sure the CSV actually contained usage data.
    if record_count == 0:
        raise ValueError("CSV file contains no electricity usage records.")

    return round(total_consumption, 2)


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
    - TypeError: If consumption, rate, or fixed_fee is not a number.
    - ValueError: If consumption, rate, or fixed_fee is negative.
    """
    # Type checks first — bool is a subclass of int in Python, so we
    # explicitly exclude it to stop True/False being treated as 1/0.
    for name, value in (("consumption", consumption), ("rate", rate), ("fixed_fee", fixed_fee)):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be a number.")

    if consumption < 0:
        raise ValueError("Consumption cannot be negative.")
    if rate < 0:
        raise ValueError("Rate cannot be negative.")
    if fixed_fee < 0:
        raise ValueError("Fixed fee cannot be negative.")

    energy_cost = consumption * rate
    total_bill = energy_cost + fixed_fee

    return round(total_bill, 2)