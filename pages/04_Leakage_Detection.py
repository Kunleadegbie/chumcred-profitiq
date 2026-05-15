import streamlit as st
import pandas as pd
import plotly.express as px
from modules.ai_insights import generate_leakage_insights
from modules.openai_ai import generate_ai_leakage_review


# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="Leakage Detection | Chumcred ProfitIQ",
    page_icon="🚨",
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
        <div class="page-title">Leakage Detection</div>
        <div class="page-subtitle">
            Detect possible revenue leakages, duplicate payments, abnormal expenses,
            excessive charges, collection gaps, and other areas where money may be leaving the business unnoticed.
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
# GET UPLOADED DATA
# ==========================================================
sales_df = st.session_state.get("sales_data")
expense_df = st.session_state.get("expense_data")
bank_df = st.session_state.get("bank_charges_data")
vendor_df = st.session_state.get("vendor_data")
inventory_df = st.session_state.get("inventory_data")

if sales_df is None and expense_df is None and bank_df is None and vendor_df is None and inventory_df is None:
    st.warning("No relevant data uploaded yet. Please upload Sales, Expense, Bank Charges, Vendor, or Inventory Data first.")
    if st.button("Go to Financial Upload"):
        st.switch_page("pages/02_Financial_Upload.py")
    st.stop()

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================
def safe_numeric(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)


def detect_duplicates(df, amount_col=None, date_col=None, vendor_col=None, desc_col=None):
    working_df = df.copy()
    subset_cols = []

    for col in [date_col, vendor_col, desc_col, amount_col]:
        if col and col != "None" and col in working_df.columns:
            subset_cols.append(col)

    if not subset_cols:
        return pd.DataFrame()

    return working_df[working_df.duplicated(subset=subset_cols, keep=False)]


def high_value_outliers(df, amount_col):
    working_df = df.copy()
    working_df[amount_col] = safe_numeric(working_df[amount_col])

    if working_df.empty:
        return pd.DataFrame()

    avg_value = working_df[amount_col].mean()
    threshold = avg_value * 2.5

    return working_df[working_df[amount_col] > threshold]


def create_leakage_item(area, observation, estimated_value, recommendation, priority):
    return {
        "Leakage Area": area,
        "Observation": observation,
        "Estimated Leakage Exposure": float(estimated_value) if estimated_value else 0,
        "Recommended Action": recommendation,
        "Priority": priority,
    }


leakage_items = []

# ==========================================================
# EXPENSE LEAKAGE ANALYSIS
# ==========================================================
if expense_df is not None:
    st.markdown("## 1. Expense Leakage Review")

    exp = expense_df.copy()
    exp_columns = list(exp.columns)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        exp_date_col = st.selectbox("Expense Date Column", ["None"] + exp_columns, key="exp_date_col")

    with col2:
        exp_amount_col = st.selectbox("Expense Amount Column", exp_columns, key="exp_amount_col")

    with col3:
        exp_vendor_col = st.selectbox("Expense Vendor Column", ["None"] + exp_columns, key="exp_vendor_col")

    with col4:
        exp_desc_col = st.selectbox("Expense Description Column", ["None"] + exp_columns, key="exp_desc_col")

    exp[exp_amount_col] = safe_numeric(exp[exp_amount_col])
    total_expense = exp[exp_amount_col].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Expenses Reviewed", f"₦{total_expense:,.0f}")
    col2.metric("Expense Records", f"{len(exp):,.0f}")
    col3.metric("Average Expense Value", f"₦{exp[exp_amount_col].mean():,.0f}")

    duplicate_expenses = detect_duplicates(
        exp,
        amount_col=exp_amount_col,
        date_col=exp_date_col,
        vendor_col=exp_vendor_col,
        desc_col=exp_desc_col,
    )

    if not duplicate_expenses.empty:
        duplicate_value = duplicate_expenses[exp_amount_col].sum()
        leakage_items.append(
            create_leakage_item(
                "Possible Duplicate Expense Payments",
                f"{len(duplicate_expenses)} possible duplicate expense records detected.",
                duplicate_value,
                "Review duplicate payments against invoices, approvals, and bank payment records.",
                "High",
            )
        )

        st.warning(f"Possible duplicate expenses detected: {len(duplicate_expenses)} records.")
        st.dataframe(duplicate_expenses, use_container_width=True)

    outlier_expenses = high_value_outliers(exp, exp_amount_col)

    if not outlier_expenses.empty:
        outlier_value = outlier_expenses[exp_amount_col].sum()
        leakage_items.append(
            create_leakage_item(
                "Abnormally High Expense Transactions",
                f"{len(outlier_expenses)} transactions are more than 2.5x the average expense value.",
                outlier_value * 0.20,
                "Validate high-value expenses against contracts, approvals, and expected business activity.",
                "Medium",
            )
        )

        st.info(f"High-value expense outliers detected: {len(outlier_expenses)} records.")
        st.dataframe(outlier_expenses, use_container_width=True)

    if exp_vendor_col != "None":
        vendor_summary = (
            exp.groupby(exp_vendor_col, as_index=False)[exp_amount_col]
            .sum()
            .sort_values(exp_amount_col, ascending=False)
        )

        st.markdown("### Top Vendors by Expense")
        st.dataframe(vendor_summary.head(10), use_container_width=True)

        fig = px.bar(
            vendor_summary.head(10),
            x=exp_vendor_col,
            y=exp_amount_col,
            title="Top 10 Vendors by Expense",
        )
        st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# BANK CHARGES LEAKAGE ANALYSIS
