import pandas as pd
from io import BytesIO


def generate_excel_report(
    company_name,
    industry,
    review_date,
    total_revenue_opportunity,
    total_leakage_exposure,
    total_cost_saving,
    business_diagnostic_df=None,
    revenue_opportunity_df=None,
    leakage_df=None,
    cost_saving_df=None,
    action_plan_df=None,
    risk_heatmap_df=None,
    branch_performance_df=None,
    product_performance_df=None,
    recommendations_df=None,
):
    profit_improvement_potential = (
        total_revenue_opportunity + total_leakage_exposure + total_cost_saving
    )

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        executive_summary_df = pd.DataFrame(
            [
                ["Company", company_name],
                ["Industry", industry],
                ["Review Date", review_date],
                ["Revenue Opportunity", total_revenue_opportunity],
                ["Leakage Exposure", total_leakage_exposure],
                ["Cost Saving Potential", total_cost_saving],
                ["Profit Improvement Potential", profit_improvement_potential],
            ],
            columns=["Metric", "Value"],
        )

        executive_summary_df.to_excel(
            writer,
            sheet_name="Executive Summary",
            index=False,
        )

        if business_diagnostic_df is not None:
            business_diagnostic_df.to_excel(
                writer,
                sheet_name="Business Diagnostic",
                index=False,
            )

        if revenue_opportunity_df is not None:
            revenue_opportunity_df.to_excel(
                writer,
                sheet_name="Revenue Opportunity Map",
                index=False,
            )

        if leakage_df is not None:
            leakage_df.to_excel(
                writer,
                sheet_name="Leakage Register",
                index=False,
            )

        if cost_saving_df is not None:
            cost_saving_df.to_excel(
                writer,
                sheet_name="Cost Savings Report",
                index=False,
            )

        if action_plan_df is not None:
            action_plan_df.to_excel(
                writer,
                sheet_name="90 Day Action Plan",
                index=False,
            )

        if risk_heatmap_df is not None:
            risk_heatmap_df.to_excel(
                writer,
                sheet_name="Risk Heatmap",
                index=False,
            )

        if branch_performance_df is not None:
            branch_performance_df.to_excel(
                writer,
                sheet_name="Branch Performance",
                index=False,
            )

        if product_performance_df is not None:
            product_performance_df.to_excel(
                writer,
                sheet_name="Product Performance",
                index=False,
            )

        if recommendations_df is not None:
            recommendations_df.to_excel(
                writer,
                sheet_name="Recommendations",
                index=False,
            )

    return output.getvalue()


def build_executive_narrative(
    company_name,
    total_revenue_opportunity,
    total_leakage_exposure,
    total_cost_saving,
):
    profit_improvement_potential = (
        total_revenue_opportunity + total_leakage_exposure + total_cost_saving
    )

    return f"""
The review of {company_name} identified opportunities to improve profitability through revenue growth,
leakage reduction, and cost optimization.

The analysis identified estimated revenue growth opportunities of ₦{total_revenue_opportunity:,.0f},
potential leakage exposure of ₦{total_leakage_exposure:,.0f}, and estimated cost-saving opportunities
of ₦{total_cost_saving:,.0f}.

Overall, the review identified a combined estimated profit improvement potential of
₦{profit_improvement_potential:,.0f}.

The key recommendation is for management to prioritize high-impact revenue opportunities,
validate identified leakages, strengthen operational controls, and implement the recommended
90-day action plan with clear ownership and monitoring discipline.
"""


def build_business_diagnostic_summary(profile, uploaded_data_summary=None):
    company_name = profile.get("company_name", "Not Provided")
    industry = profile.get("industry", "Not Provided")
    location = profile.get("location", "Not Provided")
    business_stage = profile.get("business_stage", "Not Provided")
    branches = profile.get("number_of_branches", 0)
    staff = profile.get("number_of_staff", 0)
    monthly_revenue_range = profile.get("monthly_revenue_range", "Not Disclosed")
    products_services = profile.get("products_services", "Not Provided")
    review_objective = profile.get("review_objective", "Not Provided")
    expected_outcome = profile.get("expected_outcome", "Not Provided")

    major_revenue_channels = profile.get("major_revenue_channels", [])
    key_challenges = profile.get("key_challenges", [])

    if isinstance(major_revenue_channels, list):
        major_revenue_channels = ", ".join(major_revenue_channels)

    if isinstance(key_challenges, list):
        key_challenges = ", ".join(key_challenges)

    diagnostic_rows = [
        ["Company Name", company_name],
        ["Industry", industry],
        ["Location", location],
        ["Business Stage", business_stage],
        ["Number of Branches", branches],
        ["Number of Staff", staff],
        ["Monthly Revenue Range", monthly_revenue_range],
        ["Major Products / Services", products_services],
        ["Major Revenue Channels", major_revenue_channels],
        ["Key Challenges", key_challenges],
        ["Review Objective", review_objective],
        ["Expected Outcome", expected_outcome],
    ]

    if uploaded_data_summary:
        diagnostic_rows.append(["Data Areas Uploaded", uploaded_data_summary])

    return pd.DataFrame(
        diagnostic_rows,
        columns=["Diagnostic Area", "Details"],
    )