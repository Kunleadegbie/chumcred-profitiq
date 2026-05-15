import streamlit as st
import pandas as pd
import plotly.express as px
from modules.ai_insights import generate_cost_insights

# Optional real OpenAI cost insight layer
try:
    from modules.openai_ai import generate_ai_cost_review
except Exception:
    generate_ai_cost_review = None

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="Cost Review | Chumcred ProfitIQ",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# AUTH PROTECTION
# ==========================================================
from auth import require_login

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
        <div class="page-title">Cost Review</div>
        <div class="page-subtitle">
            Review expense patterns, identify high-cost areas, compare cost categories,
            and estimate practical cost-saving opportunities without weakening business operations.
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
# GET DATA
# ==========================================================
expense_df = st.session_state.get("expense_data")
sales_df = st.session_state.get("sales_data")
payroll_df = st.session_state.get("payroll_data")
vendor_df = st.session_state.get("vendor_data")

if expense_df is None and payroll_df is None and vendor_df is None:
    st.warning("No cost-related data uploaded yet. Please upload Expense, Payroll, or Vendor Data first.")
    if st.button("Go to Financial Upload"):
        st.switch_page("pages/02_Financial_Upload.py")
    st.stop()

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================
def fix_bad_csv_dataframe(df):
    """
    Fixes files read as one combined comma-separated column.
    """
    if df is None or df.empty:
        return df

    if len(df.columns) == 1 and "," in str(df.columns[0]):
        single_col = df.columns[0]
        fixed_df = df[single_col].astype(str).str.split(",", expand=True)
        fixed_df.columns = [col.strip() for col in str(single_col).split(",")]
        return fixed_df

    return df


def safe_numeric(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)


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


def safe_selectbox(label, options, key, default_index=0):
    if not options:
        st.warning(f"No valid options available for {label}.")
        return None

    return st.selectbox(label, options, key=key, index=default_index)


def add_saving_item(area, observation, estimated_saving, recommendation, priority):
    cost_saving_items.append(
        {
            "Cost Area": area,
            "Observation": observation,
            "Estimated Cost Saving": float(estimated_saving) if estimated_saving else 0,
            "Recommended Action": recommendation,
            "Priority": priority,
        }
    )


# Fix badly-read CSVs
expense_df = fix_bad_csv_dataframe(expense_df)
sales_df = fix_bad_csv_dataframe(sales_df)
payroll_df = fix_bad_csv_dataframe(payroll_df)
vendor_df = fix_bad_csv_dataframe(vendor_df)

# Update session state after fixing
if expense_df is not None:
    st.session_state["expense_data"] = expense_df
if sales_df is not None:
    st.session_state["sales_data"] = sales_df
if payroll_df is not None:
    st.session_state["payroll_data"] = payroll_df
if vendor_df is not None:
    st.session_state["vendor_data"] = vendor_df

cost_saving_items = []
total_expense = 0
total_revenue = 0
total_payroll = 0
total_vendor_cost = 0

# ==========================================================
# EXPENSE REVIEW
# ==========================================================
if expense_df is not None:
    st.markdown("## 1. Expense Cost Review")

    exp = expense_df.copy()
    exp_columns = list(exp.columns)
    exp_numeric_columns = get_numeric_like_columns(exp)
    exp_date_columns = get_date_like_columns(exp)

    if not exp_numeric_columns:
        st.error("No numeric expense amount column detected. Please check your Expense Data.")
    else:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            exp_date_col = st.selectbox(
                "Expense Date Column",
                ["None"] + exp_date_columns,
                key="cost_exp_date_col",
            )

        with col2:
            exp_amount_col = st.selectbox(
                "Expense Amount Column",
                exp_numeric_columns,
                key="cost_exp_amount_col",
            )

        with col3:
            exp_category_col = st.selectbox(
                "Expense Category Column",
                ["None"] + exp_columns,
                key="cost_exp_category_col",
            )

        with col4:
            exp_department_col = st.selectbox(
                "Department/Branch Column",
                ["None"] + exp_columns,
                key="cost_exp_department_col",
            )

        exp[exp_amount_col] = safe_numeric(exp[exp_amount_col])

        total_expense = exp[exp_amount_col].sum()
        avg_expense = exp[exp_amount_col].mean()
        highest_expense = exp[exp_amount_col].max()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Expenses Reviewed", f"₦{total_expense:,.0f}")
        col2.metric("Average Expense Value", f"₦{avg_expense:,.0f}")
        col3.metric("Highest Expense Value", f"₦{highest_expense:,.0f}")

        if exp_category_col != "None":
            category_cost = (
                exp.groupby(exp_category_col, as_index=False)[exp_amount_col]
                .sum()
                .sort_values(exp_amount_col, ascending=False)
            )

            st.markdown("### Cost by Category")
            st.dataframe(category_cost, use_container_width=True)

            fig = px.bar(
                category_cost.head(10),
                x=exp_category_col,
                y=exp_amount_col,
                title="Top 10 Cost Categories",
            )
            st.plotly_chart(fig, use_container_width=True)

            top_category = category_cost.iloc[0]
            top_category_share = (
                top_category[exp_amount_col] / total_expense * 100
                if total_expense > 0
                else 0
            )

            if top_category_share >= 30:
                add_saving_item(
                    "High Cost Concentration",
                    f"{top_category[exp_category_col]} accounts for {top_category_share:.1f}% of total reviewed expenses.",
                    top_category[exp_amount_col] * 0.10,
                    "Review contracts, usage pattern, approval limits, pricing, and alternative suppliers for this cost category.",
                    "High",
                )

        if exp_department_col != "None":
            department_cost = (
                exp.groupby(exp_department_col, as_index=False)[exp_amount_col]
                .sum()
                .sort_values(exp_amount_col, ascending=False)
            )

            st.markdown("### Cost by Department / Branch")
            st.dataframe(department_cost, use_container_width=True)

            fig = px.bar(
                department_cost,
                x=exp_department_col,
                y=exp_amount_col,
                title="Cost by Department / Branch",
            )
            st.plotly_chart(fig, use_container_width=True)

            avg_department_cost = department_cost[exp_amount_col].mean()
            high_cost_units = department_cost[department_cost[exp_amount_col] > avg_department_cost * 1.5]

            if not high_cost_units.empty:
                add_saving_item(
                    "High-Cost Department / Branch",
                    f"{len(high_cost_units)} departments/branches are spending more than 1.5x the average cost level.",
                    high_cost_units[exp_amount_col].sum() * 0.08,
                    "Review operational efficiency, staff productivity, procurement discipline, and approval controls in high-cost units.",
                    "Medium",
                )

        if exp_date_col != "None":
            try:
                exp[exp_date_col] = pd.to_datetime(exp[exp_date_col], errors="coerce")
                exp = exp.dropna(subset=[exp_date_col])
                exp["Month"] = exp[exp_date_col].dt.to_period("M").astype(str)

                monthly_cost = exp.groupby("Month", as_index=False)[exp_amount_col].sum()
                monthly_cost = monthly_cost.sort_values("Month")

                st.markdown("### Monthly Cost Trend")
                fig = px.line(
                    monthly_cost,
                    x="Month",
                    y=exp_amount_col,
                    markers=True,
                    title="Monthly Cost Trend",
                )
                st.plotly_chart(fig, use_container_width=True)

                if len(monthly_cost) >= 2:
                    latest_cost = monthly_cost.iloc[-1][exp_amount_col]
                    previous_cost = monthly_cost.iloc[-2][exp_amount_col]

                    if latest_cost > previous_cost:
                        cost_increase = latest_cost - previous_cost
                        add_saving_item(
                            "Recent Cost Increase",
                            "Latest month cost is higher than the previous month.",
                            cost_increase * 0.25,
                            "Investigate the main drivers of the recent cost increase and introduce spending controls.",
                            "High",
                        )
            except Exception:
                st.info("Could not generate monthly cost trend from selected date column.")

# ==========================================================
# COST TO REVENUE RATIO
# ==========================================================
if expense_df is not None and sales_df is not None:
    st.markdown("## 2. Cost-to-Revenue Review")

    sales = sales_df.copy()
    sales_columns = list(sales.columns)
    sales_numeric_columns = get_numeric_like_columns(sales)

    if not sales_numeric_columns:
        st.error("No numeric revenue column detected in Sales Data. Please check your Sales Data.")
    else:
        revenue_col = st.selectbox(
            "Select Revenue Amount Column",
            sales_numeric_columns,
            key="cost_revenue_col",
        )

        sales[revenue_col] = safe_numeric(sales[revenue_col])

        total_revenue = sales[revenue_col].sum()
        total_cost = total_expense
        cost_to_revenue = (total_cost / total_revenue * 100) if total_revenue > 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Revenue", f"₦{total_revenue:,.0f}")
        col2.metric("Total Cost", f"₦{total_cost:,.0f}")
        col3.metric("Cost-to-Revenue Ratio", f"{cost_to_revenue:.1f}%")

        if total_revenue <= 0:
            st.warning(
                "Total revenue is zero. Please ensure you selected the correct revenue amount column."
            )

        if cost_to_revenue >= 70:
            add_saving_item(
                "High Cost-to-Revenue Ratio",
                f"Cost-to-revenue ratio is {cost_to_revenue:.1f}%, which may be putting pressure on profitability.",
                total_cost * 0.10,
                "Review pricing, cost structure, procurement, staffing, logistics, and product profitability.",
                "High",
            )
        elif cost_to_revenue >= 50:
            add_saving_item(
                "Moderate Cost Pressure",
                f"Cost-to-revenue ratio is {cost_to_revenue:.1f}%. There may be room for cost optimization.",
                total_cost * 0.05,
                "Review top cost drivers and identify quick savings without disrupting operations.",
                "Medium",
            )

