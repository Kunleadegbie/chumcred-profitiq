# ==========================================================
# SECTOR LABEL CONFIGURATION
# ==========================================================

def get_sector_labels(engagement_type="Private Sector"):
    """
    Returns platform labels based on engagement type.
    This allows ProfitIQ to support both private businesses and government institutions
    without rebuilding the whole app.
    """

    if engagement_type == "Government":
        return {
            "revenue": "IGR / Government Revenue",
            "sales_data": "Revenue Collection Data",
            "expense_data": "Expenditure Data",
            "customer": "Taxpayer / Revenue Source",
            "product": "Revenue Stream",
            "branch": "MDA / LGA",
            "target": "Revenue Target",
            "cost": "Expenditure",
            "profit": "Net Revenue Position",
            "leakage": "Revenue Leakage / Financial Control Gap",
            "dashboard": "Government Revenue Intelligence Dashboard",
            "executive_report": "Government Financial Intelligence Report",
            "action_plan": "Revenue Improvement & Leakage Reduction Plan",
        }

    return {
        "revenue": "Revenue",
        "sales_data": "Sales Data",
        "expense_data": "Expense Data",
        "customer": "Customer",
        "product": "Product / Service",
        "branch": "Branch / Location",
        "target": "Sales Target",
        "cost": "Cost",
        "profit": "Profit",
        "leakage": "Revenue Leakage",
        "dashboard": "Opportunity Dashboard",
        "executive_report": "Executive Report",
        "action_plan": "90-Day Profit Improvement Plan",
    }


def get_engagement_type():
    """
    Safely gets engagement type from company profile.
    """

    try:
        import streamlit as st

        profile = st.session_state.get("company_profile", {})
        return profile.get("engagement_type", "Private Sector")

    except Exception:
        return "Private Sector"


def get_current_sector_labels():
    """
    Returns the active label dictionary based on current session profile.
    """

    engagement_type = get_engagement_type()
    return get_sector_labels(engagement_type)