import streamlit as st
import pandas as pd
import plotly.express as px
from modules.ai_insights import generate_revenue_insights
from modules.openai_ai import generate_ai_revenue_analysis
from modules.sector_labels import get_current_sector_labels

from modules.period_analysis import (
    filter_by_review_period,
    generate_period_trend,
    generate_multiyear_summary,
)

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="Revenue Analysis | Chumcred ProfitIQ",
    page_icon="📈",
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
from modules.supabase_helpers import get_or_create_active_project, save_analysis_output

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
        <div class="page-title">Revenue Analysis</div>
        <div class="page-subtitle">
            Analyze revenue trends, top-performing products, weak revenue areas, branch performance,
            and practical growth opportunities.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==========================================================
# SECTOR LABELS
# ==========================================================
sector_labels = get_current_sector_labels()

revenue_label = sector_labels.get("revenue", "Revenue")
sales_data_label = sector_labels.get("sales_data", "Sales Data")
customer_label = sector_labels.get("customer", "Customer")
product_label = sector_labels.get("product", "Product / Service")
branch_label = sector_labels.get("branch", "Branch / Location")
target_label = sector_labels.get("target", "Sales Target")
leakage_label = sector_labels.get("leakage", "Revenue Leakage")

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
# CHECK DATA
# ==========================================================
sales_df = st.session_state.get("sales_data")

if sales_df is None:
    st.warning("No Sales Data uploaded yet. Please upload Sales Data first.")
    if st.button("Go to Financial Upload"):
        st.switch_page("pages/02_Financial_Upload.py")
    st.stop()

df = sales_df.copy()

# ==========================================================
# COLUMN MAPPING
# ==========================================================
st.markdown("## Map Your Revenue Data Columns")

columns = list(df.columns)

# Detect likely numeric columns
# ==========================================================
# DETECT NUMERIC-LIKE COLUMNS SAFELY
# ==========================================================
# ==========================================================
# DETECT NUMERIC-LIKE COLUMNS SAFELY
# ==========================================================
def get_numeric_like_columns(df):
    numeric_cols = []

    if df is None or df.empty:
        return numeric_cols

    for col in df.columns:

        # Skip obvious date columns
        if (
            "date" in str(col).lower()
            or "month" in str(col).lower()
            or "year" in str(col).lower()
        ):
            continue

        # Skip datetime-like columns
        try:
            converted_date = pd.to_datetime(df[col], errors="coerce")

            if converted_date.notna().sum() > len(df) * 0.7:
                continue

        except Exception:
            pass

        # Clean possible currency/commas/spaces
        cleaned_series = (
            df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("₦", "", regex=False)
            .str.strip()
        )

        converted_num = pd.to_numeric(cleaned_series, errors="coerce")

        # If at least some rows are numeric, accept it
        if converted_num.notna().sum() > 0:
            numeric_cols.append(col)

    return numeric_cols


numeric_like_columns = get_numeric_like_columns(df)

if not numeric_like_columns:
    st.error("No numeric revenue/amount column detected. Please check your uploaded Sales Data.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)

with col1:
    date_col = st.selectbox("Date Column", columns)

with col2:
    amount_col = st.selectbox(f"{revenue_label} Amount Column", numeric_like_columns)

with col3:
    product_col = st.selectbox(f"{product_label} Column", ["None"] + columns)

with col4:
    branch_col = st.selectbox(f"{branch_label} Column", ["None"] + columns)

col1, col2 = st.columns(2)

with col1:
    customer_col = st.selectbox(f"{customer_label} Column", ["None"] + columns)

with col2:
    target_col = st.selectbox(
        f"{target_label} Column (if available)",
        ["None"] + numeric_like_columns,
    )

# ==========================================================
# CLEAN DATA
# ==========================================================
try:
    df[amount_col] = (
        df[amount_col]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("₦", "", regex=False)
        .str.strip()
    )

    df[amount_col] = pd.to_numeric(df[amount_col], errors="coerce").fillna(0)   


df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col])
except Exception as e:
    st.error(f"Error preparing revenue data: {e}")
    st.stop()

df["Month"] = df[date_col].dt.to_period("M").astype(str)


