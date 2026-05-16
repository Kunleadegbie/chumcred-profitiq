import streamlit as st
import pandas as pd
from datetime import datetime
from modules.report_generator import generate_excel_report
from modules.ai_insights import generate_report_narrative
from modules.export_generator import (
    generate_pdf_report,
    generate_powerpoint_report,
)

from modules.openai_ai import (
    generate_ai_board_report,
    generate_ai_executive_commentary,
    generate_ai_action_plan,
    generate_ai_multiyear_trend_commentary,
)

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="Executive Report | Chumcred ProfitIQ",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# AUTH PROTECTION
# ==========================================================
from auth import require_login, show_user_bar

require_login()


# ==========================================================
# SIDEBAR + GLOBAL STYLING
# ==========================================================
from modules.styling import apply_global_style, custom_sidebar
from modules.supabase_helpers import (
    get_or_create_active_project,
    fetch_analysis_outputs,
    fetch_action_plans,
    save_generated_report,
)

apply_global_style()
custom_sidebar()

# ==========================================================
# PAGE-SPECIFIC STYLING
# ==========================================================
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-left: 3rem;
            padding-right: 3rem;
            max-width: 100%;
        }

        .upload-card {
            background: #FFFFFF;
            padding: 1.5rem;
            border-radius: 18px;
            border: 1px solid #E6EAF0;
            box-shadow: 0 8px 24px rgba(0,0,0,0.04);
            margin-bottom: 1.5rem;
        }

        .report-card {
            background: #FFFFFF;
            padding: 1.5rem;
            border-radius: 18px;
            border: 1px solid #E6EAF0;
            box-shadow: 0 8px 24px rgba(0,0,0,0.04);
            margin-bottom: 1.5rem;
        }

        .section-title {
            font-size: 1.4rem;
            font-weight: 800;
            color: #0B1F3A;
            margin-bottom: 0.8rem;
        }

        div.stButton > button {
            background-color: #1D70A2;
            color: white;
            border-radius: 12px;
            padding: 0.75rem 1.2rem;
            border: none;
            font-weight: 700;
            width: 100%;
        }

        div.stButton > button:hover {
            background-color: #123C69;
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================================
# HEADER
# ==========================================================
st.markdown(
    """
    <div class="page-header">
        <div class="page-title">Executive Report Generator</div>
        <div class="page-subtitle">
            Generate a professional executive report covering the Business Diagnostic Report,
            Revenue Opportunity Map, Leakage Register, Cost Savings Report,
            90-Day Profit Improvement Plan, and Executive Summary Report.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==========================================================
# ACTIVE PROJECT
# ==========================================================
if "active_project" not in st.session_state:
    try:
        st.session_state["active_project"] = get_or_create_active_project()
    except Exception as e:
        st.session_state["active_project"] = None
        st.warning(f"Could not create or load active Supabase project: {e}")

# ==========================================================
# LOAD SAVED DATA FROM SUPABASE
# ==========================================================
def load_saved_report_inputs_from_supabase():
    project = st.session_state.get("active_project")

    if not project:
        return

    try:
        analysis_result = fetch_analysis_outputs(project.get("id"))

        if analysis_result.data:
            for item in analysis_result.data:
                analysis_type = item.get("analysis_type")
                output_json = item.get("output_json") or []
                total_value = float(item.get("total_value") or 0)
                df = pd.DataFrame(output_json)

                if analysis_type == "revenue_opportunity" and st.session_state.get("revenue_opportunity_df") is None:
                    st.session_state["revenue_opportunity_df"] = df
                    st.session_state["total_revenue_opportunity"] = total_value

                elif analysis_type == "leakage_detection" and st.session_state.get("leakage_df") is None:
                    st.session_state["leakage_df"] = df
                    st.session_state["total_leakage_exposure"] = total_value

                elif analysis_type == "cost_saving" and st.session_state.get("cost_saving_df") is None:
                    st.session_state["cost_saving_df"] = df
                    st.session_state["total_cost_saving"] = total_value

                elif analysis_type == "risk_heatmap" and st.session_state.get("risk_heatmap_df") is None:
                    st.session_state["risk_heatmap_df"] = df

                elif analysis_type == "branch_performance" and st.session_state.get("branch_performance_dashboard_df") is None:
                    st.session_state["branch_performance_dashboard_df"] = df

                elif analysis_type == "product_performance" and st.session_state.get("product_performance_dashboard_df") is None:
                    st.session_state["product_performance_dashboard_df"] = df

                elif analysis_type == "industry_benchmarking" and st.session_state.get("benchmark_df") is None:
                    st.session_state["benchmark_df"] = df

                elif analysis_type == "branch_risk_heatmap" and st.session_state.get("branch_risk_heatmap_df") is None:
                    st.session_state["branch_risk_heatmap_df"] = df

                elif analysis_type == "cost_concentration_heatmap" and st.session_state.get("cost_concentration_heatmap_df") is None:
                    st.session_state["cost_concentration_heatmap_df"] = df

                elif analysis_type == "leakage_risk_matrix" and st.session_state.get("leakage_risk_matrix_df") is None:
                    st.session_state["leakage_risk_matrix_df"] = df

                elif analysis_type == "profitability_heatmap" and st.session_state.get("profitability_heatmap_df") is None:
                    st.session_state["profitability_heatmap_df"] = df

                elif analysis_type == "revenue_forecast" and st.session_state.get("revenue_forecast_df") is None:
                    st.session_state["revenue_forecast_df"] = df

                elif analysis_type == "cost_forecast" and st.session_state.get("cost_forecast_df") is None:
                    st.session_state["cost_forecast_df"] = df

                elif analysis_type == "profit_forecast" and st.session_state.get("profit_forecast_df") is None:
                    st.session_state["profit_forecast_df"] = df

    except Exception as e:
        st.warning(f"Could not load saved analysis outputs from Supabase: {e}")

    try:
        action_result = fetch_action_plans(project.get("id"))

        if action_result.data and st.session_state.get("action_plan_df") is None:
            action_rows = []

            for row in action_result.data:
                action_rows.append(
                    {
                        "Action ID": row.get("action_id"),
                        "Source": row.get("source"),
                        "Issue Area": row.get("issue_area"),
                        "Observation": row.get("observation"),
                        "Recommended Action": row.get("recommended_action"),
                        "Priority": row.get("priority"),
                        "Expected Impact": row.get("expected_impact"),
                        "Action Owner": row.get("action_owner"),
                        "Department": row.get("department"),
                        "Start Date": row.get("start_date"),
                        "Due Date": row.get("due_date"),
                        "Status": row.get("status"),
                        "Actual Impact": row.get("actual_impact"),
                        "Management Comment": row.get("management_comment"),
                    }
                )

            st.session_state["action_plan_df"] = pd.DataFrame(action_rows)

    except Exception as e:
        st.warning(f"Could not load saved action plans from Supabase: {e}")


load_saved_report_inputs_from_supabase()

# ==========================================================
# GET SESSION DATA
# ==========================================================
profile = st.session_state.get("company_profile", {})
user_profile = st.session_state.get("user_profile", {})

revenue_opportunity_df = st.session_state.get("revenue_opportunity_df")
leakage_df = st.session_state.get("leakage_df")
cost_saving_df = st.session_state.get("cost_saving_df")
action_plan_df = st.session_state.get("action_plan_df")
priority_action_df = st.session_state.get("priority_action_df")
risk_heatmap_df = st.session_state.get("risk_heatmap_df")
branch_performance_df = st.session_state.get("branch_performance_dashboard_df")
product_performance_df = st.session_state.get("product_performance_dashboard_df")
benchmark_df = st.session_state.get("benchmark_df")
benchmark_insights = st.session_state.get("benchmark_insights")
branch_risk_heatmap_df = st.session_state.get("branch_risk_heatmap_df")
cost_concentration_heatmap_df = st.session_state.get("cost_concentration_heatmap_df")
leakage_risk_matrix_df = st.session_state.get("leakage_risk_matrix_df")
profitability_heatmap_df = st.session_state.get("profitability_heatmap_df")
revenue_forecast_df = st.session_state.get("revenue_forecast_df")
cost_forecast_df = st.session_state.get("cost_forecast_df")
profit_forecast_df = st.session_state.get("profit_forecast_df")
forecast_insights = st.session_state.get("forecast_insights")
revenue_trend_df = st.session_state.get("revenue_trend_df")
cost_trend_df = st.session_state.get("cost_trend_df")
profit_trend_df = st.session_state.get("profit_trend_df")

revenue_multiyear_summary = st.session_state.get("revenue_multiyear_summary", {})
cost_multiyear_summary = st.session_state.get("cost_multiyear_summary", {})

sales_df = st.session_state.get("sales_data")
expense_df = st.session_state.get("expense_data")
pnl_df = st.session_state.get("pnl_data")
bank_statement_df = st.session_state.get("bank_statement_data")
bank_charges_df = st.session_state.get("bank_charges_data")
branch_df = st.session_state.get("branch_data")
vendor_df = st.session_state.get("vendor_data")
inventory_df = st.session_state.get("inventory_data")
payroll_df = st.session_state.get("payroll_data")

total_revenue_opportunity = float(st.session_state.get("total_revenue_opportunity", 0) or 0)
total_leakage_exposure = float(st.session_state.get("total_leakage_exposure", 0) or 0)
total_cost_saving = float(st.session_state.get("total_cost_saving", 0) or 0)

profit_improvement_potential = (
    total_revenue_opportunity + total_leakage_exposure + total_cost_saving
)

# ==========================================================
# VALIDATION
# ==========================================================
if not profile and not user_profile.get("company_name"):
    st.warning("Company profile not found. Please complete the Company Profile page first.")

    if st.button("Go to Company Profile"):
        st.switch_page("pages/01_Company_Profile.py")

    st.stop()

# ==========================================================
# COMPANY DETAILS
# ==========================================================
company_name = profile.get("company_name", user_profile.get("company_name", "Not Provided"))
industry = profile.get("industry", "Not Provided")
review_date = profile.get("review_date", "Not Provided")
location = profile.get("location", "Not Provided")
branches = profile.get("number_of_branches", 0)
staff = profile.get("number_of_staff", 0)
monthly_revenue_range = profile.get("monthly_revenue_range", "Not Disclosed")
business_stage = profile.get("business_stage", "Not Provided")
review_objective = profile.get("review_objective", "Not Provided")
expected_outcome = profile.get("expected_outcome", "Not Provided")
review_type = profile.get("review_type", "Single Period Review")
reporting_frequency = profile.get("reporting_frequency", "Monthly")
review_start_date = profile.get("review_start_date", "Not Provided")
review_end_date = profile.get("review_end_date", "Not Provided")

# ==========================================================
# EXECUTIVE SUMMARY REPORT
# ==========================================================
st.markdown("## 1. Executive Summary Report")

col1, col2, col3 = st.columns(3)
col1.metric("Company", company_name)
col2.metric("Industry", industry)
col3.metric("Review Date", review_date)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Revenue Opportunity", f"₦{total_revenue_opportunity:,.0f}")
col2.metric("Leakage Exposure", f"₦{total_leakage_exposure:,.0f}")
col3.metric("Cost Saving Potential", f"₦{total_cost_saving:,.0f}")
col4.metric("Profit Improvement Potential", f"₦{profit_improvement_potential:,.0f}")

executive_summary = generate_report_narrative(
    company_name=company_name,
    total_revenue_opportunity=total_revenue_opportunity,
    total_leakage_exposure=total_leakage_exposure,
    total_cost_saving=total_cost_saving,
)

# ==========================================================
# DISPLAY EXECUTIVE SUMMARY SAFELY
# ==========================================================
with st.container(border=True):
    st.markdown("### Executive Narrative")
    st.write(executive_summary)

# ==========================================================
# BUSINESS DIAGNOSTIC REPORT
# ==========================================================
st.markdown("## 2. Business Diagnostic Report")

diagnostic_data = {
    "Diagnostic Area": [
        "Company Name",
        "Industry",
        "Location",
        "Business Stage",
        "Number of Branches",
        "Number of Staff",
        "Monthly Revenue Range",
        "Major Products / Services",
        "Major Revenue Channels",
        "Key Challenges",
        "Review Objective",
        "Expected Outcome",
        "Data Areas Uploaded",
    ],
    "Details": [
        company_name,
        industry,
        location,
        business_stage,
        branches,
        staff,
        monthly_revenue_range,
        profile.get("products_services", "Not Provided"),
        ", ".join(profile.get("major_revenue_channels", [])) if isinstance(profile.get("major_revenue_channels", []), list) else "Not Provided",
        ", ".join(profile.get("key_challenges", [])) if isinstance(profile.get("key_challenges", []), list) else "Not Provided",
        review_objective,
        expected_outcome,
        "",
    ],
}

uploaded_data_list = []
for label, df in [
    ("Sales Data", sales_df),
    ("Expense Data", expense_df),
    ("Profit and Loss Statement", pnl_df),
    ("Bank Statement Data", bank_statement_df),
    ("Bank Charges Data", bank_charges_df),
    ("Branch Performance Data", branch_df),
    ("Vendor / Procurement Data", vendor_df),
    ("Inventory Data", inventory_df),
    ("Payroll / Staff Cost Data", payroll_df),
]:
    if df is not None:
        uploaded_data_list.append(f"{label} ({len(df)} rows)")

diagnostic_data["Details"][-1] = ", ".join(uploaded_data_list) if uploaded_data_list else "Session data not loaded / Supabase analysis outputs available"

diagnostic_df = pd.DataFrame(diagnostic_data)
st.dataframe(diagnostic_df, use_container_width=True)

st.session_state["business_diagnostic_df"] = diagnostic_df

# ==========================================================
# REVENUE OPPORTUNITY MAP
# ==========================================================
st.markdown("## 3. Revenue Opportunity Map")

if revenue_opportunity_df is not None and not revenue_opportunity_df.empty:
    st.dataframe(revenue_opportunity_df, use_container_width=True)
else:
    st.info("Revenue Opportunity Map is not available yet. Complete Revenue Analysis first.")

# ==========================================================
# LEAKAGE REGISTER
# ==========================================================
st.markdown("## 4. Leakage Register")

if leakage_df is not None and not leakage_df.empty:
    st.dataframe(leakage_df, use_container_width=True)
else:
    st.info("Leakage Register is not available yet. Complete Leakage Detection first.")

# ==========================================================
# COST SAVINGS REPORT
# ==========================================================
st.markdown("## 5. Cost Savings Report")

if cost_saving_df is not None and not cost_saving_df.empty:
    st.dataframe(cost_saving_df, use_container_width=True)
else:
    st.info("Cost Savings Report is not available yet. Complete Cost Review first.")

# ==========================================================
# 90-DAY PROFIT IMPROVEMENT PLAN
# ==========================================================
st.markdown("## 6. 90-Day Profit Improvement Plan")

if action_plan_df is not None and not action_plan_df.empty:
    st.dataframe(action_plan_df, use_container_width=True)
elif priority_action_df is not None and not priority_action_df.empty:
    st.info("Action plan has not been finalized. Showing priority actions from dashboard.")
    st.dataframe(priority_action_df, use_container_width=True)
else:
    st.info("90-Day Profit Improvement Plan is not available yet. Complete Action Plan Tracker first.")

# ==========================================================
# EXECUTIVE DASHBOARD APPENDIX
# ==========================================================
st.markdown("## 7. Executive Dashboard Appendix")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue Opportunity", f"₦{total_revenue_opportunity:,.0f}")
col2.metric("Total Leakage Exposure", f"₦{total_leakage_exposure:,.0f}")
col3.metric("Total Cost Saving", f"₦{total_cost_saving:,.0f}")
col4.metric("Combined Impact", f"₦{profit_improvement_potential:,.0f}")

if risk_heatmap_df is not None and not risk_heatmap_df.empty:
    st.markdown("### Risk Heatmap")
    st.dataframe(risk_heatmap_df, use_container_width=True)

if branch_performance_df is not None and not branch_performance_df.empty:
    st.markdown("### Branch Performance")
    st.dataframe(branch_performance_df, use_container_width=True)

if product_performance_df is not None and not product_performance_df.empty:
    st.markdown("### Product Performance")
    st.dataframe(product_performance_df, use_container_width=True)


# ==========================================================
# INDUSTRY BENCHMARKING
# ==========================================================
st.markdown("## 8. Industry Benchmarking")

if benchmark_df is not None and not benchmark_df.empty:
    st.dataframe(benchmark_df, use_container_width=True)

    if benchmark_insights:
        st.markdown("### Benchmarking Insights")

        for insight in benchmark_insights:
            st.info(insight)

else:
    st.info(
        "Industry benchmarking is not available yet. "
        "Please complete benchmarking from the Opportunity Dashboard."
    )


# ==========================================================
# EXECUTIVE HEATMAPS
# ==========================================================
st.markdown("## 9. Executive Heatmaps")

if branch_risk_heatmap_df is not None and not branch_risk_heatmap_df.empty:
    st.markdown("### Branch Risk Heatmap")
    st.dataframe(branch_risk_heatmap_df, use_container_width=True)

if cost_concentration_heatmap_df is not None and not cost_concentration_heatmap_df.empty:
    st.markdown("### Cost Concentration Heatmap")
    st.dataframe(cost_concentration_heatmap_df, use_container_width=True)

if leakage_risk_matrix_df is not None and not leakage_risk_matrix_df.empty:
    st.markdown("### Leakage Risk Matrix")
    st.dataframe(leakage_risk_matrix_df, use_container_width=True)

if profitability_heatmap_df is not None and not profitability_heatmap_df.empty:
    st.markdown("### Product Profitability Heatmap")
    st.dataframe(profitability_heatmap_df, use_container_width=True)

if (
    (branch_risk_heatmap_df is None or branch_risk_heatmap_df.empty)
    and (cost_concentration_heatmap_df is None or cost_concentration_heatmap_df.empty)
    and (leakage_risk_matrix_df is None or leakage_risk_matrix_df.empty)
    and (profitability_heatmap_df is None or profitability_heatmap_df.empty)
):
    st.info("Executive heatmaps are not available yet. Please generate them from the Opportunity Dashboard.")

if "ai_multiyear_trend_commentary" not in st.session_state:
    st.session_state["ai_multiyear_trend_commentary"] = ""

# ==========================================================
# MULTI-YEAR TREND ANALYSIS
# ==========================================================
st.markdown("## 10. Multi-Year Trend Analysis")

if review_type == "Multi-Year Trend Review":
    col1, col2, col3 = st.columns(3)

    col1.metric("Review Frequency", reporting_frequency)
    col2.metric("Review Start Date", review_start_date)
    col3.metric("Review End Date", review_end_date)

    if revenue_multiyear_summary or cost_multiyear_summary:
        st.markdown("### Multi-Year Summary")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Revenue CAGR",
            f"{revenue_multiyear_summary.get('cagr', 0):.1f}%",
        )

        col2.metric(
            "Cost CAGR",
            f"{cost_multiyear_summary.get('cagr', 0):.1f}%",
        )

        revenue_growth = revenue_multiyear_summary.get("growth_percent", 0)
        cost_growth = cost_multiyear_summary.get("growth_percent", 0)
        growth_gap = revenue_growth - cost_growth

        col3.metric("Revenue Growth %", f"{revenue_growth:.1f}%")
        col4.metric("Revenue vs Cost Growth Gap", f"{growth_gap:.1f}%")

        if growth_gap > 0:
            st.success(
                "Revenue growth is ahead of cost growth, indicating a positive profitability direction."
            )
        elif growth_gap < 0:
            st.warning(
                "Cost growth is ahead of revenue growth, indicating possible margin pressure."
            )
        else:
            st.info(
                "Revenue and cost growth are broadly aligned across the review period."
            )

    if revenue_trend_df is not None and not revenue_trend_df.empty:
        st.markdown("### Revenue Trend")
        st.dataframe(revenue_trend_df, use_container_width=True)

    if cost_trend_df is not None and not cost_trend_df.empty:
        st.markdown("### Cost Trend")
        st.dataframe(cost_trend_df, use_container_width=True)

    if profit_trend_df is not None and not profit_trend_df.empty:
        st.markdown("### Profit Trend")
        st.dataframe(profit_trend_df, use_container_width=True)

else:
    st.info("Multi-year trend analysis is only shown when Review Type is set to Multi-Year Trend Review.")


# ==========================================================
# AI PREMIUM MULTI-YEAR TREND COMMENTARY
# ==========================================================
st.markdown("### AI Premium Multi-Year Trend Commentary")

if st.button("Generate AI Multi-Year Trend Commentary"):
    with st.spinner("Generating AI-powered multi-year trend commentary..."):
        ai_multiyear_trend_commentary = generate_ai_multiyear_trend_commentary(
            company_name=company_name,
            review_type=review_type,
            reporting_frequency=reporting_frequency,
            review_start_date=review_start_date,
            review_end_date=review_end_date,
            revenue_trend_df=revenue_trend_df,
            cost_trend_df=cost_trend_df,
            profit_trend_df=profit_trend_df,
            revenue_multiyear_summary=revenue_multiyear_summary,
            cost_multiyear_summary=cost_multiyear_summary,
        )

    st.session_state["ai_multiyear_trend_commentary"] = ai_multiyear_trend_commentary

if st.session_state.get("ai_multiyear_trend_commentary"):
    st.markdown("#### Generated Multi-Year Trend Commentary")
    st.markdown(st.session_state["ai_multiyear_trend_commentary"])

# ==========================================================
# PREDICTIVE ANALYTICS
# ==========================================================
st.markdown("## 11. Predictive Analytics")

if (
    revenue_forecast_df is not None and not revenue_forecast_df.empty
):
    st.markdown("### Revenue Forecast")
    st.dataframe(revenue_forecast_df, use_container_width=True)

if (
    cost_forecast_df is not None and not cost_forecast_df.empty
):
    st.markdown("### Cost Forecast")
    st.dataframe(cost_forecast_df, use_container_width=True)

if (
    profit_forecast_df is not None and not profit_forecast_df.empty
):
    st.markdown("### Profit Forecast")
    st.dataframe(profit_forecast_df, use_container_width=True)

if forecast_insights:
    st.markdown("### Forecast Insights")

    for insight in forecast_insights:
        st.info(insight)

if (
    (revenue_forecast_df is None or revenue_forecast_df.empty)
    and (cost_forecast_df is None or cost_forecast_df.empty)
    and (profit_forecast_df is None or profit_forecast_df.empty)
):
    st.info(
        "Predictive analytics is not available yet. "
        "Please generate forecasts from the Opportunity Dashboard."
    )

# ==========================================================
# MANAGEMENT RECOMMENDATIONS
# ==========================================================
st.markdown("## 12. Key Management Recommendations")

recommendations = []

if total_revenue_opportunity > 0:
    recommendations.append(
        "Prioritize quick-win revenue growth initiatives across products, branches, and customer segments."
    )

if total_leakage_exposure > 0:
    recommendations.append(
        "Conduct immediate validation and recovery review for identified leakage exposure areas."
    )

if total_cost_saving > 0:
    recommendations.append(
        "Implement structured cost optimization initiatives across major expense categories and vendor contracts."
    )

recommendations.extend(
    [
        "Introduce weekly executive performance tracking for the 90-day implementation period.",
        "Assign clear action owners and timelines to all priority initiatives.",
        "Strengthen internal controls, reporting visibility, and operational discipline.",
        "Track actual impact achieved against projected revenue improvement and savings.",
        "Prepare a final management report at the end of the 90-day review cycle.",
    ]
)

for rec in recommendations:
    st.write(f"✅ {rec}")

recommendations_df = pd.DataFrame({"Recommendation": recommendations})
st.session_state["management_recommendations_df"] = recommendations_df


# ==========================================================
# INITIALIZE AI SESSION STATE
# ==========================================================
if "ai_board_report" not in st.session_state:
    st.session_state["ai_board_report"] = ""

if "ai_executive_commentary" not in st.session_state:
    st.session_state["ai_executive_commentary"] = ""

if "ai_90_day_action_plan" not in st.session_state:
    st.session_state["ai_90_day_action_plan"] = ""

# ==========================================================
# AI PREMIUM BOARD-LEVEL COMMENTARY
# ==========================================================
st.markdown("## 13. AI Premium Board-Level Commentary")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Generate AI Board Report Narrative"):
        with st.spinner("Generating AI board-level report narrative..."):
            ai_board_report = generate_ai_board_report(
                company_name=company_name,
                executive_summary={
                    "revenue_opportunity": total_revenue_opportunity,
                    "leakage_exposure": total_leakage_exposure,
                    "cost_saving": total_cost_saving,
                    "profit_improvement_potential": profit_improvement_potential,
                },
                diagnostic_df=diagnostic_df,
                revenue_opportunity_df=revenue_opportunity_df,
                leakage_df=leakage_df,
                cost_saving_df=cost_saving_df,
                action_plan_df=action_plan_df if action_plan_df is not None else priority_action_df,
                benchmark_df=benchmark_df,
                forecast_df=profit_forecast_df,
            )

        st.session_state["ai_board_report"] = ai_board_report

with col2:
    if st.button("Generate AI Executive Commentary"):
        with st.spinner("Generating AI executive commentary..."):
            ai_executive_commentary = generate_ai_executive_commentary(
                company_name=company_name,
                revenue_opportunity_df=revenue_opportunity_df,
                leakage_df=leakage_df,
                cost_saving_df=cost_saving_df,
                action_plan_df=action_plan_df if action_plan_df is not None else priority_action_df,
            )

        st.session_state["ai_executive_commentary"] = ai_executive_commentary

with col3:
    if st.button("Generate AI 90-Day Action Plan"):
        with st.spinner("Generating AI 90-day action plan..."):
            ai_action_plan = generate_ai_action_plan(
                company_name=company_name,
                priority_action_df=priority_action_df,
                leakage_df=leakage_df,
                cost_saving_df=cost_saving_df,
                revenue_opportunity_df=revenue_opportunity_df,
            )

        st.session_state["ai_90_day_action_plan"] = ai_action_plan

# ==========================================================
# DISPLAY SAVED AI COMMENTARY
# ==========================================================
if st.session_state.get("ai_board_report"):
    st.markdown("### AI Board Report Narrative")
    st.markdown(st.session_state["ai_board_report"])

if st.session_state.get("ai_executive_commentary"):
    st.markdown("### AI Executive Commentary")
    st.markdown(st.session_state["ai_executive_commentary"])

if st.session_state.get("ai_90_day_action_plan"):
    st.markdown("### AI 90-Day Action Plan")
    st.markdown(st.session_state["ai_90_day_action_plan"])

# ==========================================================
# EXPORT REPORTS
# ==========================================================
st.markdown("## 14. Export Executive Reports")

safe_company_name = company_name.replace(" ", "_").replace("/", "_")

excel_filename = (
    f"{safe_company_name}_ProfitIQ_Executive_Report_"
    f"{datetime.now().strftime('%Y%m%d')}.xlsx"
)

pdf_filename = (
    f"{safe_company_name}_ProfitIQ_Executive_Report_"
    f"{datetime.now().strftime('%Y%m%d')}.pdf"
)

ppt_filename = (
    f"{safe_company_name}_ProfitIQ_Executive_Report_"
    f"{datetime.now().strftime('%Y%m%d')}.pptx"
)

# ==========================================================
# GENERATE EXCEL
# ==========================================================
excel_data = generate_excel_report(
    company_name=company_name,
    industry=industry,
    review_date=review_date,
    total_revenue_opportunity=total_revenue_opportunity,
    total_leakage_exposure=total_leakage_exposure,
    total_cost_saving=total_cost_saving,
    business_diagnostic_df=diagnostic_df,
    revenue_opportunity_df=revenue_opportunity_df,
    leakage_df=leakage_df,
    cost_saving_df=cost_saving_df,
    action_plan_df=action_plan_df if action_plan_df is not None else priority_action_df,
    risk_heatmap_df=risk_heatmap_df,
    branch_performance_df=branch_performance_df,
    product_performance_df=product_performance_df,
    recommendations_df=recommendations_df,
)

# ==========================================================
# GENERATE PDF
# ==========================================================
pdf_data = generate_pdf_report(
    company_name=company_name,
    executive_summary=executive_summary,
    total_revenue_opportunity=total_revenue_opportunity,
    total_leakage_exposure=total_leakage_exposure,
    total_cost_saving=total_cost_saving,
    business_diagnostic_df=diagnostic_df,
    revenue_opportunity_df=revenue_opportunity_df,
    leakage_df=leakage_df,
    cost_saving_df=cost_saving_df,
    action_plan_df=action_plan_df if action_plan_df is not None else priority_action_df,
    recommendations_df=recommendations_df,
)

# ==========================================================
# GENERATE POWERPOINT
# ==========================================================
ppt_data = generate_powerpoint_report(
    company_name=company_name,
    executive_summary=executive_summary,
    total_revenue_opportunity=total_revenue_opportunity,
    total_leakage_exposure=total_leakage_exposure,
    total_cost_saving=total_cost_saving,
    revenue_opportunity_df=revenue_opportunity_df,
    leakage_df=leakage_df,
    cost_saving_df=cost_saving_df,
    action_plan_df=action_plan_df if action_plan_df is not None else priority_action_df,
)

# ==========================================================
# DOWNLOAD BUTTONS
# ==========================================================
col1, col2, col3 = st.columns(3)

with col1:
    st.download_button(
        label="Download Excel Report",
        data=excel_data,
        file_name=excel_filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

with col2:
    st.download_button(
        label="Download PDF Report",
        data=pdf_data,
        file_name=pdf_filename,
        mime="application/pdf",
    )

with col3:
    st.download_button(
        label="Download PowerPoint Report",
        data=ppt_data,
        file_name=ppt_filename,
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )

# ==========================================================
# SAVE REPORT METADATA TO SUPABASE
# ==========================================================
st.markdown("## Save Report Record")

if st.button("Save Report Record to Supabase"):
    project = st.session_state.get("active_project")

    if not project:
        st.warning("No active project found. Please ensure Company Profile is saved first.")
    else:
        try:
            save_generated_report(
                project_id=project.get("id"),
                report_name=excel_filename,
                report_type="Excel",
                report_summary={
                    "company_name": company_name,
                    "industry": industry,
                    "review_date": review_date,
                    "total_revenue_opportunity": total_revenue_opportunity,
                    "total_leakage_exposure": total_leakage_exposure,
                    "total_cost_saving": total_cost_saving,
                    "profit_improvement_potential": profit_improvement_potential,
                    "generated_at": datetime.now().isoformat(),
                },
            )
            st.success("Report record saved successfully to Supabase.")
        except Exception as e:
            st.error(f"Could not save report record to Supabase: {e}")

# ==========================================================
# FINAL INSIGHT
# ==========================================================
st.markdown("---")

st.success(
    f"""
    Chumcred ProfitIQ has identified a combined estimated profit improvement potential of
    ₦{profit_improvement_potential:,.0f} for {company_name}.
    """
)

st.info(
    "Important: All findings should be validated through management review, supporting documents, operational verification, and implementation monitoring."
)

# ==========================================================
# NAVIGATION
# ==========================================================
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Back: Action Plan Tracker"):
        st.switch_page("pages/07_Action_Plan_Tracker.py")

with col2:
    if st.button("Go to Dashboard"):
        st.switch_page("pages/06_Opportunity_Dashboard.py")

with col3:
    if st.button("Back to Home"):
        st.switch_page("app.py")