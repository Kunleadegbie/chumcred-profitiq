import pandas as pd


def format_naira(value):
    try:
        return f"₦{float(value):,.0f}"
    except Exception:
        return "₦0"


def safe_number(value):
    try:
        return float(value)
    except Exception:
        return 0


# ==========================================================
# REVENUE INSIGHTS
# ==========================================================
def generate_revenue_insights(
    total_revenue=0,
    average_monthly_revenue=0,
    transaction_count=0,
    average_transaction_value=0,
    total_revenue_opportunity=0,
    monthly_revenue_df=None,
):
    insights = []

    insights.append(
        f"The company generated total reviewed revenue of {format_naira(total_revenue)} across {transaction_count:,.0f} transactions."
    )

    insights.append(
        f"Average monthly revenue is {format_naira(average_monthly_revenue)}, while average transaction value is {format_naira(average_transaction_value)}."
    )

    if monthly_revenue_df is not None and not monthly_revenue_df.empty and len(monthly_revenue_df) >= 2:
        value_col = monthly_revenue_df.columns[-1]
        latest = safe_number(monthly_revenue_df.iloc[-1][value_col])
        previous = safe_number(monthly_revenue_df.iloc[-2][value_col])

        if previous > 0:
            growth_rate = ((latest - previous) / previous) * 100

            if growth_rate > 0:
                insights.append(
                    f"Revenue improved by {growth_rate:.1f}% in the latest period, showing positive short-term momentum."
                )
            elif growth_rate < 0:
                insights.append(
                    f"Revenue declined by {abs(growth_rate):.1f}% in the latest period, requiring management attention."
                )
            else:
                insights.append(
                    "Revenue remained flat in the latest period, suggesting the need for stronger growth actions."
                )

    if total_revenue_opportunity > 0:
        insights.append(
            f"The analysis identified estimated revenue improvement potential of {format_naira(total_revenue_opportunity)}."
        )
    else:
        insights.append(
            "No major automated revenue opportunity was quantified, but deeper review may still reveal pricing, customer, product, or branch growth opportunities."
        )

    return insights


# ==========================================================
# LEAKAGE INSIGHTS
# ==========================================================
def generate_leakage_insights(total_leakage_exposure=0, leakage_df=None):
    insights = []

    if leakage_df is not None and not leakage_df.empty:
        high_priority = leakage_df[leakage_df.get("Priority", "") == "High"] if "Priority" in leakage_df.columns else pd.DataFrame()

        insights.append(
            f"The leakage review identified estimated exposure of {format_naira(total_leakage_exposure)}."
        )

        if not high_priority.empty:
            insights.append(
                f"{len(high_priority)} high-priority leakage issue(s) require immediate validation and management action."
            )

        if "Leakage Area" in leakage_df.columns:
            top_area = leakage_df.iloc[0]["Leakage Area"]
            insights.append(
                f"The first area requiring review is: {top_area}."
            )
    else:
        insights.append(
            "No major leakage was automatically detected from the uploaded data."
        )

    insights.append(
        "All leakage findings should be validated with source documents, approvals, invoices, bank statements, and operational records."
    )

    return insights


# ==========================================================
# COST INSIGHTS
# ==========================================================
def generate_cost_insights(total_cost_saving=0, cost_saving_df=None):
    insights = []

    if total_cost_saving > 0:
        insights.append(
            f"The cost review identified estimated savings potential of {format_naira(total_cost_saving)}."
        )
    else:
        insights.append(
            "No major automated cost-saving opportunity was quantified from the current data."
        )

    if cost_saving_df is not None and not cost_saving_df.empty:
        if "Priority" in cost_saving_df.columns:
            high_priority = cost_saving_df[cost_saving_df["Priority"] == "High"]

            if not high_priority.empty:
                insights.append(
                    f"{len(high_priority)} high-priority cost issue(s) should be reviewed first."
                )

        if "Cost Area" in cost_saving_df.columns:
            top_area = cost_saving_df.iloc[0]["Cost Area"]
            insights.append(
                f"The first cost area requiring attention is: {top_area}."
            )

    insights.append(
        "Cost-saving actions should protect service quality, revenue generation, customer experience, and operational continuity."
    )

    return insights


# ==========================================================
# EXECUTIVE DASHBOARD INSIGHTS
# ==========================================================
def generate_executive_dashboard_insights(
    total_revenue_opportunity=0,
    total_leakage_exposure=0,
    total_cost_saving=0,
    priority_df=None,
):
    insights = []

    total_revenue_opportunity = safe_number(total_revenue_opportunity)
    total_leakage_exposure = safe_number(total_leakage_exposure)
    total_cost_saving = safe_number(total_cost_saving)

    profit_improvement = (
        total_revenue_opportunity + total_leakage_exposure + total_cost_saving
    )

    insights.append(
        f"The combined estimated profit improvement potential is {format_naira(profit_improvement)}."
    )

    impact_components = {
        "Revenue Opportunity": total_revenue_opportunity,
        "Leakage Exposure": total_leakage_exposure,
        "Cost Saving Potential": total_cost_saving,
    }

    top_component = max(impact_components, key=impact_components.get)

    if impact_components[top_component] > 0:
        insights.append(
            f"The largest value driver is {top_component}, contributing {format_naira(impact_components[top_component])}."
        )

    if priority_df is not None and not priority_df.empty:
        insights.append(
            f"The dashboard has identified {len(priority_df)} priority action(s) for management tracking."
        )

        if "Priority" in priority_df.columns:
            high_priority = priority_df[priority_df["Priority"] == "High"]
            if not high_priority.empty:
                insights.append(
                    f"{len(high_priority)} high-priority action(s) should be treated as urgent in the 90-day execution plan."
                )

    insights.append(
        "Management should focus on quick wins, leakage validation, cost discipline, and weekly performance tracking."
    )

    return insights


# ==========================================================
# EXECUTIVE REPORT NARRATIVE
# ==========================================================
def generate_report_narrative(
    company_name,
    total_revenue_opportunity=0,
    total_leakage_exposure=0,
    total_cost_saving=0,
):
    profit_improvement = (
        safe_number(total_revenue_opportunity)
        + safe_number(total_leakage_exposure)
        + safe_number(total_cost_saving)
    )

    return f"""
The ProfitIQ review of {company_name} identified a combined estimated profit improvement potential of {format_naira(profit_improvement)}.

This comprises estimated revenue growth opportunities of {format_naira(total_revenue_opportunity)}, potential leakage exposure of {format_naira(total_leakage_exposure)}, and estimated cost-saving opportunities of {format_naira(total_cost_saving)}.

Management should prioritize high-impact actions, validate all leakage findings with source documents, implement cost-control initiatives carefully, and track actual recoveries, savings, and revenue improvements weekly over the 90-day review period.
"""