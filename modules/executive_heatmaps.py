import pandas as pd


# ==========================================================
# HELPER
# ==========================================================
def safe_number(value):
    try:
        return float(value)
    except Exception:
        return 0


# ==========================================================
# BRANCH RISK HEATMAP
# ==========================================================
def generate_branch_risk_heatmap(
    branch_df,
    branch_col,
    revenue_col,
    target_col=None,
    profit_col=None,
):
    if branch_df is None or branch_df.empty:
        return pd.DataFrame()

    df = branch_df.copy()

    df[revenue_col] = pd.to_numeric(
        df[revenue_col],
        errors="coerce",
    ).fillna(0)

    if target_col:
        df[target_col] = pd.to_numeric(
            df[target_col],
            errors="coerce",
        ).fillna(0)

        df["Target Achievement %"] = df.apply(
            lambda x: (
                (x[revenue_col] / x[target_col]) * 100
                if x[target_col] > 0
                else 0
            ),
            axis=1,
        )

    else:
        df["Target Achievement %"] = 100

    if profit_col:
        df[profit_col] = pd.to_numeric(
            df[profit_col],
            errors="coerce",
        ).fillna(0)

        df["Profitability Score"] = df[profit_col]

    else:
        df["Profitability Score"] = df[revenue_col]

    # ======================================================
    # RISK SCORE
    # ======================================================
    def assign_risk(row):
        achievement = row["Target Achievement %"]

        if achievement >= 100:
            return "Low Risk"

        elif achievement >= 80:
            return "Moderate Risk"

        elif achievement >= 60:
            return "High Risk"

        else:
            return "Critical Risk"

    df["Risk Level"] = df.apply(assign_risk, axis=1)

    result = df[
        [
            branch_col,
            revenue_col,
            "Target Achievement %",
            "Profitability Score",
            "Risk Level",
        ]
    ].copy()

    return result


# ==========================================================
# COST CONCENTRATION HEATMAP
# ==========================================================
def generate_cost_concentration_heatmap(
    expense_df,
    category_col,
    amount_col,
):
    if expense_df is None or expense_df.empty:
        return pd.DataFrame()

    df = expense_df.copy()

    df[amount_col] = pd.to_numeric(
        df[amount_col],
        errors="coerce",
    ).fillna(0)

    summary = (
        df.groupby(category_col, as_index=False)[amount_col]
        .sum()
        .sort_values(amount_col, ascending=False)
    )

    total_cost = summary[amount_col].sum()

    summary["Cost Share %"] = summary[amount_col].apply(
        lambda x: (x / total_cost * 100)
        if total_cost > 0
        else 0
    )

    def assign_concentration_level(value):
        if value >= 30:
            return "Critical"

        elif value >= 20:
            return "High"

        elif value >= 10:
            return "Moderate"

        else:
            return "Low"

    summary["Concentration Risk"] = summary["Cost Share %"].apply(
        assign_concentration_level
    )

    return summary


# ==========================================================
# LEAKAGE RISK MATRIX
# ==========================================================
def generate_leakage_risk_matrix(leakage_df):
    if leakage_df is None or leakage_df.empty:
        return pd.DataFrame()

    df = leakage_df.copy()

    value_col = None

    for candidate in [
        "Estimated Leakage Exposure",
        "Estimated Impact",
    ]:
        if candidate in df.columns:
            value_col = candidate
            break

    if value_col is None:
        return pd.DataFrame()

    df[value_col] = pd.to_numeric(
        df[value_col],
        errors="coerce",
    ).fillna(0)

    priority_col = (
        "Priority"
        if "Priority" in df.columns
        else None
    )

    if priority_col is None:
        df["Priority"] = "Review"

    def assign_leakage_score(row):
        value = row[value_col]
        priority = row["Priority"]

        if priority == "High" and value >= 1_000_000:
            return "Critical"

        elif priority == "High":
            return "High"

        elif priority == "Medium":
            return "Moderate"

        else:
            return "Low"

    df["Leakage Risk Level"] = df.apply(
        assign_leakage_score,
        axis=1,
    )

    return df


# ==========================================================
# PROFITABILITY HEATMAP
# ==========================================================
def generate_profitability_heatmap(
    sales_df,
    product_col,
    revenue_col,
):
    if sales_df is None or sales_df.empty:
        return pd.DataFrame()

    df = sales_df.copy()

    df[revenue_col] = pd.to_numeric(
        df[revenue_col],
        errors="coerce",
    ).fillna(0)

    summary = (
        df.groupby(product_col, as_index=False)[revenue_col]
        .sum()
        .sort_values(revenue_col, ascending=False)
    )

    total_revenue = summary[revenue_col].sum()

    summary["Revenue Share %"] = summary[revenue_col].apply(
        lambda x: (x / total_revenue * 100)
        if total_revenue > 0
        else 0
    )

    def assign_profitability_level(value):
        if value >= 25:
            return "High Profitability"

        elif value >= 10:
            return "Moderate Profitability"

        else:
            return "Low Profitability"

    summary["Profitability Level"] = summary["Revenue Share %"].apply(
        assign_profitability_level
    )

    return summary