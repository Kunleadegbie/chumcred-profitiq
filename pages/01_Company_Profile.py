import streamlit as st
from datetime import date, datetime
from supabase_config import get_supabase_client

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="Company Profile | Chumcred ProfitIQ",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# AUTH PROTECTION
# ==========================================================
from auth import require_login
from modules.styling import apply_global_style, custom_sidebar

require_login()

apply_global_style()
custom_sidebar()


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================
def get_valid_review_date(value):
    if isinstance(value, date):
        return value

    if isinstance(value, str):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except Exception:
            return date.today()

    return date.today()


def safe_select_index(options, saved_value, default_index=0):
    if saved_value in options:
        return options.index(saved_value)

    return default_index


def load_company_profile_from_supabase():
    supabase = get_supabase_client()

    user = st.session_state.get("user")
    user_profile = st.session_state.get("user_profile", {})

    if not user:
        return {}

    company_id = user_profile.get("company_id") or st.session_state.get("company_id")

    try:
        if company_id:
            result = (
                supabase.table("companies")
                .select("*")
                .eq("id", company_id)
                .limit(1)
                .execute()
            )
        else:
            result = (
                supabase.table("companies")
                .select("*")
                .eq("created_by", user.id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )

        if result.data and len(result.data) > 0:
            company = result.data[0]

            loaded_profile = {
                "company_name": company.get("company_name", ""),
                "industry": company.get("industry", ""),
                "location": company.get("location", ""),
                "review_date": company.get("created_at", str(date.today()))[:10],
                "contact_person": "",
                "contact_email": "",
                "contact_phone": "",
                "business_stage": "Established Business",
                "number_of_branches": company.get("number_of_branches", 1),
                "number_of_staff": company.get("number_of_staff", 10),
                "monthly_revenue_range": company.get("monthly_revenue_range", "Not Disclosed"),
                "products_services": company.get("major_products_services", ""),
                "major_revenue_channels": [],
                "key_challenges": company.get("key_challenges", "").split(", ") if company.get("key_challenges") else [],
                "review_objective": company.get("review_objective", ""),
                "expected_outcome": "",
            }

            st.session_state["company_id"] = company.get("id")

            if "user_profile" not in st.session_state or st.session_state["user_profile"] is None:
                st.session_state["user_profile"] = {}

            st.session_state["user_profile"]["company_id"] = company.get("id")
            st.session_state["user_profile"]["company_name"] = company.get("company_name", "")

            return loaded_profile

    except Exception as e:
        st.warning(f"Could not load saved company profile: {e}")

    return {}


def save_company_profile_to_supabase(profile_data):
    supabase = get_supabase_client()

    user = st.session_state.get("user")
    user_profile = st.session_state.get("user_profile", {})

    if not user:
        st.error("User not found. Please login again.")
        return None

    company_payload = {
        "company_name": profile_data.get("company_name"),
        "industry": profile_data.get("industry"),
        "location": profile_data.get("location"),
        "number_of_branches": int(profile_data.get("number_of_branches", 1)),
        "number_of_staff": int(profile_data.get("number_of_staff", 1)),
        "monthly_revenue_range": profile_data.get("monthly_revenue_range"),
        "major_products_services": profile_data.get("products_services"),
        "key_challenges": ", ".join(profile_data.get("key_challenges", [])),
        "review_objective": profile_data.get("review_objective"),
        "created_by": user.id,
    }

    existing_company_id = user_profile.get("company_id") or st.session_state.get("company_id")

    if existing_company_id:
        result = (
            supabase.table("companies")
            .update(company_payload)
            .eq("id", existing_company_id)
            .execute()
        )
        company_id = existing_company_id

    else:
        result = supabase.table("companies").insert(company_payload).execute()

        if result.data:
            company_id = result.data[0]["id"]
        else:
            company_id = None

    if company_id:
        supabase.table("user_profiles").update(
            {
                "company_id": company_id,
                "company_name": profile_data.get("company_name"),
            }
        ).eq("id", user.id).execute()

        st.session_state["company_id"] = company_id

        if "user_profile" not in st.session_state or st.session_state["user_profile"] is None:
            st.session_state["user_profile"] = {}

        st.session_state["user_profile"]["company_id"] = company_id
        st.session_state["user_profile"]["company_name"] = profile_data.get("company_name")

    return company_id


# ==========================================================
# LOAD SAVED COMPANY PROFILE
# ==========================================================
if "company_profile" not in st.session_state or not st.session_state.company_profile:
    st.session_state.company_profile = load_company_profile_from_supabase()


# ==========================================================
# PAGE-SPECIFIC STYLING
# ==========================================================
st.markdown(
    """
    <style>
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
        <div class="page-title">Company Profile</div>
        <div class="page-subtitle">
            Capture the basic business information required to understand the company structure,
            operating model, revenue lines, cost areas, and review objectives before analysis begins.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==========================================================
# FORM OPTIONS
# ==========================================================
industry_options = [
    "Manufacturing",
    "Retail & Distribution",
    "Hospitality",
    "Healthcare",
    "Education",
    "Real Estate",
    "Logistics",
    "Oil & Gas Services",
    "Telecom/Dealer Network",
    "Financial Services",
    "Government/Parastatal",
    "Other",
]

business_stage_options = [
    "Startup",
    "Growing Business",
    "Established Business",
    "Large Enterprise",
    "Turnaround/Recovery Stage",
]

monthly_revenue_options = [
    "Below ₦10m",
    "₦10m - ₦50m",
    "₦50m - ₦100m",
    "₦100m - ₦500m",
    "₦500m - ₦1bn",
    "Above ₦1bn",
    "Not Disclosed",
]

revenue_channel_options = [
    "Direct Sales",
    "Distributors/Dealers",
    "Online Sales",
    "Corporate Clients",
    "Government Contracts",
    "Retail Outlets",
    "Subscription/Recurring Revenue",
    "Project-Based Revenue",
    "Other",
]

challenge_options = [
    "Revenue Decline",
    "Low Profit Margin",
    "High Operating Cost",
    "Revenue Leakage",
    "Poor Sales Performance",
    "Inventory Losses",
    "High Bank Charges",
    "Poor Collections",
    "Branch Underperformance",
    "Vendor/Supplier Cost Issues",
    "Weak Reporting Visibility",
    "Other",
]

profile = st.session_state.company_profile

# ==========================================================
# FORM
# ==========================================================
with st.form("company_profile_form"):
    st.markdown('<div class="section-title">1. Basic Company Information</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        company_name = st.text_input(
            "Company Name",
            value=profile.get("company_name", ""),
            placeholder="e.g. ABC Manufacturing Limited",
        )

        industry = st.selectbox(
            "Industry",
            industry_options,
            index=safe_select_index(industry_options, profile.get("industry"), 0),
        )

        location = st.text_input(
            "Head Office Location",
            value=profile.get("location", ""),
            placeholder="e.g. Lagos, Nigeria",
        )

        review_date = st.date_input(
            "Review Start Date",
            value=get_valid_review_date(profile.get("review_date", date.today())),
        )

    with col2:
        contact_person = st.text_input(
            "Contact Person",
            value=profile.get("contact_person", ""),
            placeholder="e.g. Managing Director / Finance Manager",
        )

        contact_email = st.text_input(
            "Contact Email",
            value=profile.get("contact_email", ""),
            placeholder="e.g. name@company.com",
        )

        contact_phone = st.text_input(
            "Contact Phone",
            value=profile.get("contact_phone", ""),
            placeholder="e.g. +234...",
        )

        business_stage = st.selectbox(
            "Business Stage",
            business_stage_options,
            index=safe_select_index(business_stage_options, profile.get("business_stage"), 2),
        )

    st.markdown("---")
    st.markdown('<div class="section-title">2. Business Structure</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        number_of_branches = st.number_input(
            "Number of Branches/Locations",
            min_value=1,
            value=int(profile.get("number_of_branches", 1) or 1),
            step=1,
        )

    with col2:
        number_of_staff = st.number_input(
            "Number of Staff",
            min_value=1,
            value=int(profile.get("number_of_staff", 10) or 10),
            step=1,
        )

    with col3:
        monthly_revenue_range = st.selectbox(
            "Average Monthly Revenue Range",
            monthly_revenue_options,
            index=safe_select_index(monthly_revenue_options, profile.get("monthly_revenue_range"), 6),
        )

    products_services = st.text_area(
        "Major Products / Services",
        value=profile.get("products_services", ""),
        placeholder="List the company’s major products or services.",
        height=120,
    )

    major_revenue_channels = st.multiselect(
        "Major Revenue Channels",
        revenue_channel_options,
        default=[
            item for item in profile.get("major_revenue_channels", [])
            if item in revenue_channel_options
        ],
    )

    st.markdown("---")
    st.markdown('<div class="section-title">3. Business Challenges & Review Objective</div>', unsafe_allow_html=True)

    key_challenges = st.multiselect(
        "Current Business Challenges",
        challenge_options,
        default=[
            item for item in profile.get("key_challenges", [])
            if item in challenge_options
        ],
    )

    review_objective = st.text_area(
        "Review Objective",
        value=profile.get("review_objective", ""),
        placeholder="Example: To identify revenue growth opportunities, detect leakages, reduce costs, and improve profitability within 90 days.",
        height=120,
    )

    expected_outcome = st.text_area(
        "Expected Outcome from the Review",
        value=profile.get("expected_outcome", ""),
        placeholder="Example: Improved revenue visibility, reduced leakages, clear action plan, and measurable profit improvement.",
        height=100,
    )

    submitted = st.form_submit_button("Save Company Profile")


# ==========================================================
# REVIEW PERIOD CONFIGURATION
# ==========================================================
st.markdown("## Review Period Configuration")

# ----------------------------------------------------------
# REVIEW OPTIONS
# ----------------------------------------------------------
review_type_options = [
    "Single Period Review",
    "Multi-Year Trend Review",
]

reporting_frequency_options = [
    "Monthly",
    "Quarterly",
    "Yearly",
]

# ----------------------------------------------------------
# USE EXISTING PROFILE VARIABLE
# ----------------------------------------------------------
profile = st.session_state.get("company_profile", {})

# ----------------------------------------------------------
# DEFAULT VALUES
# ----------------------------------------------------------
saved_review_type = profile.get("review_type", "Single Period Review")
saved_reporting_frequency = profile.get("reporting_frequency", "Monthly")

saved_review_start_date = get_valid_review_date(
    profile.get(
        "review_start_date",
        date.today().replace(year=date.today().year - 1),
    )
)

saved_review_end_date = get_valid_review_date(
    profile.get(
        "review_end_date",
        date.today(),
    )
)


# ----------------------------------------------------------
# REVIEW SETTINGS
# ----------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    review_type = st.selectbox(
        "Review Type",
        review_type_options,
        index=review_type_options.index(saved_review_type)
        if saved_review_type in review_type_options
        else 0,
    )

with col2:
    reporting_frequency = st.selectbox(
        "Reporting Frequency",
        reporting_frequency_options,
        index=reporting_frequency_options.index(saved_reporting_frequency)
        if saved_reporting_frequency in reporting_frequency_options
        else 0,
    )

# ----------------------------------------------------------
# DATE RANGE
# ----------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    review_start_date = st.date_input(
        "Review Start Date",
        value=saved_review_start_date,
    )

with col2:
    review_end_date = st.date_input(
        "Review End Date",
        value=saved_review_end_date,
    )

# ----------------------------------------------------------
# SAVE TO COMPANY PROFILE
# ----------------------------------------------------------
profile["review_type"] = review_type
profile["reporting_frequency"] = reporting_frequency
profile["review_start_date"] = str(review_start_date)
profile["review_end_date"] = str(review_end_date)

# ----------------------------------------------------------
# REVIEW SUMMARY
# ----------------------------------------------------------
st.info(
    f"""
Review Type: {review_type}

Reporting Frequency: {reporting_frequency}

Review Period:
{review_start_date} → {review_end_date}
"""
)


# ==========================================================
# SAVE PROFILE
# ==========================================================
if submitted:
    profile_data = {
        "company_name": company_name,
        "industry": industry,
        "location": location,
        "review_date": str(review_date),
        "contact_person": contact_person,
        "contact_email": contact_email,
        "contact_phone": contact_phone,
        "business_stage": business_stage,
        "number_of_branches": number_of_branches,
        "number_of_staff": number_of_staff,
        "monthly_revenue_range": monthly_revenue_range,
        "products_services": products_services,
        "major_revenue_channels": major_revenue_channels,
        "key_challenges": key_challenges,
        "review_objective": review_objective,
        "expected_outcome": expected_outcome,
        "review_type": review_type,
        "reporting_frequency": reporting_frequency,
        "review_start_date": str(review_start_date),
        "review_end_date": str(review_end_date),
    }

    st.session_state.company_profile = profile_data

    try:
        company_id = save_company_profile_to_supabase(profile_data)

        if company_id:
            st.session_state["company_id"] = company_id
            st.success("Company profile saved successfully to Supabase.")
        else:
            st.warning("Company profile saved locally, but Supabase save was not completed.")

    except Exception as e:
        st.error(f"Company profile saved locally, but Supabase save failed: {e}")

# ==========================================================
# PROFILE SUMMARY
# ==========================================================
if st.session_state.company_profile:
    profile = st.session_state.company_profile

    st.markdown("## Company Profile Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Company", profile.get("company_name", "Not provided"))
        st.metric("Industry", profile.get("industry", "Not provided"))

    with col2:
        st.metric("Branches", profile.get("number_of_branches", 0))
        st.metric("Staff Strength", profile.get("number_of_staff", 0))

    with col3:
        st.metric("Monthly Revenue Range", profile.get("monthly_revenue_range", "Not disclosed"))
        st.metric("Business Stage", profile.get("business_stage", "Not provided"))

    st.markdown("### Review Objective")
    st.info(profile.get("review_objective", "No review objective provided."))

# ==========================================================
# NAVIGATION
# ==========================================================
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Back to Home"):
        st.switch_page("app.py")

with col2:
    if st.button("Next: Financial Upload"):
        st.switch_page("pages/02_Financial_Upload.py")

with col3:
    if st.button("Go to Dashboard"):
        st.switch_page("pages/06_Opportunity_Dashboard.py")