# ==========================================================
# PAYROLL REVIEW
# ==========================================================
if payroll_df is not None:
    st.markdown("## 3. Payroll / Staff Cost Review")

    pay = payroll_df.copy()
    pay_columns = list(pay.columns)
    pay_numeric_columns = get_numeric_like_columns(pay)

    if not pay_numeric_columns:
        st.error("No numeric payroll amount column detected. Please check your Payroll Data.")
    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            payroll_amount_col = st.selectbox(
                "Payroll Amount Column",
                pay_numeric_columns,
                key="payroll_amount_col",
            )

        with col2:
            payroll_department_col = st.selectbox(
                "Department/Branch Column",
                ["None"] + pay_columns,
                key="payroll_department_col",
            )

        with col3:
            payroll_staff_col = st.selectbox(
                "Staff/Employee Column",
                ["None"] + pay_columns,
                key="payroll_staff_col",
            )

        pay[payroll_amount_col] = safe_numeric(pay[payroll_amount_col])

        total_payroll = pay[payroll_amount_col].sum()
        avg_payroll = pay[payroll_amount_col].mean()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Payroll Cost", f"₦{total_payroll:,.0f}")
        col2.metric("Average Staff Cost", f"₦{avg_payroll:,.0f}")
        col3.metric("Payroll Records", f"{len(pay):,.0f}")

        if payroll_department_col != "None":
            payroll_by_department = (
                pay.groupby(payroll_department_col, as_index=False)[payroll_amount_col]
                .sum()
                .sort_values(payroll_amount_col, ascending=False)
            )

            st.markdown("### Payroll by Department / Branch")
            st.dataframe(payroll_by_department, use_container_width=True)

            fig = px.bar(
                payroll_by_department,
                x=payroll_department_col,
                y=payroll_amount_col,
                title="Payroll Cost by Department / Branch",
            )
            st.plotly_chart(fig, use_container_width=True)

            avg_dept_payroll = payroll_by_department[payroll_amount_col].mean()
            high_payroll_units = payroll_by_department[
                payroll_by_department[payroll_amount_col] > avg_dept_payroll * 1.5
            ]

            if not high_payroll_units.empty:
                add_saving_item(
                    "High Payroll Cost Unit",
                    f"{len(high_payroll_units)} departments/branches have payroll cost above 1.5x the average.",
                    high_payroll_units[payroll_amount_col].sum() * 0.05,
                    "Review staff deployment, productivity, overtime, role duplication, and revenue contribution by unit.",
                    "Medium",
                )

# ==========================================================
# VENDOR COST REVIEW
# ==========================================================
if vendor_df is not None:
    st.markdown("## 4. Vendor / Supplier Cost Review")

    vendor = vendor_df.copy()
    vendor_columns = list(vendor.columns)
    vendor_numeric_columns = get_numeric_like_columns(vendor)

    if not vendor_numeric_columns:
        st.error("No numeric vendor amount column detected. Please check your Vendor Data.")
    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            vendor_name_col = st.selectbox(
                "Vendor Name Column",
                ["None"] + vendor_columns,
                key="cost_vendor_name_col",
            )

        with col2:
            vendor_amount_col = st.selectbox(
                "Vendor Amount Column",
                vendor_numeric_columns,
                key="cost_vendor_amount_col",
            )

        with col3:
            vendor_category_col = st.selectbox(
                "Vendor Category Column",
                ["None"] + vendor_columns,
                key="cost_vendor_category_col",
            )

        vendor[vendor_amount_col] = safe_numeric(vendor[vendor_amount_col])

        total_vendor_cost = vendor[vendor_amount_col].sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Vendor Cost", f"₦{total_vendor_cost:,.0f}")
        col2.metric("Vendor Records", f"{len(vendor):,.0f}")
        col3.metric("Average Vendor Transaction", f"₦{vendor[vendor_amount_col].mean():,.0f}")

        if vendor_name_col != "None":
            vendor_cost = (
                vendor.groupby(vendor_name_col, as_index=False)[vendor_amount_col]
                .sum()
                .sort_values(vendor_amount_col, ascending=False)
            )

            st.markdown("### Top Vendors by Cost")
            st.dataframe(vendor_cost.head(20), use_container_width=True)

            fig = px.bar(
                vendor_cost.head(10),
                x=vendor_name_col,
                y=vendor_amount_col,
                title="Top 10 Vendors by Cost",
            )
            st.plotly_chart(fig, use_container_width=True)

            top_vendor = vendor_cost.iloc[0]
            top_vendor_share = (
                top_vendor[vendor_amount_col] / total_vendor_cost * 100
                if total_vendor_cost > 0
                else 0
            )

            if top_vendor_share >= 25:
                add_saving_item(
                    "High Vendor Dependency",
                    f"{top_vendor[vendor_name_col]} accounts for {top_vendor_share:.1f}% of total vendor cost.",
                    top_vendor[vendor_amount_col] * 0.07,
                    "Renegotiate vendor pricing, review alternative suppliers, and strengthen procurement comparison.",
                    "Medium",
                )