# ==========================================================
# REVIEW PERIOD SETTINGS
# ==========================================================
company_profile = st.session_state.get("company_profile", {})

review_type = company_profile.get("review_type", "Single Period Review")
reporting_frequency = company_profile.get("reporting_frequency", "Monthly")
review_start_date = company_profile.get("review_start_date")
review_end_date = company_profile.get("review_end_date")

if review_type == "Multi-Year Trend Review":
    df = filter_by_review_period(
        df=df,
        date_col=date_col,
        start_date=review_start_date,
        end_date=review_end_date,
    )

    if df.empty:
        st.warning("No revenue data found within the selected multi-year review period.")
        st.stop()


# ==========================================================
# KPI SUMMARY
# ==========================================================
df[amount_col] = pd.to_numeric(df[amount_col], errors="coerce").fillna(0)
total_revenue = df[amount_col].sum()
average_monthly_revenue = df.groupby("Month")[amount_col].sum().mean()
transaction_count = len(df)
average_transaction_value = total_revenue / transaction_count if transaction_count > 0 else 0

st.markdown("## Revenue Performance Summary")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Revenue", f"₦{total_revenue:,.0f}")
col2.metric("Average Monthly Revenue", f"₦{average_monthly_revenue:,.0f}")
col3.metric("Transaction Count", f"{transaction_count:,.0f}")
col4.metric("Average Transaction Value", f"₦{average_transaction_value:,.0f}")

# ==========================================================
# MONTHLY TREND
# ==========================================================
st.markdown("## Monthly Revenue Trend")

monthly_revenue = df.groupby("Month", as_index=False)[amount_col].sum()
monthly_revenue = monthly_revenue.sort_values("Month")

fig = px.line(
    monthly_revenue,
    x="Month",
    y=amount_col,
    markers=True,
    title=f"Monthly {revenue_label} Trend",
)
st.plotly_chart(fig, use_container_width=True)


# ==========================================================
# MULTI-YEAR REVENUE TREND
# ==========================================================
if review_type == "Multi-Year Trend Review":
    st.markdown("## Multi-Year Revenue Trend")

    trend_df = generate_period_trend(
        df=df,
        date_col=date_col,
        value_col=amount_col,
        frequency=reporting_frequency,
    )

    if not trend_df.empty:
        st.dataframe(trend_df, use_container_width=True)

        fig = px.line(
            trend_df,
            x="Period",
            y=amount_col,
            markers=True,
            title=f"{reporting_frequency} Revenue Trend",
        )
        st.plotly_chart(fig, use_container_width=True)

        multiyear_summary = generate_multiyear_summary(
            trend_df=trend_df,
            value_col=amount_col,
        )

        st.session_state["revenue_trend_df"] = trend_df
        st.session_state["revenue_multiyear_summary"] = multiyear_summary

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Revenue in Review Period",
            f"₦{multiyear_summary.get('total_value', 0):,.0f}",
        )

        col2.metric(
            "Growth Amount",
            f"₦{multiyear_summary.get('growth_amount', 0):,.0f}",
        )

        col3.metric(
            "Growth %",
            f"{multiyear_summary.get('growth_percent', 0):.1f}%",
        )

        col4.metric(
            "CAGR",
            f"{multiyear_summary.get('cagr', 0):.1f}%",
        )

        st.info(
            f"Best revenue period: {multiyear_summary.get('best_period')} "
            f"with ₦{multiyear_summary.get('best_period_value', 0):,.0f}. "
            f"Weakest revenue period: {multiyear_summary.get('worst_period')} "
            f"with ₦{multiyear_summary.get('worst_period_value', 0):,.0f}."
        )
    else:
        st.info("Multi-year revenue trend could not be generated from the selected columns.")


# ==========================================================
# PRODUCT ANALYSIS
# ==========================================================
product_revenue = pd.DataFrame()

if product_col != "None":
    st.markdown("## Revenue by Product / Service")

    product_revenue = (
        df.groupby(product_col, as_index=False)[amount_col]
        .sum()
        .sort_values(amount_col, ascending=False)
    )

    col1, col2 = st.columns(2)

    with col1:
        st.dataframe(product_revenue, use_container_width=True)

    with col2:
        fig = px.bar(
            product_revenue.head(10),
            x=product_col,
            y=amount_col,
            title=f"{revenue_label} by {product_label}",
        )
        st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# BRANCH ANALYSIS
