import streamlit as st
import pandas as pd

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="Financial Upload | Chumcred ProfitIQ",
    page_icon="📤",
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
from modules.supabase_helpers import (
    get_or_create_active_project,
    save_uploaded_dataset,
    fetch_uploaded_datasets,
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
        <div class="page-title">Financial Upload</div>
        <div class="page-subtitle">
            Upload business documents and datasets required for business diagnostic review,
            revenue analysis, leakage detection, cost review, and executive dashboard reporting.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==========================================================
# SESSION STATE INIT
# ==========================================================
upload_keys = [
    "sales_data",
    "expense_data",
    "bank_statement_data",
    "bank_charges_data",
    "pnl_data",
    "branch_data",
    "vendor_data",
    "inventory_data",
    "payroll_data",
]

for key in upload_keys:
    if key not in st.session_state:
        st.session_state[key] = None

if "active_project" not in st.session_state:
    try:
        st.session_state["active_project"] = get_or_create_active_project()
    except Exception as e:
        st.session_state["active_project"] = None
        st.warning(f"Could not create or load active Supabase project: {e}")

# ==========================================================
# LOAD SAVED UPLOADED DATASETS FROM SUPABASE
# ==========================================================
def load_saved_datasets_from_supabase():
    project = st.session_state.get("active_project")

    if not project:
        return

    try:
        result = fetch_uploaded_datasets(project.get("id"))

        if result.data:
            latest_datasets = {}

            for item in result.data:
                dataset_type = item.get("dataset_type")
                data_json = item.get("data_json") or []

                if dataset_type in upload_keys and dataset_type not in latest_datasets:
                    latest_datasets[dataset_type] = data_json

            for dataset_type, data_json in latest_datasets.items():
                if st.session_state.get(dataset_type) is None:
                    st.session_state[dataset_type] = pd.DataFrame(data_json)

    except Exception as e:
        st.warning(f"Could not load saved uploaded datasets: {e}")


load_saved_datasets_from_supabase()

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================
def read_uploaded_file(uploaded_file):
    if uploaded_file is None:
        return None

    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)

            # Fix badly-read CSV where all values are trapped in one comma-separated column
            if len(df.columns) == 1 and "," in df.columns[0]:
                single_col = df.columns[0]
                df = df[single_col].astype(str).str.split(",", expand=True)
                df.columns = [col.strip() for col in single_col.split(",")]

            return df

        elif uploaded_file.name.endswith((".xlsx", ".xls")):
            return pd.read_excel(uploaded_file)

        else:
            st.warning("Unsupported file format. Please upload CSV or Excel files.")
            return None

    except Exception as e:
        st.error(f"Unable to read file: {e}")
        return None


def save_dataset_to_supabase(key_name, title, uploaded_file, df):
    project = st.session_state.get("active_project")

    if not project:
        st.info("Dataset saved locally for this session, but no active Supabase project was found.")
        return

    try:
        save_uploaded_dataset(
            project_id=project.get("id"),
            dataset_type=key_name,
            file_name=uploaded_file.name,
            df=df,
        )
        st.success(f"{title} saved to Supabase.")
    except Exception as e:
        st.warning(f"{title} uploaded locally, but Supabase save failed: {e}")


def show_dataset_preview(title, df):
    st.write("Preview:")
    st.dataframe(df.head(10), use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", len(df))
    col2.metric("Columns", len(df.columns))
    col3.metric("Missing Values", int(df.isna().sum().sum()))


def upload_section(title, description, key_name, required=False):
    st.markdown('<div class="upload-card">', unsafe_allow_html=True)

    required_label = "Required" if required else "Optional"
    st.markdown(f"### {title} ({required_label})")
    st.write(description)

    uploaded_file = st.file_uploader(
        f"Upload {title}",
        type=["csv", "xlsx", "xls"],
        key=f"{key_name}_uploader",
    )

    if uploaded_file is not None:
        df = read_uploaded_file(uploaded_file)

        if df is not None:
            st.session_state[key_name] = df
            st.success(f"{title} uploaded successfully.")
            save_dataset_to_supabase(key_name, title, uploaded_file, df)
            show_dataset_preview(title, df)

    elif st.session_state[key_name] is not None:
        st.info(f"{title} already available from saved data.")
        show_dataset_preview(title, st.session_state[key_name])

        if st.button(f"Clear {title}", key=f"clear_{key_name}"):
            clear_dataset(key_name)

    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================================
# CLEAR DATASET
# ==========================================================
def clear_dataset(key_name):
    st.session_state[key_name] = None

    uploader_key = f"{key_name}_uploader"
    if uploader_key in st.session_state:
        del st.session_state[uploader_key]

    st.success("Dataset cleared. You can now upload a new file.")
    st.rerun()

# ==========================================================
# CORE REQUIRED UPLOADS
# ==========================================================
st.markdown('<div class="section-title">1. Core Financial Data</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    upload_section(
        "Sales Data",
        "Upload revenue or sales transaction data. Recommended columns: Date, Branch, Product/Service, Customer, Quantity, Amount, Target, Expected Amount, Collected Amount, Discount.",
        "sales_data",
        required=True,
    )

with col2:
    upload_section(
        "Expense Data",
        "Upload business expense data. Recommended columns: Date, Expense Category, Department, Vendor, Description, Amount.",
        "expense_data",
        required=True,
    )

# ==========================================================
# FINANCIAL STATEMENT / BANK DATA
# ==========================================================
st.markdown('<div class="section-title">2. Financial Statements & Bank Data</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    upload_section(
        "Profit and Loss Statement",
        "Upload P&L data showing revenue, cost of sales, gross profit, operating expenses, finance cost, and net profit.",
        "pnl_data",
        required=False,
    )

with col2:
    upload_section(
        "Bank Statement Data",
        "Upload bank statement transaction data for deposits, withdrawals, charges, transfers, loan deductions, and unexplained debits.",
        "bank_statement_data",
        required=False,
    )

col1, col2 = st.columns(2)

with col1:
    upload_section(
        "Bank Charges Data",
        "Upload bank charges, interest charges, loan fees, COT, maintenance fees, and other bank-related deductions.",
        "bank_charges_data",
        required=False,
    )

with col2:
    upload_section(
        "Branch Performance Data",
        "Upload branch/location performance data including revenue, target, cost, staff count, and profitability.",
        "branch_data",
        required=False,
    )

# ==========================================================
# OPERATIONAL SUPPORTING DATA
# ==========================================================
st.markdown('<div class="section-title">3. Operational & Supporting Data</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    upload_section(
        "Vendor / Procurement Data",
        "Upload vendor payments, procurement records, supplier invoices, and purchase history.",
        "vendor_data",
        required=False,
    )

with col2:
    upload_section(
        "Inventory Data",
        "Upload inventory movement, stock balances, expected stock, actual stock, stock losses, purchases, and sales records.",
        "inventory_data",
        required=False,
    )

col1, col2 = st.columns(2)

with col1:
    upload_section(
        "Payroll / Staff Cost Data",
        "Upload payroll or staff cost data for productivity and cost review analysis.",
        "payroll_data",
        required=False,
    )

with col2:
    st.markdown('<div class="upload-card">', unsafe_allow_html=True)
    st.markdown("### Upload Guidance")
    st.write(
        """
        For best analysis, ensure your files contain clear column names such as:

        - Date
        - Branch
        - Product/Service
        - Customer
        - Revenue/Amount
        - Target
        - Expected Amount
        - Collected Amount
        - Expense Category
        - Vendor
        - Department
        - Description
        - Quantity
        - Cost
        - Bank
        - Charge Type

        Sales Data and Expense Data are the minimum recommended uploads for the MVP.
        """
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================================
# CLEAR ALL UPLOADED DATA
# ==========================================================
st.markdown("---")
st.markdown("## Manage Uploaded Data")

if st.button("Clear All Uploaded Data", key="clear_all_uploaded_data"):
    for key in upload_keys:
        st.session_state[key] = None

        uploader_key = f"{key}_uploader"
        if uploader_key in st.session_state:
            del st.session_state[uploader_key]

    st.success("All uploaded datasets cleared. You can now upload fresh files.")
    st.rerun()

# ==========================================================
# UPLOAD SUMMARY
# ==========================================================
st.markdown("---")
st.markdown("## Upload Summary")

summary_data = []
required_data_keys = ["sales_data", "expense_data"]

for label, key, required in [
    ("Sales Data", "sales_data", "Required"),
    ("Expense Data", "expense_data", "Required"),
    ("Profit and Loss Statement", "pnl_data", "Optional"),
    ("Bank Statement Data", "bank_statement_data", "Optional"),
    ("Bank Charges Data", "bank_charges_data", "Optional"),
    ("Branch Performance Data", "branch_data", "Optional"),
    ("Vendor / Procurement Data", "vendor_data", "Optional"),
    ("Inventory Data", "inventory_data", "Optional"),
    ("Payroll / Staff Cost Data", "payroll_data", "Optional"),
]:
    df = st.session_state.get(key)

    summary_data.append(
        {
            "Data Type": label,
            "Requirement": required,
            "Status": "Uploaded" if df is not None else "Pending",
            "Rows": len(df) if df is not None else 0,
            "Columns": len(df.columns) if df is not None else 0,
        }
    )

summary_df = pd.DataFrame(summary_data)
st.dataframe(summary_df, use_container_width=True)

uploaded_count = sum(1 for key in upload_keys if st.session_state.get(key) is not None)
required_uploaded_count = sum(
    1 for key in required_data_keys if st.session_state.get(key) is not None
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Data Areas", len(upload_keys))
col2.metric("Uploaded Data Areas", uploaded_count)
col3.metric("Required Uploaded", f"{required_uploaded_count}/{len(required_data_keys)}")
col4.metric("Pending Data Areas", len(upload_keys) - uploaded_count)

if required_uploaded_count < len(required_data_keys):
    st.warning("Please upload at least Sales Data and Expense Data for meaningful MVP analysis.")
elif uploaded_count < 4:
    st.info("Core data uploaded. You can continue, but adding bank, P&L, branch, vendor, inventory, or payroll data will improve analysis quality.")
else:
    st.success("Data upload is strong enough to begin a comprehensive business review.")

# ==========================================================
# DATA QUALITY CHECK
# ==========================================================
st.markdown("## Basic Data Quality Check")

quality_rows = []

for label, key in [
    ("Sales Data", "sales_data"),
    ("Expense Data", "expense_data"),
    ("Profit and Loss Statement", "pnl_data"),
    ("Bank Statement Data", "bank_statement_data"),
    ("Bank Charges Data", "bank_charges_data"),
    ("Branch Performance Data", "branch_data"),
    ("Vendor / Procurement Data", "vendor_data"),
    ("Inventory Data", "inventory_data"),
    ("Payroll / Staff Cost Data", "payroll_data"),
]:
    df = st.session_state.get(key)

    if df is not None:
        quality_rows.append(
            {
                "Data Type": label,
                "Rows": len(df),
                "Columns": len(df.columns),
                "Duplicate Rows": int(df.duplicated().sum()),
                "Missing Values": int(df.isna().sum().sum()),
            }
        )

if quality_rows:
    st.dataframe(pd.DataFrame(quality_rows), use_container_width=True)
else:
    st.info("Data quality checks will appear after files are uploaded.")

# ==========================================================
# NAVIGATION
# ==========================================================
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Back: Company Profile"):
        st.switch_page("pages/01_Company_Profile.py")

with col2:
    if st.button("Next: Revenue Analysis"):
        st.switch_page("pages/03_Revenue_Analysis.py")

with col3:
    if st.button("Go to Dashboard"):
        st.switch_page("pages/06_Opportunity_Dashboard.py")