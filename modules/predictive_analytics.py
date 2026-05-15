import pandas as pd
import numpy as np


def safe_numeric(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)


def prepare_monthly_series(df, date_col, value_col):
    import pandas as pd

    if df is None or df.empty:
        return pd.DataFrame()

    # ------------------------------------------------------
    # REMOVE DUPLICATE COLUMNS
    # ------------------------------------------------------
    df = df.loc[:, ~df.columns.duplicated()].copy()

    # ------------------------------------------------------
    # VALIDATE COLUMNS
    # ------------------------------------------------------
    if date_col not in df.columns:
        return pd.DataFrame()

    if value_col not in df.columns:
        return pd.DataFrame()

    # ------------------------------------------------------
    # FORCE SERIES (NOT DATAFRAME)
    # ------------------------------------------------------
    date_series = df[date_col]

    if isinstance(date_series, pd.DataFrame):
        date_series = date_series.iloc[:, 0]

    value_series = df[value_col]

    if isinstance(value_series, pd.DataFrame):
        value_series = value_series.iloc[:, 0]

    # ------------------------------------------------------
    # BUILD CLEAN DATAFRAME
    # ------------------------------------------------------
    data = pd.DataFrame({
        "Date": pd.to_datetime(
            date_series.astype(str),
            errors="coerce",
        ),

        "Value": pd.to_numeric(
            value_series,
            errors="coerce",
        ).fillna(0)
    })

    # ------------------------------------------------------
    # REMOVE INVALID DATES
    # ------------------------------------------------------
    data = data.dropna(subset=["Date"])

    if data.empty:
        return pd.DataFrame()

    # ------------------------------------------------------
    # CREATE MONTH
    # ------------------------------------------------------
    data["Month"] = (
        data["Date"]
        .dt.to_period("M")
        .astype(str)
    )

    # ------------------------------------------------------
    # MONTHLY AGGREGATION
    # ------------------------------------------------------
    monthly = (
        data.groupby("Month", as_index=False)["Value"]
        .sum()
        .sort_values("Month")
    )

    monthly["Period Index"] = range(1, len(monthly) + 1)

    return monthly

def simple_forecast(data, value_col, forecast_periods=3):
    import pandas as pd
    import numpy as np

    if data is None or data.empty:
        return pd.DataFrame()

    # ------------------------------------------------------
    # USE SAFE VALUE COLUMN
    # ------------------------------------------------------
    safe_col = "Value" if "Value" in data.columns else value_col

    if safe_col not in data.columns:
        return pd.DataFrame()

    # ------------------------------------------------------
    # PREPARE X AND Y
    # ------------------------------------------------------
    x = np.arange(len(data))
    y = pd.to_numeric(
        data[safe_col],
        errors="coerce"
    ).fillna(0).values

    if len(y) < 2:
        return pd.DataFrame()

    # ------------------------------------------------------
    # SIMPLE LINEAR TREND
    # ------------------------------------------------------
    slope, intercept = np.polyfit(x, y, 1)

    forecast_rows = []

    for i in range(1, forecast_periods + 1):
        future_x = len(data) + i - 1

        forecast_value = intercept + (slope * future_x)

        forecast_rows.append({
            "Forecast Period": f"Forecast {i}",
            "Forecast Value": max(0, round(float(forecast_value), 2))
        })

    return pd.DataFrame(forecast_rows)


def generate_revenue_forecast(sales_df, date_col, revenue_col, forecast_periods=3):
    monthly_revenue = prepare_monthly_series(sales_df, date_col, revenue_col)
    forecast_df = simple_forecast(monthly_revenue, revenue_col, forecast_periods)

    return monthly_revenue, forecast_df


def generate_cost_forecast(expense_df, date_col, cost_col, forecast_periods=3):
    monthly_cost = prepare_monthly_series(expense_df, date_col, cost_col)
    forecast_df = simple_forecast(monthly_cost, cost_col, forecast_periods)

    return monthly_cost, forecast_df


def generate_profit_forecast(revenue_forecast_df, cost_forecast_df):
    if revenue_forecast_df is None or cost_forecast_df is None:
        return pd.DataFrame()

    if revenue_forecast_df.empty or cost_forecast_df.empty:
        return pd.DataFrame()

    revenue = revenue_forecast_df.copy()
    cost = cost_forecast_df.copy()

    profit_df = pd.DataFrame(
        {
            "Forecast Period": revenue["Forecast Period"],
            "Revenue Forecast": revenue["Forecast Value"],
            "Cost Forecast": cost["Forecast Value"],
        }
    )

    profit_df["Profit Forecast"] = (
        profit_df["Revenue Forecast"] - profit_df["Cost Forecast"]
    )

    return profit_df


def generate_forecast_insights(revenue_forecast_df=None, cost_forecast_df=None, profit_forecast_df=None):
    insights = []

    if revenue_forecast_df is not None and not revenue_forecast_df.empty:
        avg_revenue_forecast = revenue_forecast_df["Forecast Value"].mean()
        insights.append(
            f"Average forecast revenue over the next periods is ₦{avg_revenue_forecast:,.0f}."
        )

    if cost_forecast_df is not None and not cost_forecast_df.empty:
        avg_cost_forecast = cost_forecast_df["Forecast Value"].mean()
        insights.append(
            f"Average forecast cost over the next periods is ₦{avg_cost_forecast:,.0f}."
        )

    if profit_forecast_df is not None and not profit_forecast_df.empty:
        avg_profit_forecast = profit_forecast_df["Profit Forecast"].mean()

        if avg_profit_forecast > 0:
            insights.append(
                f"Average forecast profit is ₦{avg_profit_forecast:,.0f}, indicating positive expected performance."
            )
        else:
            insights.append(
                f"Average forecast profit is ₦{avg_profit_forecast:,.0f}, indicating possible profitability pressure."
            )

    if not insights:
        insights.append(
            "Forecast could not be generated. At least two monthly periods of revenue and cost data are required."
        )

    return insights