# ==========================================================
branch_revenue = pd.DataFrame()

if branch_col != "None":
    st.markdown("## Revenue by Branch / Location")

    branch_revenue = (
        df.groupby(branch_col, as_index=False)[amount_col]
        .sum()
        .sort_values(amount_col, ascending=False)
    )

    col1, col2 = st.columns(2)

    with col1:
        st.dataframe(branch_revenue, use_container_width=True)

    with col2:
        fig = px.bar(
            branch_revenue,
            x=branch_col,
            y=amount_col,
            title=f"{revenue_label} by {branch_label}",
        )
        st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# CUSTOMER ANALYSIS
# ==========================================================
customer_revenue = pd.DataFrame()

if customer_col != "None":
    st.markdown("## Revenue by Customer")

    customer_revenue = (
        df.groupby(customer_col, as_index=False)[amount_col]
        .sum()
        .sort_values(amount_col, ascending=False)
    )

    st.dataframe(customer_revenue.head(20), use_container_width=True)

    fig = px.bar(
        customer_revenue.head(10),
        x=customer_col,
        y=amount_col,
        title="Top 10 Customers by Revenue",
    )
    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# TARGET PERFORMANCE
# ==========================================================
if target_col != "None":
    st.markdown("## Revenue vs Target Analysis")

    df[target_col] = pd.to_numeric(df[target_col], errors="coerce").fillna(0)

    target_summary = df.groupby("Month", as_index=False).agg(
        Revenue=(amount_col, "sum"),
        Target=(target_col, "sum"),
    )

    target_summary["Achievement %"] = target_summary.apply(
        lambda x: (x["Revenue"] / x["Target"] * 100) if x["Target"] > 0 else 0,
        axis=1,
    )

    st.dataframe(target_summary, use_container_width=True)

    fig = px.bar(
        target_summary,
        x="Month",
        y=["Revenue", "Target"],
        barmode="group",
        title="Revenue vs Target",
    )
    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# REVENUE OPPORTUNITY MAP
# ==========================================================
st.markdown("## Revenue Opportunity Map")

opportunities = []

if len(monthly_revenue) >= 2:
    latest_revenue = monthly_revenue.iloc[-1][amount_col]
    previous_revenue = monthly_revenue.iloc[-2][amount_col]

    if latest_revenue < previous_revenue:
        gap = previous_revenue - latest_revenue
        opportunities.append(
            {
                "Opportunity Area": "Recover Recent Revenue Decline",
                "Observation": "Latest month revenue is below previous month.",
                "Estimated Revenue Opportunity": gap,
                "Recommended Action": "Review products, branches, and customers responsible for the decline.",
                "Priority": "High",
            }
        )

if product_col != "None" and not product_revenue.empty:
    avg_product_revenue = product_revenue[amount_col].mean()
    weak_products = product_revenue[product_revenue[amount_col] < avg_product_revenue]

    if not weak_products.empty:
        opportunities.append(
            {
                "Opportunity Area": "Improve Weak Product Performance",
                "Observation": f"{len(weak_products)} products/services are below average revenue contribution.",
                "Estimated Revenue Opportunity": avg_product_revenue * len(weak_products) * 0.20,
                "Recommended Action": "Review pricing, sales effort, visibility, bundling, and customer demand for weak products.",
                "Priority": "Medium",
            }
        )

if branch_col != "None" and not branch_revenue.empty:
    avg_branch_revenue = branch_revenue[amount_col].mean()
    weak_branches = branch_revenue[branch_revenue[amount_col] < avg_branch_revenue]

    if not weak_branches.empty:
        opportunities.append(
            {
                "Opportunity Area": "Improve Underperforming Branches",
                "Observation": f"{len(weak_branches)} branches are below average revenue contribution.",
                "Estimated Revenue Opportunity": avg_branch_revenue * len(weak_branches) * 0.15,
                "Recommended Action": "Review branch leadership, location potential, sales discipline, customer coverage, and local competition.",
                "Priority": "High",
            }
        )

