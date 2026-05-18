import streamlit as st
from PIL import Image


def apply_global_style():
    st.markdown(
        """
        <style>
            /* Hide Streamlit default multipage navigation only */
            [data-testid="stSidebarNav"] {
                display: none;
            }

            .block-container {
                padding-top: 2rem;
                padding-left: 3rem;
                padding-right: 3rem;
                max-width: 100%;
            }

            .page-header {
                background: linear-gradient(135deg, #0B1F3A 0%, #123C69 55%, #1D70A2 100%);
                padding: 2.5rem;
                border-radius: 22px;
                color: white;
                margin-bottom: 2rem;
            }

            .page-title {
                font-size: 2.5rem;
                font-weight: 800;
                margin-bottom: 0.5rem;
            }

            .page-subtitle {
                font-size: 1.1rem;
                line-height: 1.6;
                max-width: 950px;
                opacity: 0.95;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def custom_sidebar():
    with st.sidebar:
        # ==========================================================
        # LOGO
        # ==========================================================
        try:
            logo = Image.open("assets/logo.png")
            st.sidebar.image(logo, use_container_width=True)
        except:
            pass

        st.markdown("## Chumcred ProfitIQ")
        st.caption("Unlock Hidden Revenue. Detect Leakages. Improve Profit.")

        st.page_link("app.py", label="🏠 Home")
        st.page_link("pages/01_Company_Profile.py", label="🏢 Company Profile")
        st.page_link("pages/02_Financial_Upload.py", label="📤 Financial Upload")
        st.page_link("pages/03_Revenue_Analysis.py", label="📈 Revenue Analysis")
        st.page_link("pages/04_Leakage_Detection.py", label="🚨 Leakage Detection")
        st.page_link("pages/05_Cost_Review.py", label="💰 Cost Review")
        st.page_link("pages/06_Opportunity_Dashboard.py", label="📊 Opportunity Dashboard")
        st.page_link("pages/07_Action_Plan_Tracker.py", label="✅ Action Plan Tracker")
        st.page_link("pages/08_Executive_Report.py", label="📑 Executive Report")
        st.page_link("pages/09_Consulting_Workflow.py", label="🧭 Consulting Workflow")
        st.page_link("pages/10_AI_Assistant.py", label="🤖 AI Assistant")

        # ==========================================================
        # GOVERNMENT REVENUE INTELLIGENCE
        # ==========================================================
        profile = st.session_state.get("company_profile", {})
        engagement_type = profile.get("engagement_type", "Private Sector")

        if engagement_type == "Government":
            st.page_link(
                "pages/11_Government_Revenue_Intelligence.py",
                label="Government Revenue Intelligence",
                icon="🏛️",
            )

        # ==========================================================
        # LOGOUT BUTTON
        # ==========================================================
        st.markdown("<br><br><br>", unsafe_allow_html=True)

        if st.button("🚪 Logout", key="sidebar_logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]

            st.switch_page("pages/00_Login.py")


def page_header(title, subtitle):
    st.markdown(
        f"""
        <div class="page-header">
            <div class="page-title">{title}</div>
            <div class="page-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )