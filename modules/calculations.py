import pandas as pd


def safe_numeric(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)


def format_naira(value):
    try:
        return f"₦{float(value):,.0f}"
    except Exception:
        return "₦0"


def calculate_percentage(part, whole):
    if whole == 0:
        return 0
    return (part / whole) * 100


def monthly_summary(df, date_col, amount_col):
    data = df.copy()
    data[date_col] = pd.to_datetime(data[date_col], errors="coerce")
    data[amount_col] = safe_numeric(data[amount_col])
    data = data.dropna(subset=[date_col])
    data["Month"] = data[date_col].dt.to_period("M").astype(str)

    return (
        data.groupby("Month", as_index=False)[amount_col]
        .sum()
        .sort_values("Month")
    )


def detect_growth_rate(current_value, previous_value):
    if previous_value == 0:
        return 0
    return ((current_value - previous_value) / previous_value) * 100