# ==========================================================
if bank_df is not None:
    st.markdown("## 2. Bank Charges Leakage Review")

    bank = bank_df.copy()
    bank_columns = list(bank.columns)

    col1, col2, col3 = st.columns(3)

    with col1:
        bank_date_col = st.selectbox("Bank Charge Date Column", ["None"] + bank_columns, key="bank_date_col")

    with col2:
        bank_amount_col = st.selectbox("Bank Charge Amount Column", bank_columns, key="bank_amount_col")

    with col3:
        bank_desc_col = st.selectbox("Bank Charge Description Column", ["None"] + bank_columns, key="bank_desc_col")

    bank[bank_amount_col] = safe_numeric(bank[bank_amount_col])
    total_bank_charges = bank[bank_amount_col].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Bank Charges Reviewed", f"₦{total_bank_charges:,.0f}")
    col2.metric("Bank Charge Records", f"{len(bank):,.0f}")
    col3.metric("Average Charge", f"₦{bank[bank_amount_col].mean():,.0f}")

    charge_threshold_percent = st.slider(
        "Expected Bank Charge Benchmark as % of Total Charges to Flag",
        min_value=5,
        max_value=50,
        value=15,
        key="bank_charge_threshold",
    )

    high_bank_charges = high_value_outliers(bank, bank_amount_col)

    if not high_bank_charges.empty:
        estimated_bank_leakage = high_bank_charges[bank_amount_col].sum() * (charge_threshold_percent / 100)

        leakage_items.append(
            create_leakage_item(
                "Potential Excess Bank Charges",
                f"{len(high_bank_charges)} bank charge records appear unusually high.",
                estimated_bank_leakage,
                "Review bank statements, facility letters, agreed rates, fees, and charge computations.",
                "High",
            )
        )

        st.warning(f"Unusually high bank charges detected: {len(high_bank_charges)} records.")
        st.dataframe(high_bank_charges, use_container_width=True)

