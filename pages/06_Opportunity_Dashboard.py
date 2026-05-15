import streamlit as st
import pandas as pd
import plotly.express as px
from modules.ai_insights import generate_executive_dashboard_insights
from modules.industry_benchmarking import (
    generate_benchmark_comparison,
    generate_benchmark_insights,
)

from modules.executive_heatmaps import (
    generate_branch_risk_heatmap,
    generate_cost_concentration_heatmap,
    generate_leakage_risk_matrix,
    generate_profitability_heatmap,
)

from modules.predictive_analytics import (
    generate_revenue_forecast,
    generate_cost_forecast,
    generate_profit_forecast,
    generate_forecast_insights,
)

from modules.openai_ai import (
    generate_ai_dashboard_summary,
    generate_ai_forecast_commentary,
    generate_ai_benchmark_commentary,
    generate_ai_heatmap_commentary,
)

from modules.period_analysis import (
    filter_by_review_period,
    generate_period_trend,
    generate_multiyear_summary,
)

# ==========================================================
# DATA CLEANING HELPERS
# ==========================================================
def fix_bad_csv_dataframe(df):
    if df is None or df.empty:
        return df

    if len(df.columns) == 1 and "," in str(df.columns[0]):
        single_col = df.columns[0]
        fixed_df = df[single_col].astype(str).str.split(",", expand=True)
        fixed_df.columns = [col.strip() for col in str(single_col).split(",")]
        return fixed_df

    return df


def remove_duplicate_columns(df):
    if df is None or df.empty:
        return df

    return df.loc[:, ~df.columns.duplicated()]


def get_numeric_like_columns(df):
    numeric_cols = []

    if df is None or df.empty:
        return numeric_cols

    for col in df.columns:
        converted = pd.to_numeric(df[col], errors="coerce")
        if converted.notna().sum() > 0:
            numeric_cols.append(col)

    return numeric_cols


def get_date_like_columns(df):
    date_cols = []

    if df is None or df.empty:
        return date_cols

    for col in df.columns:
        converted = pd.to_datetime(df[col], errors="coerce")
        if converted.notna().sum() > 0:
            date_cols.append(col)

    return date_cols

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="Opportunity Dashboard | Chumcred ProfitIQ",
    page_icon="📊",
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
    save_analysis_output,
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

        .section-title {
            font-size: 1.4rem;
            font-weight: 800;
            color: #0B1F3A;
            margin-bottom: 0.8rem;
        }

        .insight-card {
            background: #FFFFFF;
            padding: 1.5rem;
            border-radius: 18px;
            border: 1px solid #E6EAF0;
            box-shadow: 0 8px 24px rgba(0,0,0,0.04);
            margin-bottom: 1.2rem;
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
        <div class="page-title">Opportunity Dashboard</div>
        <div class="page-subtitle">
            CEO-level dashboard showing revenue opportunities, leakage exposure, cost-saving potential,
            profit improvement, top actions, risk heatmap, branch performance, and product performance.
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
# LOAD SAVED ANALYSIS OUTPUTS FROM SUPABASE
# ==========================================================
def load_saved_outputs_from_supabase():
    project = st.session_state.get("active_project")

    if not project:
        return

    try:
        result = fetch_analysis_outputs(project.get("id"))

        if not result.data:
            return

        for item in result.data:
            analysis_type = item.get("analysis_type")
            output_json = item.get("output_json") or []
            total_value = item.get("total_value") or 0

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

    except Exception as e:
        st.warning(f"Could not load saved analysis outputs from Supabase: {e}")


load_saved_outputs_from_supabase()

# ==========================================================
# GET ANALYSIS OUTPUTS
# ==========================================================
revenue_opportunity_df = st.session_state.get("revenue_opportunity_df")
leakage_df = st.session_state.get("leakage_df")
cost_saving_df = st.session_state.get("cost_saving_df")

sales_df = st.session_state.get("sales_data")
branch_df = st.session_state.get("branch_data")
expense_df = st.session_state.get("expense_data")
payroll_df = st.session_state.get("payroll_data")

sales_df = remove_duplicate_columns(fix_bad_csv_dataframe(sales_df))
branch_df = remove_duplicate_columns(fix_bad_csv_dataframe(branch_df))
expense_df = remove_duplicate_columns(fix_bad_csv_dataframe(expense_df))
payroll_df = remove_duplicate_columns(fix_bad_csv_dataframe(payroll_df))

if sales_df is not None:
    st.session_state["sales_data"] = sales_df

if branch_df is not None:
    st.session_state["branch_data"] = branch_df

if expense_df is not None:
    st.session_state["expense_data"] = expense_df

if payroll_df is not None:
    st.session_state["payroll_data"] = payroll_df

total_revenue_opportunity = float(st.session_state.get("total_revenue_opportunity", 0) or 0)
total_leakage_exposure = float(st.session_state.get("total_leakage_exposure", 0) or 0)
total_cost_saving = float(st.session_state.get("total_cost_saving", 0) or 0)

profit_improvement_potential = (
    total_revenue_opportunity + total_leakage_exposure + total_cost_saving
)

# ==========================================================
# EMPTY STATE
# ==========================================================
if (
    revenue_opportunity_df is None
    and leakage_df is None
    and cost_saving_df is None
):
    st.warning(
        "No analysis output found yet. Please complete Revenue Analysis, Leakage Detection, and Cost Review first."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Go to Revenue Analysis"):
            st.switch_page("pages/03_Revenue_Analysis.py")

    with col2:
        if st.button("Go to Leakage Detection"):
            st.switch_page("pages/04_Leakage_Detection.py")

    with col3:
        if st.button("Go to Cost Review"):
            st.switch_page("pages/05_Cost_Review.py")

    st.stop()

# ==========================================================
# COMPANY CONTEXT
# ==========================================================
profile = st.session_state.get("company_profile", {})
user_profile = st.session_state.get("user_profile", {})

# ==========================================================
# REVIEW PERIOD SETTINGS
# ==========================================================
review_type = profile.get("review_type", "Single Period Review")
reporting_frequency = profile.get("reporting_frequency", "Monthly")
review_start_date = profile.get("review_start_date")
review_end_date = profile.get("review_end_date")

st.markdown("## Company Review Context")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Company", profile.get("company_name", user_profile.get("company_name", "Not Provided")))
col2.metric("Industry", profile.get("industry", "Not Provided"))
col3.metric("Branches", profile.get("number_of_branches", 0))
col4.metric("Staff", profile.get("number_of_staff", 0))

# ==========================================================
# EXECUTIVE KPI CARDS
# ==========================================================
st.markdown("## Executive Opportunity Summary")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Revenue Opportunity", f"₦{total_revenue_opportunity:,.0f}")
col2.metric("Leakage Exposure", f"₦{total_leakage_exposure:,.0f}")
col3.metric("Cost Saving Potential", f"₦{total_cost_saving:,.0f}")
col4.metric("Profit Improvement Potential", f"₦{profit_improvement_potential:,.0f}")


# ==========================================================
# MULTI-YEAR PERFORMANCE SUMMARY
# ==========================================================
if review_type == "Multi-Year Trend Review":
    st.markdown("## Multi-Year Performance Summary")

    revenue_trend_df = st.session_state.get("revenue_trend_df")
    cost_trend_df = st.session_state.get("cost_trend_df")

    revenue_summary = st.session_state.get("revenue_multiyear_summary", {})
    cost_summary = st.session_state.get("cost_multiyear_summary", {})

    if revenue_summary or cost_summary:
        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Review Frequency",
            reporting_frequency,
        )

        col2.metric(
            "Revenue CAGR",
            f"{revenue_summary.get('cagr', 0):.1f}%",
        )

        col3.metric(
            "Cost CAGR",
            f"{cost_summary.get('cagr', 0):.1f}%",
        )

        revenue_growth = revenue_summary.get("growth_percent", 0)
        cost_growth = cost_summary.get("growth_percent", 0)

        margin_direction = revenue_growth - cost_growth

        col4.metric(
            "Revenue vs Cost Growth Gap",
            f"{margin_direction:.1f}%",
        )

        if margin_direction > 0:
            st.success(
                "Revenue growth is currently ahead of cost growth, which may support improved profitability."
            )
        elif margin_direction < 0:
            st.warning(
                "Cost growth is ahead of revenue growth. Management should review cost escalation and margin pressure."
            )
        else:
            st.info(
                "Revenue and cost growth are broadly aligned within the selected review period."
            )

    else:
        st.info(
            "Multi-year summary will appear after generating Revenue Trend and Cost Trend from Revenue Analysis and Cost Review."
        )

    # ------------------------------------------------------
    # REVENUE TREND CHART
    # ------------------------------------------------------
    if revenue_trend_df is not None and not revenue_trend_df.empty:
        st.markdown("### Multi-Year Revenue Trend")
        st.dataframe(revenue_trend_df, use_container_width=True)

        revenue_value_col = [
            col for col in revenue_trend_df.columns
            if col not in ["Period", "Previous Period Value", "Growth Amount", "Growth %"]
        ]

        if revenue_value_col:
            fig = px.line(
                revenue_trend_df,
                x="Period",
                y=revenue_value_col[0],
                markers=True,
                title=f"{reporting_frequency} Revenue Trend",
            )
            st.plotly_chart(fig, use_container_width=True)

    # ------------------------------------------------------
    # COST TREND CHART
    # ------------------------------------------------------
    if cost_trend_df is not None and not cost_trend_df.empty:
        st.markdown("### Multi-Year Cost Trend")
        st.dataframe(cost_trend_df, use_container_width=True)

        cost_value_col = [
            col for col in cost_trend_df.columns
            if col not in ["Period", "Previous Period Value", "Growth Amount", "Growth %"]
        ]

        if cost_value_col:
            fig = px.line(
                cost_trend_df,
                x="Period",
                y=cost_value_col[0],
                markers=True,
                title=f"{reporting_frequency} Cost Trend",
            )
            st.plotly_chart(fig, use_container_width=True)

    # ------------------------------------------------------
    # PROFIT TREND
    # ------------------------------------------------------
    if (
        revenue_trend_df is not None and not revenue_trend_df.empty
        and cost_trend_df is not None and not cost_trend_df.empty
    ):
        st.markdown("### Multi-Year Profit Trend")

        revenue_value_col = [
            col for col in revenue_trend_df.columns
            if col not in ["Period", "Previous Period Value", "Growth Amount", "Growth %"]
        ][0]

        cost_value_col = [
            col for col in cost_trend_df.columns
            if col not in ["Period", "Previous Period Value", "Growth Amount", "Growth %"]
        ][0]

        profit_trend_df = revenue_trend_df[["Period", revenue_value_col]].merge(
            cost_trend_df[["Period", cost_value_col]],
            on="Period",
            how="outer",
        ).fillna(0)

        profit_trend_df = profit_trend_df.rename(
            columns={
                revenue_value_col: "Revenue",
                cost_value_col: "Cost",
            }
        )

        profit_trend_df["Estimated Profit"] = (
            profit_trend_df["Revenue"] - profit_trend_df["Cost"]
        )

        st.dataframe(profit_trend_df, use_container_width=True)

        fig = px.line(
            profit_trend_df,
            x="Period",
            y=["Revenue", "Cost", "Estimated Profit"],
            markers=True,
            title="Revenue, Cost and Estimated Profit Trend",
        )
        st.plotly_chart(fig, use_container_width=True)

        st.session_state["profit_trend_df"] = profit_trend_df


# ==========================================================
# INDUSTRY BENCHMARKING
# ==========================================================
st.markdown("## Industry Benchmarking")

industry = profile.get("industry", "General")

# Estimate revenue from sales data
total_revenue_for_benchmark = 0
if sales_df is not None and not sales_df.empty:
    sales_columns = list(sales_df.columns)

    benchmark_revenue_col = st.selectbox(
        "Select Revenue Column for Benchmarking",
        sales_columns,
        key="benchmark_revenue_col",
    )

    total_revenue_for_benchmark = pd.to_numeric(
        sales_df[benchmark_revenue_col],
        errors="coerce",
    ).fillna(0).sum()

# Estimate cost from expense data
expense_df = st.session_state.get("expense_data")
total_cost_for_benchmark = 0

if expense_df is not None and not expense_df.empty:
    expense_columns = list(expense_df.columns)

    benchmark_cost_col = st.selectbox(
        "Select Cost Column for Benchmarking",
        expense_columns,
        key="benchmark_cost_col",
    )

    total_cost_for_benchmark = pd.to_numeric(
        expense_df[benchmark_cost_col],
        errors="coerce",
    ).fillna(0).sum()

# Estimate payroll from payroll data
payroll_df = st.session_state.get("payroll_data")
total_payroll_for_benchmark = 0

if payroll_df is not None and not payroll_df.empty:
    payroll_columns = list(payroll_df.columns)

    benchmark_payroll_col = st.selectbox(
        "Select Payroll Column for Benchmarking",
        payroll_columns,
        key="benchmark_payroll_col",
    )

    total_payroll_for_benchmark = pd.to_numeric(
        payroll_df[benchmark_payroll_col],
        errors="coerce",
    ).fillna(0).sum()

# Estimate net profit
net_profit_for_benchmark = (
    total_revenue_for_benchmark - total_cost_for_benchmark
)

benchmark_df = generate_benchmark_comparison(
    industry=industry,
    total_revenue=total_revenue_for_benchmark,
    total_cost=total_cost_for_benchmark,
    total_payroll=total_payroll_for_benchmark,
    net_profit=net_profit_for_benchmark,
)

st.dataframe(benchmark_df, use_container_width=True)

benchmark_insights = generate_benchmark_insights(benchmark_df)

for insight in benchmark_insights:
    st.info(insight)

st.session_state["benchmark_df"] = benchmark_df
st.session_state["benchmark_insights"] = benchmark_insights

# ==========================================================
# IMPACT BREAKDOWN CHART
# ==========================================================
st.markdown("## Profit Improvement Breakdown")

impact_df = pd.DataFrame(
    [
        {"Area": "Revenue Opportunity", "Estimated Impact": total_revenue_opportunity},
        {"Area": "Leakage Exposure", "Estimated Impact": total_leakage_exposure},
        {"Area": "Cost Saving Potential", "Estimated Impact": total_cost_saving},
    ]
)

fig = px.bar(
    impact_df,
    x="Area",
    y="Estimated Impact",
    title="Estimated Profit Improvement Breakdown",
    text_auto=True,
)
st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# PRIORITY ACTIONS
# ==========================================================
st.markdown("## Top 10 Priority Actions")

priority_frames = []

if revenue_opportunity_df is not None and not revenue_opportunity_df.empty:
    temp = revenue_opportunity_df.copy()
    temp["Source"] = "Revenue Analysis"
    temp = temp.rename(
        columns={
            "Opportunity Area": "Issue Area",
            "Estimated Revenue Opportunity": "Estimated Impact",
        }
    )

    required_cols = ["Source", "Issue Area", "Observation", "Estimated Impact", "Recommended Action", "Priority"]
    if all(col in temp.columns for col in required_cols):
        priority_frames.append(temp[required_cols])

if leakage_df is not None and not leakage_df.empty:
    temp = leakage_df.copy()
    temp["Source"] = "Leakage Detection"
    temp = temp.rename(
        columns={
            "Leakage Area": "Issue Area",
            "Estimated Leakage Exposure": "Estimated Impact",
        }
    )

    required_cols = ["Source", "Issue Area", "Observation", "Estimated Impact", "Recommended Action", "Priority"]
    if all(col in temp.columns for col in required_cols):
        priority_frames.append(temp[required_cols])

if cost_saving_df is not None and not cost_saving_df.empty:
    temp = cost_saving_df.copy()
    temp["Source"] = "Cost Review"
    temp = temp.rename(
        columns={
            "Cost Area": "Issue Area",
            "Estimated Cost Saving": "Estimated Impact",
        }
    )

    required_cols = ["Source", "Issue Area", "Observation", "Estimated Impact", "Recommended Action", "Priority"]
    if all(col in temp.columns for col in required_cols):
        priority_frames.append(temp[required_cols])

if priority_frames:
    priority_df = pd.concat(priority_frames, ignore_index=True)
    priority_df["Estimated Impact"] = pd.to_numeric(
        priority_df["Estimated Impact"], errors="coerce"
    ).fillna(0)

    priority_order = {"High": 1, "Medium": 2, "Low": 3, "Review": 4}
    priority_df["Priority Rank"] = priority_df["Priority"].map(priority_order).fillna(5)

    priority_df = priority_df.sort_values(
        by=["Priority Rank", "Estimated Impact"],
        ascending=[True, False],
    )

    top_10_actions = priority_df.drop(columns=["Priority Rank"]).head(10)
    st.dataframe(top_10_actions, use_container_width=True)

    st.session_state["priority_action_df"] = priority_df.drop(columns=["Priority Rank"])

    fig = px.bar(
        top_10_actions,
        x="Issue Area",
        y="Estimated Impact",
        color="Source",
        title="Top 10 Actions by Estimated Impact",
        text_auto=True,
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("No priority actions available yet.")

# ==========================================================
# RISK HEATMAP
# ==========================================================
st.markdown("## Risk Heatmap")

if priority_frames:
    risk_df = priority_df.copy()

    risk_score_map = {
        "High": 3,
        "Medium": 2,
        "Low": 1,
        "Review": 1,
    }

    risk_df["Risk Score"] = risk_df["Priority"].map(risk_score_map).fillna(1)

    if risk_df["Estimated Impact"].nunique() >= 3:
        risk_df["Impact Score"] = pd.qcut(
            risk_df["Estimated Impact"].rank(method="first"),
            q=3,
            labels=[1, 2, 3],
        ).astype(int)
    else:
        risk_df["Impact Score"] = 1

    risk_df["Heatmap Score"] = risk_df["Risk Score"] * risk_df["Impact Score"]

    heatmap_summary = (
        risk_df.groupby(["Source", "Priority"], as_index=False)
        .agg(
            Total_Impact=("Estimated Impact", "sum"),
            Average_Risk_Score=("Risk Score", "mean"),
            Average_Impact_Score=("Impact Score", "mean"),
            Heatmap_Score=("Heatmap Score", "sum"),
            Issue_Count=("Issue Area", "count"),
        )
        .sort_values("Heatmap_Score", ascending=False)
    )

    st.dataframe(heatmap_summary, use_container_width=True)

    fig = px.density_heatmap(
        heatmap_summary,
        x="Source",
        y="Priority",
        z="Heatmap_Score",
        title="Risk Heatmap by Review Area and Priority",
        text_auto=True,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.session_state["risk_heatmap_df"] = heatmap_summary

else:
    st.info("Risk heatmap will appear after priority actions are available.")


# ==========================================================
# EXECUTIVE HEATMAPS
# ==========================================================
st.markdown("## Executive Heatmaps")

expense_df = st.session_state.get("expense_data")

# ----------------------------------------------------------
# 1. Branch Risk Heatmap
# ----------------------------------------------------------
st.markdown("### Branch Risk Heatmap")

if branch_df is not None and not branch_df.empty:


    branch_columns = list(branch_df.columns)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        heat_branch_col = st.selectbox(
            "Heatmap Branch Column",
            branch_columns,
            key="heat_branch_col",
        )

    with col2:
        heat_revenue_col = st.selectbox(
            "Heatmap Revenue Column",
            branch_columns,
            key="heat_revenue_col",
        )

    with col3:
        heat_target_col = st.selectbox(
            "Heatmap Target Column",
            ["None"] + branch_columns,
            key="heat_target_col",
        )

    with col4:
        heat_profit_col = st.selectbox(
            "Heatmap Profit Column",
            ["None"] + branch_columns,
            key="heat_profit_col",
        )

    branch_risk_heatmap_df = generate_branch_risk_heatmap(
        branch_df=branch_df,
        branch_col=heat_branch_col,
        revenue_col=heat_revenue_col,
        target_col=None if heat_target_col == "None" else heat_target_col,
        profit_col=None if heat_profit_col == "None" else heat_profit_col,
    )

    branch_risk_heatmap_df = remove_duplicate_columns(branch_risk_heatmap_df)
    st.dataframe(branch_risk_heatmap_df, use_container_width=True)

    if not branch_risk_heatmap_df.empty:
        fig = px.density_heatmap(
            branch_risk_heatmap_df,
            x=heat_branch_col,
            y="Risk Level",
            z="Target Achievement %",
            title="Branch Risk Heatmap",
            text_auto=True,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.session_state["branch_risk_heatmap_df"] = remove_duplicate_columns(branch_risk_heatmap_df)

else:
    st.info("Upload Branch Performance Data to generate Branch Risk Heatmap.")

# ----------------------------------------------------------
# 2. Cost Concentration Heatmap
# ----------------------------------------------------------
st.markdown("### Cost Concentration Heatmap")

if expense_df is not None and not expense_df.empty:
    expense_columns = list(expense_df.columns)

    col1, col2 = st.columns(2)

    with col1:
        heat_cost_category_col = st.selectbox(
            "Cost Category Column",
            expense_columns,
            key="heat_cost_category_col",
        )

    with col2:
        heat_cost_amount_col = st.selectbox(
            "Cost Amount Column",
            expense_columns,
            key="heat_cost_amount_col",
        )

    cost_concentration_heatmap_df = generate_cost_concentration_heatmap(
        expense_df=expense_df,
        category_col=heat_cost_category_col,
        amount_col=heat_cost_amount_col,
    )

    st.dataframe(cost_concentration_heatmap_df, use_container_width=True)

    if not cost_concentration_heatmap_df.empty:
        fig = px.density_heatmap(
            cost_concentration_heatmap_df,
            x=heat_cost_category_col,
            y="Concentration Risk",
            z="Cost Share %",
            title="Cost Concentration Heatmap",
            text_auto=True,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.session_state["cost_concentration_heatmap_df"] = cost_concentration_heatmap_df

else:
    st.info("Upload Expense Data to generate Cost Concentration Heatmap.")

# ----------------------------------------------------------
# 3. Leakage Risk Matrix
# ----------------------------------------------------------
st.markdown("### Leakage Risk Matrix")

if leakage_df is not None and not leakage_df.empty:
    leakage_risk_matrix_df = generate_leakage_risk_matrix(leakage_df)

    st.dataframe(leakage_risk_matrix_df, use_container_width=True)

    if not leakage_risk_matrix_df.empty:
        value_col = (
            "Estimated Leakage Exposure"
            if "Estimated Leakage Exposure" in leakage_risk_matrix_df.columns
            else "Estimated Impact"
        )

        fig = px.density_heatmap(
            leakage_risk_matrix_df,
            x="Priority",
            y="Leakage Risk Level",
            z=value_col,
            title="Leakage Risk Matrix",
            text_auto=True,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.session_state["leakage_risk_matrix_df"] = leakage_risk_matrix_df

else:
    st.info("Complete Leakage Detection to generate Leakage Risk Matrix.")

# ----------------------------------------------------------
# 4. Product Profitability Heatmap
# ----------------------------------------------------------
st.markdown("### Product Profitability Heatmap")

if sales_df is not None and not sales_df.empty:
    sales_columns = list(sales_df.columns)

    col1, col2 = st.columns(2)

    with col1:
        heat_product_col = st.selectbox(
            "Product Column for Profitability Heatmap",
            ["None"] + sales_columns,
            key="heat_product_col",
        )

    with col2:
        heat_product_revenue_col = st.selectbox(
            "Product Revenue Column",
            sales_columns,
            key="heat_product_revenue_col",
        )

    if heat_product_col != "None":
        profitability_heatmap_df = generate_profitability_heatmap(
            sales_df=sales_df,
            product_col=heat_product_col,
            revenue_col=heat_product_revenue_col,
        )

        st.dataframe(profitability_heatmap_df, use_container_width=True)

        if not profitability_heatmap_df.empty:
            fig = px.density_heatmap(
                profitability_heatmap_df,
                x=heat_product_col,
                y="Profitability Level",
                z="Revenue Share %",
                title="Product Profitability Heatmap",
                text_auto=True,
            )
            st.plotly_chart(fig, use_container_width=True)

        st.session_state["profitability_heatmap_df"] = profitability_heatmap_df

else:
    st.info("Upload Sales Data to generate Product Profitability Heatmap.")


# ==========================================================
# PREDICTIVE ANALYTICS
# ==========================================================
st.markdown("## Predictive Analytics")

expense_df = st.session_state.get("expense_data")

# ----------------------------------------------------------
# FORECAST SETTINGS
# ----------------------------------------------------------
forecast_periods = st.slider(
    "Forecast Periods",
    min_value=1,
    max_value=12,
    value=3,
)

# ----------------------------------------------------------
# REVENUE FORECAST
# ----------------------------------------------------------
st.markdown("### Revenue Forecast")

revenue_forecast_df = pd.DataFrame()
monthly_revenue_df = pd.DataFrame()

if sales_df is not None and not sales_df.empty:
    sales_columns = list(sales_df.columns)

    col1, col2 = st.columns(2)

    with col1:
        forecast_sales_date_col = st.selectbox(
            "Revenue Forecast Date Column",
            sales_columns,
            key="forecast_sales_date_col",
        )

    with col2:
        forecast_sales_amount_col = st.selectbox(
            "Revenue Forecast Amount Column",
            sales_columns,
            key="forecast_sales_amount_col",
        )

    monthly_revenue_df, revenue_forecast_df = generate_revenue_forecast(
        sales_df=sales_df,
        date_col=forecast_sales_date_col,
        revenue_col=forecast_sales_amount_col,
        forecast_periods=forecast_periods,
    )

    if not monthly_revenue_df.empty:
        st.markdown("#### Historical Revenue Trend")
        st.dataframe(monthly_revenue_df, use_container_width=True)

        fig = px.line(
            monthly_revenue_df,
            x="Month",
            y="Value",
            markers=True,
            title="Historical Revenue Trend",
        )
        st.plotly_chart(fig, use_container_width=True)

    if not revenue_forecast_df.empty:
        st.markdown("#### Revenue Forecast")
        st.dataframe(revenue_forecast_df, use_container_width=True)

        fig = px.bar(
            revenue_forecast_df,
            x="Forecast Period",
            y="Forecast Value",
            title="Revenue Forecast",
            text_auto=True,
        )
        st.plotly_chart(fig, use_container_width=True)

        st.session_state["revenue_forecast_df"] = revenue_forecast_df

else:
    st.info("Upload Sales Data to generate Revenue Forecast.")

# ----------------------------------------------------------
# COST FORECAST
# ----------------------------------------------------------
st.markdown("### Cost Forecast")

cost_forecast_df = pd.DataFrame()
monthly_cost_df = pd.DataFrame()

if expense_df is not None and not expense_df.empty:
    expense_columns = list(expense_df.columns)

    col1, col2 = st.columns(2)

    with col1:
        forecast_cost_date_col = st.selectbox(
            "Cost Forecast Date Column",
            expense_columns,
            key="forecast_cost_date_col",
        )

    with col2:
        forecast_cost_amount_col = st.selectbox(
            "Cost Forecast Amount Column",
            expense_columns,
            key="forecast_cost_amount_col",
        )

    monthly_cost_df, cost_forecast_df = generate_cost_forecast(
        expense_df=expense_df,
        date_col=forecast_cost_date_col,
        cost_col=forecast_cost_amount_col,
        forecast_periods=forecast_periods,
    )

    if not monthly_cost_df.empty:
        st.markdown("#### Historical Cost Trend")
        st.dataframe(monthly_cost_df, use_container_width=True)

        fig = px.line(
            monthly_cost_df,
            x="Month",
            y="Value",
            markers=True,
            title="Historical Cost Trend",
        )
        st.plotly_chart(fig, use_container_width=True)

    if not cost_forecast_df.empty:
        st.markdown("#### Cost Forecast")
        st.dataframe(cost_forecast_df, use_container_width=True)

        fig = px.bar(
            cost_forecast_df,
            x="Forecast Period",
            y="Forecast Value",
            title="Cost Forecast",
            text_auto=True,
        )
        st.plotly_chart(fig, use_container_width=True)

        st.session_state["cost_forecast_df"] = cost_forecast_df

else:
    st.info("Upload Expense Data to generate Cost Forecast.")

# ----------------------------------------------------------
# PROFIT FORECAST
# ----------------------------------------------------------
st.markdown("### Profit Forecast")

profit_forecast_df = generate_profit_forecast(
    revenue_forecast_df=revenue_forecast_df,
    cost_forecast_df=cost_forecast_df,
)

if not profit_forecast_df.empty:
    st.dataframe(profit_forecast_df, use_container_width=True)

    fig = px.bar(
        profit_forecast_df,
        x="Forecast Period",
        y="Profit Forecast",
        title="Profit Forecast",
        text_auto=True,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.session_state["profit_forecast_df"] = profit_forecast_df

else:
    st.info("Profit forecast requires both Revenue Forecast and Cost Forecast.")

# ----------------------------------------------------------
# FORECAST INSIGHTS
# ----------------------------------------------------------
st.markdown("### Forecast Insights")

forecast_insights = generate_forecast_insights(
    revenue_forecast_df=revenue_forecast_df,
    cost_forecast_df=cost_forecast_df,
    profit_forecast_df=profit_forecast_df,
)

for insight in forecast_insights:
    st.info(insight)

st.session_state["forecast_insights"] = forecast_insights

# ==========================================================
# BRANCH PERFORMANCE
# ==========================================================
st.markdown("## Branch Performance")

if branch_df is not None and not branch_df.empty:
    # Fix badly-read CSV where all columns are combined into one comma-separated column
    if len(branch_df.columns) == 1 and "," in branch_df.columns[0]:
        single_col = branch_df.columns[0]

        branch_df = branch_df[single_col].astype(str).str.split(",", expand=True)
        branch_df.columns = [col.strip() for col in single_col.split(",")]

        st.warning(
            "Branch data appeared to be loaded as one combined column. "
            "ProfitIQ has attempted to split it automatically."
        )
    
    branch_data = branch_df.copy()
    branch_columns = list(branch_data.columns)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        branch_col = st.selectbox("Branch Column", branch_columns, key="dash_branch_col")

    with col2:
        branch_revenue_col = st.selectbox("Revenue Column", branch_columns, key="dash_branch_revenue_col")

    with col3:
        branch_target_col = st.selectbox("Target Column", ["None"] + branch_columns, key="dash_branch_target_col")

    with col4:
        branch_profit_col = st.selectbox("Profit Column", ["None"] + branch_columns, key="dash_branch_profit_col")

    branch_data[branch_revenue_col] = pd.to_numeric(
        branch_data[branch_revenue_col], errors="coerce"
    ).fillna(0)

    if branch_target_col != "None":
        branch_data[branch_target_col] = pd.to_numeric(
            branch_data[branch_target_col], errors="coerce"
        ).fillna(0)

        branch_data["Achievement %"] = branch_data.apply(
            lambda x: (x[branch_revenue_col] / x[branch_target_col] * 100)
            if x[branch_target_col] > 0
            else 0,
            axis=1,
        )

    if branch_profit_col != "None":
        branch_data[branch_profit_col] = pd.to_numeric(
            branch_data[branch_profit_col], errors="coerce"
        ).fillna(0) 

    fig = px.bar(
        branch_data.sort_values(branch_revenue_col, ascending=False),
        x=branch_col,
        y=branch_revenue_col,
        title="Branch Revenue Performance",
        text_auto=True,
    )
    st.plotly_chart(fig, use_container_width=True)

    if branch_target_col != "None":
        fig = px.bar(
            branch_data.sort_values("Achievement %", ascending=False),
            x=branch_col,
            y="Achievement %",
            title="Branch Target Achievement %",
            text_auto=True,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.session_state["branch_performance_dashboard_df"] = branch_data

elif sales_df is not None and not sales_df.empty:
    st.info("Branch performance data not uploaded. You can still generate branch performance from Sales Data.")

    sales_data = sales_df.copy()
    sales_columns = list(sales_data.columns)

    col1, col2 = st.columns(2)

    with col1:
        sales_branch_col = st.selectbox("Sales Branch Column", ["None"] + sales_columns, key="sales_branch_dashboard_col")

    with col2:
        sales_amount_col = st.selectbox("Sales Amount Column", sales_columns, key="sales_amount_dashboard_col")

    if sales_branch_col != "None":
        sales_data[sales_amount_col] = pd.to_numeric(
            sales_data[sales_amount_col], errors="coerce"
        ).fillna(0)

        branch_sales = (
            sales_data.groupby(sales_branch_col, as_index=False)[sales_amount_col]
            .sum()
            .sort_values(sales_amount_col, ascending=False)
        )

        st.dataframe(branch_sales, use_container_width=True)

        fig = px.bar(
            branch_sales,
            x=sales_branch_col,
            y=sales_amount_col,
            title="Branch Revenue from Sales Data",
            text_auto=True,
        )
        st.plotly_chart(fig, use_container_width=True)

        st.session_state["branch_performance_dashboard_df"] = branch_sales
else:
    st.info("Upload Branch Performance Data or Sales Data to view branch performance.")

# ==========================================================
# PRODUCT PERFORMANCE
# ==========================================================
st.markdown("## Product Performance")

if sales_df is not None and not sales_df.empty:
    sales_data = sales_df.copy()
    sales_columns = list(sales_data.columns)

    col1, col2 = st.columns(2)

    with col1:
        product_col = st.selectbox("Product/Service Column", ["None"] + sales_columns, key="dash_product_col")

    with col2:
        product_amount_col = st.selectbox("Revenue Amount Column", sales_columns, key="dash_product_amount_col")

    if product_col != "None":
        sales_data[product_amount_col] = pd.to_numeric(
            sales_data[product_amount_col], errors="coerce"
        ).fillna(0)

        product_performance = (
            sales_data.groupby(product_col, as_index=False)[product_amount_col]
            .sum()
            .sort_values(product_amount_col, ascending=False)
        )

        total_product_revenue = product_performance[product_amount_col].sum()
        product_performance["Revenue Share %"] = product_performance[product_amount_col].apply(
            lambda x: (x / total_product_revenue * 100) if total_product_revenue > 0 else 0
        )

        st.dataframe(product_performance, use_container_width=True)

        fig = px.bar(
            product_performance,
            x=product_col,
            y=product_amount_col,
            title="Product / Service Revenue Performance",
            text_auto=True,
        )
        st.plotly_chart(fig, use_container_width=True)

        fig = px.pie(
            product_performance,
            names=product_col,
            values=product_amount_col,
            title="Product / Service Revenue Share",
        )
        st.plotly_chart(fig, use_container_width=True)

        st.session_state["product_performance_dashboard_df"] = product_performance

    else:
        st.info("Select a product/service column to view product performance.")
else:
    st.info("Upload Sales Data to view product performance.")

# ==========================================================
# SAVE DASHBOARD OUTPUTS TO SUPABASE
# ==========================================================
st.markdown("## Save Dashboard Outputs")

if st.button("Save Dashboard Outputs to Supabase"):
    project = st.session_state.get("active_project")

    if not project:
        st.warning("No active project found. Please ensure Company Profile is saved first.")
    else:
        try:
            if st.session_state.get("risk_heatmap_df") is not None:
                save_analysis_output(
                    project_id=project.get("id"),
                    analysis_type="risk_heatmap",
                    total_value=profit_improvement_potential,
                    df=st.session_state["risk_heatmap_df"],
                )

            if st.session_state.get("branch_performance_dashboard_df") is not None:
                save_analysis_output(
                    project_id=project.get("id"),
                    analysis_type="branch_performance",
                    total_value=profit_improvement_potential,
                    df=st.session_state["branch_performance_dashboard_df"],
                )

            if st.session_state.get("product_performance_dashboard_df") is not None:
                save_analysis_output(
                    project_id=project.get("id"),
                    analysis_type="product_performance",
                    total_value=profit_improvement_potential,
                    df=st.session_state["product_performance_dashboard_df"],
                )

            if st.session_state.get("benchmark_df") is not None:
                save_analysis_output(
                    project_id=project.get("id"),
                    analysis_type="industry_benchmarking",
                    total_value=profit_improvement_potential,
                    df=st.session_state["benchmark_df"],
                )

            if st.session_state.get("branch_risk_heatmap_df") is not None:
                save_analysis_output(
                    project_id=project.get("id"),
                    analysis_type="branch_risk_heatmap",
                    total_value=profit_improvement_potential,
                    df=st.session_state["branch_risk_heatmap_df"],
                )

            if st.session_state.get("cost_concentration_heatmap_df") is not None:
                save_analysis_output(
                    project_id=project.get("id"),
                    analysis_type="cost_concentration_heatmap",
                    total_value=profit_improvement_potential,
                    df=st.session_state["cost_concentration_heatmap_df"],
                )

            if st.session_state.get("leakage_risk_matrix_df") is not None:
                save_analysis_output(
                    project_id=project.get("id"),
                    analysis_type="leakage_risk_matrix",
                    total_value=profit_improvement_potential,
                    df=st.session_state["leakage_risk_matrix_df"],
                )

            if st.session_state.get("profitability_heatmap_df") is not None:
                save_analysis_output(
                    project_id=project.get("id"),
                    analysis_type="profitability_heatmap",
                    total_value=profit_improvement_potential,
                    df=st.session_state["profitability_heatmap_df"],
                )


            if st.session_state.get("revenue_forecast_df") is not None:
                save_analysis_output(
                    project_id=project.get("id"),
                    analysis_type="revenue_forecast",
                    total_value=profit_improvement_potential,
                    df=st.session_state["revenue_forecast_df"],
                )

            if st.session_state.get("cost_forecast_df") is not None:
                save_analysis_output(
                    project_id=project.get("id"),
                    analysis_type="cost_forecast",
                    total_value=profit_improvement_potential,
                    df=st.session_state["cost_forecast_df"],
                )

            if st.session_state.get("profit_forecast_df") is not None:
                save_analysis_output(
                    project_id=project.get("id"),
                    analysis_type="profit_forecast",
                    total_value=profit_improvement_potential,
                    df=st.session_state["profit_forecast_df"],
                )

            st.success("Dashboard outputs saved successfully to Supabase.")

        except Exception as e:
            st.error(f"Could not save dashboard outputs to Supabase: {e}")

# ==========================================================
# AI-STYLE EXECUTIVE INSIGHTS
# ==========================================================
st.markdown("## AI-Style Executive Insights")

insights = generate_executive_dashboard_insights(
    total_revenue_opportunity=total_revenue_opportunity,
    total_leakage_exposure=total_leakage_exposure,
    total_cost_saving=total_cost_saving,
    priority_df=st.session_state.get("priority_action_df"),
)

for insight in insights:
    st.info(insight)

# ==========================================================
# INITIALIZE AI SESSION STATE
# ==========================================================
if "ai_dashboard_summary" not in st.session_state:
    st.session_state["ai_dashboard_summary"] = ""

if "ai_forecast_commentary" not in st.session_state:
    st.session_state["ai_forecast_commentary"] = ""

if "ai_benchmark_commentary" not in st.session_state:
    st.session_state["ai_benchmark_commentary"] = ""

if "ai_heatmap_commentary" not in st.session_state:
    st.session_state["ai_heatmap_commentary"] = ""

# ==========================================================
# INITIALIZE AI SESSION STATE
# ==========================================================
if "ai_dashboard_summary" not in st.session_state:
    st.session_state["ai_dashboard_summary"] = ""

if "ai_forecast_commentary" not in st.session_state:
    st.session_state["ai_forecast_commentary"] = ""

# ==========================================================
# AI PREMIUM EXECUTIVE DASHBOARD COMMENTARY
# ==========================================================
st.markdown("## AI Premium Executive Dashboard Commentary")

company_profile = st.session_state.get("company_profile", {})
company_name = company_profile.get("company_name", "the company")

dashboard_summary = {
    "total_revenue_opportunity": total_revenue_opportunity,
    "total_leakage_exposure": total_leakage_exposure,
    "total_cost_saving": total_cost_saving,
    "profit_improvement_potential": profit_improvement_potential,
}

# ==========================================================
# DASHBOARD SUMMARY + FORECAST
# ==========================================================
col1, col2 = st.columns(2)

with col1:
    if st.button("Generate AI Executive Dashboard Summary"):
        with st.spinner("Generating AI executive dashboard summary..."):
            ai_dashboard_summary = generate_ai_dashboard_summary(
                company_name=company_name,
                dashboard_summary=dashboard_summary,
                priority_action_df=st.session_state.get("priority_action_df"),
                benchmark_df=st.session_state.get("benchmark_df"),
                risk_heatmap_df=st.session_state.get("risk_heatmap_df"),
                forecast_df=st.session_state.get("profit_forecast_df"),
            )

        st.session_state["ai_dashboard_summary"] = ai_dashboard_summary

with col2:
    if st.button("Generate AI Forecast Commentary"):
        with st.spinner("Generating AI forecast commentary..."):
            ai_forecast_commentary = generate_ai_forecast_commentary(
                company_name=company_name,
                revenue_forecast_df=st.session_state.get("revenue_forecast_df"),
                cost_forecast_df=st.session_state.get("cost_forecast_df"),
                profit_forecast_df=st.session_state.get("profit_forecast_df"),
            )

        st.session_state["ai_forecast_commentary"] = ai_forecast_commentary

# ==========================================================
# DISPLAY SAVED AI COMMENTARY
# ==========================================================
if st.session_state.get("ai_dashboard_summary"):
    st.markdown("### Executive Dashboard Summary")
    st.markdown(st.session_state["ai_dashboard_summary"])

if st.session_state.get("ai_forecast_commentary"):
    st.markdown("### Forecast Commentary")
    st.markdown(st.session_state["ai_forecast_commentary"])

# ==========================================================
# BENCHMARK + HEATMAP
# ==========================================================
col1, col2 = st.columns(2)

with col1:
    if st.button("Generate AI Benchmark Commentary"):
        with st.spinner("Generating AI benchmark commentary..."):
            ai_benchmark_commentary = generate_ai_benchmark_commentary(
                company_name=company_name,
                benchmark_df=st.session_state.get("benchmark_df"),
            )

        st.session_state["ai_benchmark_commentary"] = ai_benchmark_commentary

with col2:
    if st.button("Generate AI Heatmap Commentary"):
        with st.spinner("Generating AI heatmap commentary..."):
            ai_heatmap_commentary = generate_ai_heatmap_commentary(
                company_name=company_name,
                branch_risk_heatmap_df=st.session_state.get("branch_risk_heatmap_df"),
                cost_concentration_heatmap_df=st.session_state.get("cost_concentration_heatmap_df"),
                leakage_risk_matrix_df=st.session_state.get("leakage_risk_matrix_df"),
                profitability_heatmap_df=st.session_state.get("profitability_heatmap_df"),
            )

        st.session_state["ai_heatmap_commentary"] = ai_heatmap_commentary

# ==========================================================
# DISPLAY SAVED AI COMMENTARY
# ==========================================================
if st.session_state.get("ai_dashboard_summary"):
    st.markdown("### Executive Dashboard Summary")
    st.markdown(st.session_state["ai_dashboard_summary"])

if st.session_state.get("ai_forecast_commentary"):
    st.markdown("### Forecast Commentary")
    st.markdown(st.session_state["ai_forecast_commentary"])

if st.session_state.get("ai_benchmark_commentary"):
    st.markdown("### Benchmark Commentary")
    st.markdown(st.session_state["ai_benchmark_commentary"])

if st.session_state.get("ai_heatmap_commentary"):
    st.markdown("### Heatmap Commentary")
    st.markdown(st.session_state["ai_heatmap_commentary"])
# ==========================================================
# RECOMMENDED 90-DAY FOCUS
# ==========================================================
st.markdown("## Recommended 90-Day Focus")

focus_items = []

if total_leakage_exposure > 0:
    focus_items.append("Validate and recover confirmed revenue leakages.")
if total_revenue_opportunity > 0:
    focus_items.append("Execute targeted revenue growth actions by product, customer, and branch.")
if total_cost_saving > 0:
    focus_items.append("Implement cost-control actions across major cost drivers.")
if priority_frames:
    focus_items.append("Assign owners and timelines to the top 10 priority actions.")

focus_items.append("Track actual recovery, savings, and revenue improvement weekly.")

for item in focus_items:
    st.write(f"✅ {item}")

# ==========================================================
# NAVIGATION
# ==========================================================
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Back: Cost Review"):
        st.switch_page("pages/05_Cost_Review.py")

with col2:
    if st.button("Next: Action Plan Tracker"):
        st.switch_page("pages/07_Action_Plan_Tracker.py")

with col3:
    if st.button("Go to Executive Report"):
        st.switch_page("pages/08_Executive_Report.py")
