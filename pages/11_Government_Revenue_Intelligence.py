import streamlit as st
import pandas as pd
import plotly.express as px

from auth import require_login
from modules.styling import apply_global_style, custom_sidebar
from modules.sector_labels import get_current_sector_labels

try:
    from modules.openai_ai import generate_ai_revenue_analysis
except Exception:
    generate_ai_revenue_analysis = None


# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="Government Revenue Intelligence | Chumcred ProfitIQ",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# AUTH + STYLE
# ==========================================================
require_login()
apply_global_style()
custom_sidebar()

# ==========================================================
# PAGE STYLING
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
        <div class="page-title">Government Revenue Intelligence</div>
        <div class="page-subtitle">
            Analyze IGR performance, MDA/LGA contribution, revenue streams, collection channels,
            leakage signals, and executive revenue improvement opportunities.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==========================================================
# HELPERS
# ==========================================================
def safe_numeric(series):
    cleaned = (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("₦", "", regex=False)
        .str.replace("NGN", "", regex=False)
        .str.strip()
    )

    return pd.to_numeric(cleaned, errors="coerce").fillna(0)

def get_numeric_like_columns(df):
    numeric_cols = []

    if df is None or df.empty:
        return numeric_cols

    for col in df.columns:
        col_name = str(col).lower().strip()

        if col_name in ["date", "month", "year", "period"]:
            continue

        cleaned = (
            df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("₦", "", regex=False)
            .str.replace("NGN", "", regex=False)
            .str.strip()
        )

        converted = pd.to_numeric(cleaned, errors="coerce")

        if converted.notna().sum() >= max(1, len(df) * 0.30):
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


def fix_bad_csv_dataframe(df):
    if df is None or df.empty:
        return df

    if len(df.columns) == 1 and "," in str(df.columns[0]):
        single_col = df.columns[0]
        fixed_df = df[single_col].astype(str).str.split(",", expand=True)
        fixed_df.columns = [col.strip() for col in str(single_col).split(",")]
        return fixed_df

    return df


# ==========================================================
# SESSION DATA
# ==========================================================
profile = st.session_state.get("company_profile", {})
engagement_type = profile.get("engagement_type", "Private Sector")

sector_labels = get_current_sector_labels()

sales_df = st.session_state.get("sales_data")
sales_df = fix_bad_csv_dataframe(sales_df)

if sales_df is not None:
    st.session_state["sales_data"] = sales_df

if engagement_type != "Government":
    st.info(
        "This page is designed for Government engagements. "
        "To activate government labels, go to Company Profile and set Engagement Type to Government."
    )

if sales_df is None or sales_df.empty:
    st.warning("No revenue collection data uploaded yet. Please upload Sales / Revenue Collection Data first.")

    if st.button("Go to Financial Upload"):
        st.switch_page("pages/02_Financial_Upload.py")

    st.stop()

# ==========================================================
# COLUMN MAPPING
# ==========================================================
st.markdown("## Revenue Collection Data Mapping")

columns = list(sales_df.columns)
numeric_columns = get_numeric_like_columns(sales_df)
date_columns = get_date_like_columns(sales_df)

def find_default_column(columns, preferred_names):
    for preferred in preferred_names:
        for col in columns:
            if preferred.lower() == str(col).lower().strip():
                return col

    for preferred in preferred_names:
        for col in columns:
            if preferred.lower() in str(col).lower():
                return col

    return columns[0] if columns else None


default_amount_col = find_default_column(
    numeric_columns,
    ["Amount", "Actual Revenue", "Remitted Amount", "Credit", "Revenue Target"]
)

col1, col2 = st.columns(2)

with col1:
    date_col = st.selectbox(
        "Collection Date Column",
        date_columns if date_columns else columns,
        key="gov_revenue_date_col",
    )

with col2:
    amount_col = st.selectbox(
        "IGR / Revenue Amount Column",
        numeric_columns if numeric_columns else columns,
        key="gov_revenue_amount_col",
    )

col1, col2, col3 = st.columns(3)

with col1:
    mda_lga_col = st.selectbox(
        "MDA / LGA Column",
        ["None"] + columns,
        key="gov_mda_lga_col",
    )

with col2:
    revenue_stream_col = st.selectbox(
        "Revenue Stream Column",
        ["None"] + columns,
        key="gov_revenue_stream_col",
    )

with col3:
    collection_channel_col = st.selectbox(
        "Collection Channel Column",
        ["None"] + columns,
        key="gov_collection_channel_col",
    )

