import pandas as pd
from modules.calculations import safe_numeric


def cost_by_dimension(df, dimension_col, amount_col):
    data = df.copy()
    data[amount_col] = safe_numeric(data[amount_col])

    return (
        data.groupby(dimension_col, as_index=False)[amount_col]
        .sum()
        .sort_values(amount_col, ascending=False)
    )


def calculate_cost_to_revenue(total_cost, total_revenue):
    if total_revenue == 0:
        return 0
    return (total_cost / total_revenue) * 100


def create_cost_saving_item(area, observation, estimated_saving, recommendation, priority):
    return {
        "Cost Area": area,
        "Observation": observation,
        "Estimated Cost Saving": float(estimated_saving) if estimated_saving else 0,
        "Recommended Action": recommendation,
        "Priority": priority,
    }


def detect_high_cost_concentration(category_cost_df, category_col, amount_col, total_expense):
    if category_cost_df.empty or total_expense == 0:
        return None

    top_category = category_cost_df.iloc[0]
    share = (top_category[amount_col] / total_expense) * 100

    if share >= 30:
        return create_cost_saving_item(
            "High Cost Concentration",
            f"{top_category[category_col]} accounts for {share:.1f}% of total reviewed expenses.",
            top_category[amount_col] * 0.10,
            "Review contracts, usage pattern, pricing, approval limits, and alternative suppliers.",
            "High",
        )

    return None


def detect_high_cost_units(unit_cost_df, unit_col, amount_col):
    if unit_cost_df.empty:
        return None

    avg_cost = unit_cost_df[amount_col].mean()
    high_cost_units = unit_cost_df[unit_cost_df[amount_col] > avg_cost * 1.5]

    if not high_cost_units.empty:
        return create_cost_saving_item(
            "High-Cost Department / Branch",
            f"{len(high_cost_units)} departments/branches are spending more than 1.5x the average cost level.",
            high_cost_units[amount_col].sum() * 0.08,
            "Review operational efficiency, staff productivity, procurement discipline, and approval controls.",
            "Medium",
        )

    return None