# ==========================================================
# SALES / COLLECTION LEAKAGE ANALYSIS
# ==========================================================
if sales_df is not None:
    st.markdown("## 3. Revenue Collection & Sales Leakage Review")

    sales = sales_df.copy()
    sales_columns = list(sales.columns)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        sales_date_col = st.selectbox("Sales Date Column", ["None"] + sales_columns, key="sales_date_col_leakage")

    with col2:
        sales_amount_col = st.selectbox("Sales Amount Column", sales_columns, key="sales_amount_col_leakage")

    with col3:
        expected_amount_col = st.selectbox("Expected/Billed Amount Column, if available", ["None"] + sales_columns, key="expected_amount_col")

    with col4:
        collected_amount_col = st.selectbox("Collected Amount Column, if available", ["None"] + sales_columns, key="collected_amount_col")

    sales[sales_amount_col] = safe_numeric(sales[sales_amount_col])

    if expected_amount_col != "None" and collected_amount_col != "None":
        sales[expected_amount_col] = safe_numeric(sales[expected_amount_col])
        sales[collected_amount_col] = safe_numeric(sales[collected_amount_col])
        sales["Collection Gap"] = sales[expected_amount_col] - sales[collected_amount_col]

        collection_gaps = sales[sales["Collection Gap"] > 0]

        if not collection_gaps.empty:
            total_collection_gap = collection_gaps["Collection Gap"].sum()

            leakage_items.append(
                create_leakage_item(
                    "Revenue Collection Gap",
                    f"{len(collection_gaps)} records show expected amount higher than collected amount.",
                    total_collection_gap,
                    "Follow up outstanding balances, reconcile collections, and confirm customer payment status.",
                    "High",
                )
            )

            st.warning(f"Revenue collection gaps detected: ₦{total_collection_gap:,.0f}")
            st.dataframe(collection_gaps, use_container_width=True)

    discount_col = st.selectbox("Discount Column, if available", ["None"] + sales_columns, key="discount_col")

    if discount_col != "None":
        sales[discount_col] = safe_numeric(sales[discount_col])

        excessive_discounts = sales[sales[discount_col] > sales[discount_col].mean() * 2]

        if not excessive_discounts.empty:
            total_excess_discount = excessive_discounts[discount_col].sum()

            leakage_items.append(
                create_leakage_item(
                    "Possible Excessive Discounts",
                    f"{len(excessive_discounts)} sales records show discounts above normal pattern.",
                    total_excess_discount,
                    "Review discount approval limits, pricing policy, and customer-level discount exceptions.",
                    "Medium",
                )
            )

            st.info(f"Possible excessive discounts detected: ₦{total_excess_discount:,.0f}")
            st.dataframe(excessive_discounts, use_container_width=True)

# ==========================================================
# VENDOR LEAKAGE ANALYSIS
# ==========================================================
if vendor_df is not None:
    st.markdown("## 4. Vendor / Procurement Leakage Review")

    vendor = vendor_df.copy()
    vendor_columns = list(vendor.columns)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        vendor_name_col = st.selectbox("Vendor Name Column", ["None"] + vendor_columns, key="vendor_name_col")

    with col2:
        vendor_amount_col = st.selectbox("Vendor Amount Column", vendor_columns, key="vendor_amount_col")

    with col3:
        vendor_invoice_col = st.selectbox("Invoice Number Column, if available", ["None"] + vendor_columns, key="vendor_invoice_col")

    with col4:
        vendor_date_col = st.selectbox("Vendor Date Column", ["None"] + vendor_columns, key="vendor_date_col")

    vendor[vendor_amount_col] = safe_numeric(vendor[vendor_amount_col])

    duplicate_vendor_payments = detect_duplicates(
        vendor,
        amount_col=vendor_amount_col,
        date_col=vendor_date_col,
        vendor_col=vendor_name_col,
        desc_col=vendor_invoice_col,
    )

    if not duplicate_vendor_payments.empty:
        duplicate_vendor_value = duplicate_vendor_payments[vendor_amount_col].sum()

        leakage_items.append(
            create_leakage_item(
                "Possible Duplicate Vendor Payments",
                f"{len(duplicate_vendor_payments)} possible duplicate vendor payment records detected.",
                duplicate_vendor_value,
                "Review vendor invoices, payment approvals, and procurement records for duplication.",
                "High",
            )
        )

        st.warning(f"Possible duplicate vendor payments detected: {len(duplicate_vendor_payments)} records.")
        st.dataframe(duplicate_vendor_payments, use_container_width=True)

