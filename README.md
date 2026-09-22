# XPower Household Tariff Analysis Prototype

This prototype imports hourly or daily electricity usage, filters a selected billing period, calculates Flat Rate, Time-of-Use (TOU), and Tiered bills, compares their costs, displays detailed energy and fixed-fee breakdowns, charts usage and bills, and provides transparent cost-saving suggestions.

## Required file format

Upload a `.csv` or `.xlsx` file containing these exact columns:

```text
timestamp,kWh
2025-01-01 00:00:00,0.25
```

Timestamps may use ISO `YYYY-MM-DD HH:MM:SS` or common Australian `DD/MM/YYYY` formats. Electricity usage must be numeric and non-negative.

## Install and run

```bash
python -m pip install -r requirements.txt
python xpower_app.py
```

Use **Upload CSV or Excel**, confirm or change the date range and tariff settings, and select **Run Tariff Analysis**. The Bill Results tab provides the detailed comparison and suggestions. The Charts tab displays the usage trend and bill breakdown.

For a command-line demonstration using the supplied data:

```bash
python run_analysis.py
```

## Run the tests

```bash
python -m pytest -v
```

The completed test suite contains 64 positive, boundary, negative, and integration tests. All 50 tests pass against the supplied dataset and invalid-file fixtures.

## Supplied dataset results

- Total usage: 850.67 kWh across 720 hourly records.
- Flat Rate: $222.67 at $0.25/kWh plus a $10 fixed fee.
- Time-of-Use: $244.16 using Peak $0.40, Off-Peak $0.15, Shoulder $0.25, and a $10 fixed fee.
- Tiered: $310.27 using the assignment's three tiers and a $10 fixed fee.
- Cheapest under these example settings: Flat Rate, saving $21.49 compared with TOU and $87.60 compared with Tiered.

These figures are estimates produced from the supplied data and entered rates. Users should confirm actual tariff terms and fees with their electricity provider.