# ==========================================================
# COST SAVINGS REPORT
# ==========================================================
st.markdown("---")
st.markdown("## Cost Savings Report")

if cost_saving_items:
    cost_saving_df = pd.DataFrame(cost_saving_items)
else:
    cost_saving_df = pd.DataFrame(
        [
            {
                "Cost Area": "No Major Cost Saving Automatically Detected",
                "Observation": "Current uploaded data did not produce major automated cost-saving red flags.",
                "Estimated Cost Saving": 0,
                "Recommended Action": "Conduct deeper review of contracts, vendors, procurement, staffing, utilities, logistics, and operating processes.",
                "Priority": "Review",
            }
        ]
    )

st.dataframe(cost_saving_df, use_container_width=True)

total_cost_saving = cost_saving_df["Estimated Cost Saving"].sum()

st.session_state["cost_saving_df"] = cost_saving_df
st.session_state["total_cost_saving"] = total_cost_saving

st.success(f"Estimated Cost Saving Opportunity: ₦{total_cost_saving:,.0f}")

# ==========================================================
# SAVE ANALYSIS OUTPUT TO SUPABASE
# ==========================================================
st.markdown("## Save Cost Review")

if st.button("Save Cost Review to Supabase"):
    project = st.session_state.get("active_project")

    if not project:
        st.warning("No active project found. Please ensure Company Profile is saved first.")
    else:
        try:
            save_analysis_output(
                project_id=project.get("id"),
                analysis_type="cost_saving",
                total_value=total_cost_saving,
                df=cost_saving_df,
            )
            st.success("Cost review output saved successfully to Supabase.")
        except Exception as e:
            st.error(f"Could not save cost review output to Supabase: {e}")

# ==========================================================
# AI-STYLE MANAGEMENT INSIGHTS
# ==========================================================
st.markdown("## AI-Style Management Insights")

insights = generate_cost_insights(
    total_cost_saving=total_cost_saving,
    cost_saving_df=cost_saving_df,
)

for insight in insights:
    st.info(insight)

# ==========================================================
# INITIALIZE AI SESSION STATE
# ==========================================================
if "ai_cost_commentary" not in st.session_state:
    st.session_state["ai_cost_commentary"] = ""

# ==========================================================
# AI PREMIUM COST COMMENTARY
# ==========================================================
st.markdown("## AI Premium Cost Commentary")

cost_summary = {
    "total_expense": total_expense,
    "total_revenue": total_revenue,
    "total_payroll": total_payroll,
    "total_vendor_cost": total_vendor_cost,
    "total_cost_saving": total_cost_saving,
}

if st.button("Generate AI Cost Commentary"):
    company_profile = st.session_state.get("company_profile", {})
    company_name = company_profile.get("company_name", "the company")

    if generate_ai_cost_review is None:
        st.warning("OpenAI module is not available. Please confirm modules/openai_ai.py exists.")
    else:
        with st.spinner("Generating AI-powered cost review commentary..."):
            ai_response = generate_ai_cost_review(
                company_name=company_name,
                cost_summary=cost_summary,
                cost_saving_df=cost_saving_df,
                expense_df=expense_df,
                payroll_df=payroll_df,
                vendor_df=vendor_df,
            )

        st.session_state["ai_cost_commentary"] = ai_response

if st.session_state.get("ai_cost_commentary"):
    st.markdown("### Generated Cost Commentary")
    st.markdown(st.session_state["ai_cost_commentary"])

# ==========================================================
# NAVIGATION
# ==========================================================
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Back: Leakage Detection"):
        st.switch_page("pages/04_Leakage_Detection.py")

with col2:
    if st.button("Next: Opportunity Dashboard"):
        st.switch_page("pages/06_Opportunity_Dashboard.py")

with col3:
    if st.button("Go to Report Generator"):
        st.switch_page("pages/08_Executive_Report.py")