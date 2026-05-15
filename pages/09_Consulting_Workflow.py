import streamlit as st
import pandas as pd
from modules.openai_ai import (
    generate_ai_diagnostic_summary,
    generate_ai_consulting_recommendations,
)

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="Consulting Workflow | Chumcred ProfitIQ",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# AUTH
# ==========================================================
from auth import require_login, show_user_bar

require_login()


# ==========================================================
# STYLING + SIDEBAR
# ==========================================================
from modules.styling import apply_global_style, custom_sidebar

apply_global_style()
custom_sidebar()

# ==========================================================
# WORKFLOW MODULE
# ==========================================================
from modules.consulting_workflow import (
    create_default_workflow,
    generate_workflow_summary,
    generate_workflow_insights,
)

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

        .workflow-card {
            background: #FFFFFF;
            padding: 1.5rem;
            border-radius: 18px;
            border: 1px solid #E6EAF0;
            box-shadow: 0 8px 24px rgba(0,0,0,0.04);
            margin-bottom: 1.5rem;
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
        <div class="page-title">Consulting Workflow</div>
        <div class="page-subtitle">
            Manage the end-to-end consulting engagement lifecycle from onboarding,
            analysis, management review, implementation tracking, and final reporting.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==========================================================
# INITIALIZE WORKFLOW
# ==========================================================
if "consulting_workflow_df" not in st.session_state:
    st.session_state["consulting_workflow_df"] = create_default_workflow()

workflow_df = st.session_state["consulting_workflow_df"]

# ==========================================================
# WORKFLOW SUMMARY
# ==========================================================
st.markdown("## Workflow Summary")

summary_df = generate_workflow_summary(workflow_df)

if not summary_df.empty:
    st.dataframe(summary_df, use_container_width=True)

# ==========================================================
# WORKFLOW EDITOR
# ==========================================================
st.markdown("## Engagement Workflow Tracker")

edited_df = st.data_editor(
    workflow_df,
    use_container_width=True,
    num_rows="dynamic",
    column_config={
        "Start Date": st.column_config.DateColumn(
            "Start Date"
        ),
        "Due Date": st.column_config.DateColumn(
            "Due Date"
        ),
        "Status": st.column_config.SelectboxColumn(
            "Status",
            options=[
                "Not Started",
                "In Progress",
                "Completed",
                "Delayed",
                "Cancelled",
            ],
        ),
    },
)

# ==========================================================
# SAVE WORKFLOW
# ==========================================================
if st.button("Save Workflow Updates"):
    st.session_state["consulting_workflow_df"] = edited_df
    st.success("Workflow updates saved successfully.")

# ==========================================================
# WORKFLOW INSIGHTS
# ==========================================================
st.markdown("## Workflow Insights")

workflow_insights = generate_workflow_insights(edited_df)

for insight in workflow_insights:
    st.info(insight)

# ==========================================================
# INITIALIZE AI SESSION STATE
# ==========================================================
if "ai_diagnostic_summary" not in st.session_state:
    st.session_state["ai_diagnostic_summary"] = ""

if "ai_consulting_recommendations" not in st.session_state:
    st.session_state["ai_consulting_recommendations"] = ""

# ==========================================================
# AI PREMIUM CONSULTING COMMENTARY
# ==========================================================
st.markdown("## AI Premium Consulting Commentary")

company_profile = st.session_state.get("company_profile", {})
company_name = company_profile.get("company_name", "the company")

col1, col2 = st.columns(2)

with col1:
    if st.button("Generate AI Diagnostic Summary"):
        with st.spinner("Generating AI-powered diagnostic summary..."):
            ai_diagnostic_summary = generate_ai_diagnostic_summary(
                company_name=company_name,
                diagnostic_df=edited_df,
                benchmark_df=st.session_state.get("benchmark_df"),
                forecast_df=st.session_state.get("profit_forecast_df"),
            )

        st.session_state["ai_diagnostic_summary"] = ai_diagnostic_summary

with col2:
    if st.button("Generate AI Consulting Recommendations"):
        with st.spinner("Generating AI-powered consulting recommendations..."):
            ai_consulting_recommendations = generate_ai_consulting_recommendations(
                company_name=company_name,
                revenue_opportunity_df=st.session_state.get("revenue_opportunity_df"),
                leakage_df=st.session_state.get("leakage_df"),
                cost_saving_df=st.session_state.get("cost_saving_df"),
            )

        st.session_state["ai_consulting_recommendations"] = ai_consulting_recommendations

# ==========================================================
# DISPLAY SAVED AI COMMENTARY
# ==========================================================
if st.session_state.get("ai_diagnostic_summary"):
    st.markdown("### AI Diagnostic Summary")
    st.markdown(st.session_state["ai_diagnostic_summary"])

if st.session_state.get("ai_consulting_recommendations"):
    st.markdown("### AI Consulting Recommendations")
    st.markdown(st.session_state["ai_consulting_recommendations"])

# ==========================================================
# EXECUTION GUIDANCE
# ==========================================================
st.markdown("## Consulting Execution Guidance")

guidance_items = [
    "Hold weekly project review meetings.",
    "Track blockers and delayed actions early.",
    "Validate all analysis findings with management.",
    "Assign clear owners to every action item.",
    "Track actual business impact weekly.",
    "Escalate unresolved issues promptly.",
    "Document all observations and management decisions.",
]

for item in guidance_items:
    st.write(f"✅ {item}")

# ==========================================================
# NAVIGATION
# ==========================================================
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Back: Executive Report"):
        st.switch_page("pages/08_Executive_Report.py")

with col2:
    if st.button("Go to Dashboard"):
        st.switch_page("pages/06_Opportunity_Dashboard.py")

with col3:
    if st.button("Back to Home"):
        st.switch_page("app.py")