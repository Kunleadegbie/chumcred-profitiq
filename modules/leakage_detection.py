import pandas as pd
from modules.calculations import safe_numeric


def detect_duplicates(df, amount_col=None, date_col=None, vendor_col=None, desc_col=None):
    data = df.copy()
    subset_cols = []

    for col in [date_col, vendor_col, desc_col, amount_col]:
        if col and col != "None" and col in data.columns:
            subset_cols.append(col)

    if not subset_cols:
        return pd.DataFrame()

    return data[data.duplicated(subset=subset_cols, keep=False)]


def detect_high_value_outliers(df, amount_col, multiplier=2.5):
    data = df.copy()
    data[amount_col] = safe_numeric(data[amount_col])

    avg_value = data[amount_col].mean()
    threshold = avg_value * multiplier

    return data[data[amount_col] > threshold]


def create_leakage_item(area, observation, estimated_value, recommendation, priority):
    return {
        "Leakage Area": area,
        "Observation": observation,
        "Estimated Leakage Exposure": float(estimated_value) if estimated_value else 0,
        "Recommended Action": recommendation,
        "Priority": priority,
    }


def detect_collection_gaps(df, expected_col, collected_col):
    data = df.copy()
    data[expected_col] = safe_numeric(data[expected_col])
    data[collected_col] = safe_numeric(data[collected_col])
    data["Collection Gap"] = data[expected_col] - data[collected_col]

    return data[data["Collection Gap"] > 0]


def detect_excessive_discounts(df, discount_col, multiplier=2):
    data = df.copy()
    data[discount_col] = safe_numeric(data[discount_col])
    threshold = data[discount_col].mean() * multiplier

    return data[data[discount_col] > threshold]


def detect_inventory_losses(df, expected_stock_col, actual_stock_col, unit_value_col=None):
    data = df.copy()
    data[expected_stock_col] = safe_numeric(data[expected_stock_col])
    data[actual_stock_col] = safe_numeric(data[actual_stock_col])
    data["Stock Variance"] = data[expected_stock_col] - data[actual_stock_col]

    losses = data[data["Stock Variance"] > 0].copy()

    if unit_value_col and unit_value_col != "None":
        losses[unit_value_col] = safe_numeric(losses[unit_value_col])
        losses["Estimated Loss Value"] = losses["Stock Variance"] * losses[unit_value_col]

    return losses