data = sales_df.copy()

data[amount_col] = safe_numeric(data[amount_col])

if date_col != "None" and date_col in data.columns:
    data[date_col] = pd.to_datetime(data[date_col], errors="coerce")

# ==========================================================
# GOVERNMENT REVENUE KPIs
# ==========================================================
st.markdown("## Government Revenue Summary")

# ==========================================================
# FORCE SELECTED AMOUNT COLUMN TO NUMERIC
# ==========================================================
data[amount_col] = (
    data[amount_col]
    .astype(str)
    .str.replace(",", "", regex=False)
    .str.replace("₦", "", regex=False)
    .str.replace("NGN", "", regex=False)
    .str.strip()
)

data[amount_col] = pd.to_numeric(
    data[amount_col],
    errors="coerce"
).fillna(0)

total_igr = data[amount_col].sum()
average_collection = data[amount_col].mean()
transaction_count = len(data)
highest_collection = data[amount_col].max()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total IGR / Revenue Reviewed", f"₦{total_igr:,.0f}")
col2.metric("Average Collection Value", f"₦{average_collection:,.0f}")
col3.metric("Collection Records", f"{transaction_count:,.0f}")
col4.metric("Highest Collection", f"₦{highest_collection:,.0f}")

# ==========================================================
# MONTHLY IGR TREND
# ==========================================================
if date_col in data.columns:
    trend_data = data.dropna(subset=[date_col]).copy()

    if not trend_data.empty:
        trend_data["Month"] = trend_data[date_col].dt.to_period("M").astype(str)

        monthly_igr = (
            trend_data.groupby("Month", as_index=False)[amount_col]
            .sum()
            .sort_values("Month")
        )

        st.markdown("## Monthly IGR Trend")
        st.dataframe(monthly_igr, use_container_width=True)

        fig = px.line(
            monthly_igr,
            x="Month",
            y=amount_col,
            markers=True,
            title="Monthly IGR / Government Revenue Trend",
        )
        st.plotly_chart(fig, use_container_width=True)

        st.session_state["government_monthly_igr_df"] = monthly_igr