if customer_col != "None" and not customer_revenue.empty:
    if len(customer_revenue) >= 5:
        bottom_customers = customer_revenue.tail(5)
        estimated_customer_opportunity = bottom_customers[amount_col].mean() * 5 * 0.25

        opportunities.append(
            {
                "Opportunity Area": "Increase Revenue from Low-Value Customers",
                "Observation": "Several customers have low revenue contribution.",
                "Estimated Revenue Opportunity": estimated_customer_opportunity,
                "Recommended Action": "Create cross-selling, upselling, reactivation, and account management actions.",
                "Priority": "Medium",
            }
        )

if not opportunities:
    opportunities.append(
        {
            "Opportunity Area": "Revenue Growth Review Required",
            "Observation": "No major automated revenue gap detected from current dataset.",
            "Estimated Revenue Opportunity": 0,
            "Recommended Action": "Conduct deeper review by product, customer, pricing, market, and branch performance.",
            "Priority": "Review",
        }
    )

opportunity_df = pd.DataFrame(opportunities)

st.dataframe(opportunity_df, use_container_width=True)

total_revenue_opportunity = opportunity_df["Estimated Revenue Opportunity"].sum()

st.session_state["revenue_opportunity_df"] = opportunity_df
st.session_state["total_revenue_opportunity"] = total_revenue_opportunity

st.success(f"Estimated Revenue Opportunity Identified: ₦{total_revenue_opportunity:,.0f}")

# ==========================================================
# SAVE ANALYSIS OUTPUT TO SUPABASE
# ==========================================================
st.markdown(f"## {revenue_label} Analysis")

if st.button("Save Revenue Analysis to Supabase"):
    project = st.session_state.get("active_project")

    if not project:
        st.warning("No active project found. Please ensure Company Profile is saved first.")
    else:
        try:
            save_analysis_output(
                project_id=project.get("id"),
                analysis_type="revenue_opportunity",
                total_value=total_revenue_opportunity,
                df=opportunity_df,
            )
            st.success("Revenue analysis output saved successfully to Supabase.")
        except Exception as e:
            st.error(f"Could not save revenue analysis output to Supabase: {e}")

# ==========================================================
# AI-STYLE BUSINESS INSIGHTS
# ==========================================================
st.markdown("## AI-Style Management Insights")

insights = generate_revenue_insights(
    total_revenue=total_revenue,
    average_monthly_revenue=average_monthly_revenue,
    transaction_count=transaction_count,
    average_transaction_value=average_transaction_value,
    total_revenue_opportunity=total_revenue_opportunity,
    monthly_revenue_df=monthly_revenue,
)

for insight in insights:
    st.info(insight)


# ==========================================================
# AI PREMIUM REVENUE COMMENTARY
# ==========================================================
st.markdown(f"## AI Premium {revenue_label} Commentary")

revenue_summary = {
    "total_revenue": total_revenue,
    "average_monthly_revenue": average_monthly_revenue,
    "transaction_count": transaction_count,
    "average_transaction_value": average_transaction_value,
    "total_revenue_opportunity": total_revenue_opportunity,
}

if st.button("Generate AI Revenue Commentary"):
    company_profile = st.session_state.get("company_profile", {})
    company_name = company_profile.get("company_name", "the company")

    with st.spinner("Generating AI-powered revenue commentary..."):
        ai_revenue_commentary = generate_ai_revenue_analysis(
            company_name=company_name,
            revenue_summary=revenue_summary,
            monthly_revenue_df=monthly_revenue,
            product_revenue_df=product_revenue,
            branch_revenue_df=branch_revenue,
            customer_revenue_df=customer_revenue,
            revenue_opportunity_df=opportunity_df,
        )

    st.session_state["ai_revenue_commentary"] = ai_revenue_commentary

if st.session_state.get("ai_revenue_commentary"):
    st.markdown("### Generated Revenue Commentary")
    st.markdown(st.session_state["ai_revenue_commentary"])

# ==========================================================
# NAVIGATION
# ==========================================================
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Back: Financial Upload"):
        st.switch_page("pages/02_Financial_Upload.py")

with col2:
    if st.button("Next: Leakage Detection"):
        st.switch_page("pages/04_Leakage_Detection.py")

with col3:
    if st.button("Go to Dashboard"):
        st.switch_page("pages/06_Opportunity_Dashboard.py")