# ==========================================================
# INVENTORY LEAKAGE ANALYSIS
# ==========================================================
if inventory_df is not None:
    st.markdown("## 5. Inventory Leakage Review")

    inv = inventory_df.copy()
    inv_columns = list(inv.columns)

    col1, col2, col3 = st.columns(3)

    with col1:
        stock_expected_col = st.selectbox("Expected Stock Column", ["None"] + inv_columns, key="stock_expected_col")

    with col2:
        stock_actual_col = st.selectbox("Actual Stock Column", ["None"] + inv_columns, key="stock_actual_col")

    with col3:
        stock_value_col = st.selectbox("Unit Value / Cost Column", ["None"] + inv_columns, key="stock_value_col")

    if stock_expected_col != "None" and stock_actual_col != "None":
        inv[stock_expected_col] = safe_numeric(inv[stock_expected_col])
        inv[stock_actual_col] = safe_numeric(inv[stock_actual_col])

        inv["Stock Variance"] = inv[stock_expected_col] - inv[stock_actual_col]
        stock_losses = inv[inv["Stock Variance"] > 0].copy()

        if not stock_losses.empty:
            if stock_value_col != "None":
                stock_losses[stock_value_col] = safe_numeric(stock_losses[stock_value_col])
                stock_losses["Estimated Loss Value"] = stock_losses["Stock Variance"] * stock_losses[stock_value_col]
                estimated_stock_loss = stock_losses["Estimated Loss Value"].sum()
            else:
                estimated_stock_loss = stock_losses["Stock Variance"].sum()

            leakage_items.append(
                create_leakage_item(
                    "Possible Inventory Losses",
                    f"{len(stock_losses)} inventory records show expected stock higher than actual stock.",
                    estimated_stock_loss,
                    "Conduct stock reconciliation, review store controls, and investigate movement records.",
                    "High",
                )
            )

            st.warning(f"Possible inventory leakage detected: ₦{estimated_stock_loss:,.0f}")
            st.dataframe(stock_losses, use_container_width=True)

# ==========================================================
# LEAKAGE REGISTER
# ==========================================================
st.markdown("---")
st.markdown("## Leakage Register")

if leakage_items:
    leakage_df = pd.DataFrame(leakage_items)
else:
    leakage_df = pd.DataFrame(
        [
            {
                "Leakage Area": "No Major Leakage Automatically Detected",
                "Observation": "Current uploaded data did not produce major automated leakage red flags.",
                "Estimated Leakage Exposure": 0,
                "Recommended Action": "Conduct deeper document review, staff interviews, bank statement review, and process walkthrough.",
                "Priority": "Review",
            }
        ]
    )

st.dataframe(leakage_df, use_container_width=True)

total_leakage_exposure = leakage_df["Estimated Leakage Exposure"].sum()

st.session_state["leakage_df"] = leakage_df
st.session_state["total_leakage_exposure"] = total_leakage_exposure

st.error(f"Estimated Leakage Exposure Identified: ₦{total_leakage_exposure:,.0f}")

# ==========================================================
# SAVE ANALYSIS OUTPUT TO SUPABASE
# ==========================================================
st.markdown("## Save Leakage Analysis")

if st.button("Save Leakage Analysis to Supabase"):
    project = st.session_state.get("active_project")

    if not project:
        st.warning("No active project found. Please ensure Company Profile is saved first.")
    else:
        try:
            save_analysis_output(
                project_id=project.get("id"),
                analysis_type="leakage_detection",
                total_value=total_leakage_exposure,
                df=leakage_df,
            )
            st.success("Leakage analysis output saved successfully to Supabase.")
        except Exception as e:
            st.error(f"Could not save leakage analysis output to Supabase: {e}")

# ==========================================================
# AI-STYLE MANAGEMENT INSIGHTS
# ==========================================================
st.markdown("## AI-Style Management Insights")

insights = generate_leakage_insights(
    total_leakage_exposure=total_leakage_exposure,
    leakage_df=leakage_df,
)

for insight in insights:
    st.info(insight)

# ==========================================================
# AI PREMIUM LEAKAGE COMMENTARY
# ==========================================================
st.markdown("## AI Premium Leakage Commentary")

if st.button("Generate AI Leakage Commentary"):
    company_profile = st.session_state.get("company_profile", {})
    company_name = company_profile.get("company_name", "the company")

    with st.spinner("Generating AI-powered leakage commentary..."):
        ai_leakage_commentary = generate_ai_leakage_review(
            company_name=company_name,
            leakage_df=leakage_df,
            total_leakage_exposure=total_leakage_exposure,
        )

    st.session_state["ai_leakage_commentary"] = ai_leakage_commentary

if st.session_state.get("ai_leakage_commentary"):
    st.markdown("### Generated Leakage Commentary")
    st.markdown(st.session_state["ai_leakage_commentary"])

# ==========================================================
# NAVIGATION
# ==========================================================
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Back: Revenue Analysis"):
        st.switch_page("pages/03_Revenue_Analysis.py")

with col2:
    if st.button("Next: Cost Review"):
        st.switch_page("pages/05_Cost_Review.py")

with col3:
    if st.button("Go to Dashboard"):
        st.switch_page("pages/06_Opportunity_Dashboard.py")