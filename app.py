import streamlit as st

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="Chumcred ProfitIQ",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


col1, col2 = st.columns([1, 2])

with col1:
    st.image("assets/logo.png", width=200)


# ==========================================================
# AUTO REDIRECT LOGGED-IN USERS TO PLATFORM
# ==========================================================
if st.session_state.get("user") is not None:
    st.switch_page("pages/01_Company_Profile.py")

# ==========================================================
# HIDE STREAMLIT DEFAULT SIDEBAR + STYLE PAGE
# ==========================================================
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }

        [data-testid="collapsedControl"] {
            display: none;
        }

        .block-container {
            padding-top: 2rem;
            padding-left: 4rem;
            padding-right: 4rem;
            max-width: 100%;
        }

        .hero-section {
            background: linear-gradient(135deg, #0B1F3A 0%, #123C69 50%, #1D70A2 100%);
            padding: 4rem 3rem;
            border-radius: 24px;
            color: white;
            margin-bottom: 2rem;
        }

        .hero-title {
            font-size: 3.2rem;
            font-weight: 800;
            margin-bottom: 1rem;
            line-height: 1.1;
        }

        .hero-subtitle {
            font-size: 1.25rem;
            line-height: 1.7;
            max-width: 900px;
            opacity: 0.95;
        }

        .section-title {
            font-size: 2rem;
            font-weight: 800;
            color: #0B1F3A;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }

        .card {
            background: #FFFFFF;
            padding: 1.6rem;
            border-radius: 18px;
            border: 1px solid #E6EAF0;
            box-shadow: 0 8px 24px rgba(0,0,0,0.05);
            min-height: 210px;
        }

        .card h3 {
            color: #0B1F3A;
            font-size: 1.25rem;
            margin-bottom: 0.7rem;
        }

        .card p {
            color: #4A5568;
            font-size: 1rem;
            line-height: 1.6;
        }

        .metric-box {
            background: #F5F8FC;
            padding: 1.5rem;
            border-radius: 18px;
            border-left: 6px solid #1D70A2;
        }

        .metric-title {
            color: #4A5568;
            font-size: 0.95rem;
            margin-bottom: 0.3rem;
        }

        .metric-value {
            color: #0B1F3A;
            font-size: 1.7rem;
            font-weight: 800;
        }

        .process-box {
            background: #F9FBFD;
            padding: 1.4rem;
            border-radius: 16px;
            border: 1px solid #E6EAF0;
            min-height: 160px;
        }

        .process-number {
            background: #1D70A2;
            color: white;
            width: 38px;
            height: 38px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            margin-bottom: 0.8rem;
        }

        .login-box {
            background: #F5F8FC;
            padding: 2rem;
            border-radius: 22px;
            border: 1px solid #E6EAF0;
            margin-top: 2rem;
            text-align: center;
        }

        .footer {
            text-align: center;
            margin-top: 3rem;
            padding: 2rem;
            color: #5A6473;
            font-size: 0.95rem;
        }

        div.stButton > button {
            background-color: #1D70A2;
            color: white;
            border-radius: 12px;
            padding: 0.8rem 1.4rem;
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
# HERO SECTION
# ==========================================================
st.markdown(
    """
    <div class="hero-section">
        <div class="hero-title">Chumcred ProfitIQ</div>
        <div class="hero-subtitle">
            A Business Growth & Leakage Intelligence Platform designed to help companies
            identify hidden revenue opportunities, detect revenue leakages, reduce avoidable costs,
            and improve profitability through a structured 90-day business review framework.
        </div>
        <br>
        <div style="font-size:1.1rem; font-weight:700;">
            Unlock Hidden Revenue. Detect Leakages. Improve Profit.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==========================================================
# QUICK VALUE METRICS
# ==========================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        """
        <div class="metric-box">
            <div class="metric-title">Focus Area</div>
            <div class="metric-value">Revenue Growth</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="metric-box">
            <div class="metric-title">Focus Area</div>
            <div class="metric-value">Leakage Detection</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="metric-box">
            <div class="metric-title">Focus Area</div>
            <div class="metric-value">Cost Savings</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        """
        <div class="metric-box">
            <div class="metric-title">Review Cycle</div>
            <div class="metric-value">90 Days</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ==========================================================
# WHAT THE PLATFORM DOES
# ==========================================================
st.markdown('<div class="section-title">What ProfitIQ Helps Businesses Do</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="card">
            <h3>Identify Revenue Opportunities</h3>
            <p>
            Analyze products, branches, customers, channels, and sales trends to discover
            areas where the business can grow revenue and improve performance.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="card">
            <h3>Detect Revenue Leakages</h3>
            <p>
            Review transactions, collections, pricing, discounts, bank charges, and operational
            gaps to detect where money may be leaking from the business.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="card">
            <h3>Reduce Avoidable Costs</h3>
            <p>
            Examine expenses, vendors, logistics, payroll, utilities, and operating costs to
            identify practical cost-saving opportunities.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ==========================================================
# PLATFORM MODULES
# ==========================================================
st.markdown('<div class="section-title">Core Platform Modules</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

modules = [
    ("Company Profile", "Capture company structure, industry, branches, products, and review objectives."),
    ("Financial Upload", "Upload sales, expense, bank, branch, vendor, payroll, and operational data."),
    ("Revenue Analysis", "Analyze revenue trends, performance gaps, customer value, and growth opportunities."),
    ("Leakage Detection", "Identify duplicate payments, underbilling, high charges, losses, and collection gaps."),
    ("Cost Review", "Review cost categories, expense trends, vendor costs, and savings opportunities."),
    ("Opportunity Dashboard", "Show executive KPIs, profit improvement potential, risks, and quick wins."),
    ("Action Plan Tracker", "Track recommendations, owners, deadlines, status, and implementation impact."),
    ("Executive Report", "Generate professional reports for management, board, or client presentation."),
]

for index, (title, desc) in enumerate(modules):
    with [col1, col2, col3, col4][index % 4]:
        st.markdown(
            f"""
            <div class="card">
                <h3>{title}</h3>
                <p>{desc}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ==========================================================
# 90-DAY REVIEW PROCESS
# ==========================================================
st.markdown('<div class="section-title">90-Day Business Growth & Leakage Review Process</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

process_steps = [
    ("1", "Diagnostic Review", "Understand the business, collect data, review revenue lines, costs, and operational structure."),
    ("2", "Opportunity & Leakage Analysis", "Analyze revenue gaps, leakage points, cost drivers, and financial impact areas."),
    ("3", "Profit Improvement Roadmap", "Prioritize findings and create practical recommendations with expected impact."),
    ("4", "Implementation Tracking", "Track action owners, timelines, savings, recoveries, and final business impact."),
]

for col, (num, title, desc) in zip([col1, col2, col3, col4], process_steps):
    with col:
        st.markdown(
            f"""
            <div class="process-box">
                <div class="process-number">{num}</div>
                <h3 style="color:#0B1F3A;">{title}</h3>
                <p style="color:#4A5568; line-height:1.6;">{desc}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ==========================================================
# DELIVERABLES
# ==========================================================
st.markdown('<div class="section-title">Key Deliverables</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div class="card">
            <h3>Consulting Deliverables</h3>
            <p>
            • Business Diagnostic Report<br>
            • Revenue Opportunity Map<br>
            • Leakage Register<br>
            • Cost Savings Report<br>
            • 90-Day Profit Improvement Plan<br>
            • Final Management Report
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="card">
            <h3>Executive Dashboard Insights</h3>
            <p>
            • Total revenue opportunity identified<br>
            • Estimated leakage exposure<br>
            • Cost-saving potential<br>
            • Profit improvement potential<br>
            • Top priority actions<br>
            • Business risk indicators
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ==========================================================
# TARGET INDUSTRIES
# ==========================================================
st.markdown('<div class="section-title">Target Industries</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="card">
        <p>
        ProfitIQ can be adapted for manufacturing, retail and distribution, hotels, hospitals,
        schools, real estate, logistics, oil and gas service companies, government agencies,
        financial institutions, and telecom distribution networks.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==========================================================
# LOGIN / SIGNUP CALL TO ACTION
# ==========================================================
st.markdown(
    """
    <div class="login-box">
        <h2 style="color:#0B1F3A;">Ready to Start Your ProfitIQ Review?</h2>
        <p style="color:#4A5568; font-size:1rem;">
            Login if you already have an account, or create a new account to begin your business review.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("Login"):
        st.switch_page("pages/00_Login.py")

with col2:
    if st.button("Create Account"):
        st.switch_page("pages/00_Signup.py")

with col3:
    if st.button("Learn Platform Modules"):
        st.info("Scroll up to review the full platform modules and 90-day review process.")

# ==========================================================
# FOOTER
# ==========================================================
st.markdown(
    """
    <div class="footer">
        Chumcred ProfitIQ | Business Growth, Leakage Detection & Profit Improvement Intelligence
    </div>
    """,
    unsafe_allow_html=True,
)