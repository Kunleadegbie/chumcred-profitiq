import pandas as pd
import numpy as np


def safe_numeric(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)


def safe_date(series):
    return pd.to_datetime(series, errors="coerce")


def filter_by_review_period(df, date_col, start_date=None, end_date=None):
    if df is None or df.empty:
        return pd.DataFrame()

    if date_col not in df.columns:
        return df.copy()

    data = df.copy()
    data[date_col] = safe_date(data[date_col])
    data = data.dropna(subset=[date_col])

    if start_date:
        data = data[data[date_col] >= pd.to_datetime(start_date)]

    if end_date:
        data = data[data[date_col] <= pd.to_datetime(end_date)]

    return data


def generate_period_trend(df, date_col, value_col, frequency="Monthly"):
    if df is None or df.empty:
        return pd.DataFrame()

    if date_col not in df.columns or value_col not in df.columns:
        return pd.DataFrame()

    data = df.copy()
    data[date_col] = safe_date(data[date_col])
    data[value_col] = safe_numeric(data[value_col])
    data = data.dropna(subset=[date_col])

    if data.empty:
        return pd.DataFrame()

    if frequency == "Yearly":
        data["Period"] = data[date_col].dt.year.astype(str)
    elif frequency == "Quarterly":
        data["Period"] = data[date_col].dt.to_period("Q").astype(str)
    else:
        data["Period"] = data[date_col].dt.to_period("M").astype(str)

    trend_df = (
        data.groupby("Period", as_index=False)[value_col]
        .sum()
        .sort_values("Period")
    )

    trend_df["Previous Period Value"] = trend_df[value_col].shift(1)
    trend_df["Growth Amount"] = trend_df[value_col] - trend_df["Previous Period Value"]
    trend_df["Growth %"] = np.where(
        trend_df["Previous Period Value"] > 0,
        trend_df["Growth Amount"] / trend_df["Previous Period Value"] * 100,
        0,
    )

    return trend_df


def calculate_cagr(start_value, end_value, years):
    if start_value <= 0 or end_value <= 0 or years <= 0:
        return 0

    return ((end_value / start_value) ** (1 / years) - 1) * 100


def generate_multiyear_summary(trend_df, value_col):
    if trend_df is None or trend_df.empty or value_col not in trend_df.columns:
        return {}

    first_value = float(trend_df[value_col].iloc[0])
    last_value = float(trend_df[value_col].iloc[-1])
    periods = len(trend_df)

    years = max(periods / 12, 1)

    if len(trend_df["Period"].astype(str).str[:4].unique()) > 1:
        years = max(
            len(trend_df["Period"].astype(str).str[:4].unique()) - 1,
            1,
        )

    total_value = float(trend_df[value_col].sum())
    average_value = float(trend_df[value_col].mean())
    growth_amount = last_value - first_value
    growth_percent = (growth_amount / first_value * 100) if first_value > 0 else 0
    cagr = calculate_cagr(first_value, last_value, years)

    best_period_row = trend_df.loc[trend_df[value_col].idxmax()]
    worst_period_row = trend_df.loc[trend_df[value_col].idxmin()]

    return {
        "total_value": total_value,
        "average_value": average_value,
        "first_period_value": first_value,
        "last_period_value": last_value,
        "growth_amount": growth_amount,
        "growth_percent": growth_percent,
        "cagr": cagr,
        "best_period": best_period_row["Period"],
        "best_period_value": float(best_period_row[value_col]),
        "worst_period": worst_period_row["Period"],
        "worst_period_value": float(worst_period_row[value_col]),
    }