# ==========================================================
# MDA / LGA PERFORMANCE
# ==========================================================
if mda_lga_col != "None":
    st.markdown("## MDA / LGA Revenue Performance")

    mda_lga_performance = (
        data.groupby(mda_lga_col, as_index=False)[amount_col]
        .sum()
        .sort_values(amount_col, ascending=False)
    )

    total = mda_lga_performance[amount_col].sum()
    mda_lga_performance["Revenue Share %"] = mda_lga_performance[amount_col].apply(
        lambda x: (x / total * 100) if total > 0 else 0
    )

    st.dataframe(mda_lga_performance, use_container_width=True)

    fig = px.bar(
        mda_lga_performance,
        x=mda_lga_col,
        y=amount_col,
        title="MDA / LGA Revenue Ranking",
        text_auto=True,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.session_state["government_mda_lga_performance_df"] = mda_lga_performance

# ==========================================================
# REVENUE STREAM PERFORMANCE
# ==========================================================
if revenue_stream_col != "None":
    st.markdown("## Revenue Stream Performance")

    revenue_stream_performance = (
        data.groupby(revenue_stream_col, as_index=False)[amount_col]
        .sum()
        .sort_values(amount_col, ascending=False)
    )

    total = revenue_stream_performance[amount_col].sum()
    revenue_stream_performance["Revenue Share %"] = revenue_stream_performance[amount_col].apply(
        lambda x: (x / total * 100) if total > 0 else 0
    )

    st.dataframe(revenue_stream_performance, use_container_width=True)

    fig = px.bar(
        revenue_stream_performance,
        x=revenue_stream_col,
        y=amount_col,
        title="Revenue Stream Performance",
        text_auto=True,
    )
    st.plotly_chart(fig, use_container_width=True)

    fig = px.pie(
        revenue_stream_performance,
        names=revenue_stream_col,
        values=amount_col,
        title="Revenue Stream Share",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.session_state["government_revenue_stream_performance_df"] = revenue_stream_performance

# ==========================================================
# COLLECTION CHANNEL ANALYSIS
# ==========================================================
if collection_channel_col != "None":
    st.markdown("## Collection Channel Analysis")

    channel_performance = (
        data.groupby(collection_channel_col, as_index=False)[amount_col]
        .sum()
        .sort_values(amount_col, ascending=False)
    )

    st.dataframe(channel_performance, use_container_width=True)

    fig = px.bar(
        channel_performance,
        x=collection_channel_col,
        y=amount_col,
        title="Revenue by Collection Channel",
        text_auto=True,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.session_state["government_collection_channel_df"] = channel_performance

# ==========================================================
# GOVERNMENT REVENUE OPPORTUNITY FLAGS
# ==========================================================
st.markdown("## Revenue Opportunity & Control Flags")

flags = []

if mda_lga_col != "None":
    avg_mda_revenue = mda_lga_performance[amount_col].mean()
    low_performing_units = mda_lga_performance[mda_lga_performance[amount_col] < avg_mda_revenue * 0.5]

    if not low_performing_units.empty:
        flags.append(
            {
                "Area": "Low Performing MDA / LGA",
                "Observation": f"{len(low_performing_units)} MDAs/LGAs are performing below 50% of average revenue contribution.",
                "Recommended Action": "Review collection processes, enforcement, taxpayer coverage, remittance discipline, and revenue officer accountability.",
                "Priority": "High",
            }
        )

if revenue_stream_col != "None":
    top_stream_share = revenue_stream_performance["Revenue Share %"].max()

    if top_stream_share >= 40:
        flags.append(
            {
                "Area": "Revenue Concentration Risk",
                "Observation": f"One revenue stream contributes {top_stream_share:.1f}% of total reviewed revenue.",
                "Recommended Action": "Diversify revenue improvement efforts and strengthen underperforming revenue streams.",
                "Priority": "Medium",
            }
        )

if collection_channel_col != "None":
    top_channel_value = channel_performance[amount_col].max()
    top_channel_share = (top_channel_value / total_igr * 100) if total_igr > 0 else 0

    if top_channel_share >= 60:
        flags.append(
            {
                "Area": "Collection Channel Concentration",
                "Observation": f"One collection channel accounts for {top_channel_share:.1f}% of total revenue.",
                "Recommended Action": "Review channel dependency, reconciliation controls, settlement timelines, and possible remittance risks.",
                "Priority": "Medium",
            }
        )

if not flags:
    flags.append(
        {
            "Area": "General Revenue Review",
            "Observation": "No major automated government revenue red flag was detected from the selected fields.",
            "Recommended Action": "Conduct deeper review of MDA/LGA performance, bank statements, remittances, and revenue stream compliance.",
            "Priority": "Review",
        }
    )

flags_df = pd.DataFrame(flags)
st.dataframe(flags_df, use_container_width=True)

st.session_state["government_revenue_flags_df"] = flags_df

# ==========================================================
# AI GOVERNMENT COMMENTARY
# ==========================================================
if "ai_government_revenue_commentary" not in st.session_state:
    st.session_state["ai_government_revenue_commentary"] = ""

st.markdown("## AI Government Revenue Commentary")

if st.button("Generate AI Government Revenue Commentary"):
    company_name = profile.get("company_name", "the government institution")

    revenue_summary = {
        "total_igr": total_igr,
        "average_collection": average_collection,
        "transaction_count": transaction_count,
        "highest_collection": highest_collection,
    }

    with st.spinner("Generating AI government revenue commentary..."):
        if generate_ai_revenue_analysis is None:
            ai_response = "OpenAI module is not available. Please confirm modules/openai_ai.py exists."
        else:
            ai_response = generate_ai_revenue_analysis(
                company_name=company_name,
                revenue_summary=revenue_summary,
                monthly_revenue_df=st.session_state.get("government_monthly_igr_df"),
                product_revenue_df=st.session_state.get("government_revenue_stream_performance_df"),
                branch_revenue_df=st.session_state.get("government_mda_lga_performance_df"),
                customer_revenue_df=st.session_state.get("government_collection_channel_df"),
                revenue_opportunity_df=flags_df,
            )

    st.session_state["ai_government_revenue_commentary"] = ai_response

if st.session_state.get("ai_government_revenue_commentary"):
    st.markdown("### Generated Government Revenue Commentary")
    st.markdown(st.session_state["ai_government_revenue_commentary"])

# ==========================================================
# NAVIGATION
# ==========================================================
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Back: Financial Upload"):
        st.switch_page("pages/02_Financial_Upload.py")

with col2:
    if st.button("Go to Opportunity Dashboard"):
        st.switch_page("pages/06_Opportunity_Dashboard.py")

with col3:
    if st.button("Go to Executive Report"):
        st.switch_page("pages/08_Executive_Report.py")