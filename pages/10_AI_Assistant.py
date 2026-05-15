import streamlit as st
import pandas as pd

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="AI Assistant | Chumcred ProfitIQ",
    page_icon="🤖",
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
# OPENAI AI MODULE
# ==========================================================
from modules.openai_ai import answer_business_question

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
        <div class="page-title">ProfitIQ AI Assistant</div>
        <div class="page-subtitle">
            Ask intelligent questions about uploaded business data, revenue opportunities,
            leakages, cost savings, benchmarks, forecasts, heatmaps, and action plans.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==========================================================
# HELPER
# ==========================================================
def df_to_records(df, max_rows=30):
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return []

    return df.head(max_rows).to_dict(orient="records")


# ==========================================================
# BUILD CONTEXT
# ==========================================================
profile = st.session_state.get("company_profile", {})
user_profile = st.session_state.get("user_profile", {})

context_data = {
    "company_profile": profile,
    "user_profile": {
        "company_name": user_profile.get("company_name"),
        "role": user_profile.get("role"),
    },
    "summary_metrics": {
        "total_revenue_opportunity": st.session_state.get("total_revenue_opportunity", 0),
        "total_leakage_exposure": st.session_state.get("total_leakage_exposure", 0),
        "total_cost_saving": st.session_state.get("total_cost_saving", 0),
    },
    "revenue_opportunity_map": df_to_records(st.session_state.get("revenue_opportunity_df")),
    "leakage_register": df_to_records(st.session_state.get("leakage_df")),
    "cost_savings_report": df_to_records(st.session_state.get("cost_saving_df")),
    "priority_actions": df_to_records(st.session_state.get("priority_action_df")),
    "action_plan": df_to_records(st.session_state.get("action_plan_df")),
    "benchmarking": df_to_records(st.session_state.get("benchmark_df")),
    "risk_heatmap": df_to_records(st.session_state.get("risk_heatmap_df")),
    "branch_risk_heatmap": df_to_records(st.session_state.get("branch_risk_heatmap_df")),
    "cost_concentration_heatmap": df_to_records(st.session_state.get("cost_concentration_heatmap_df")),
    "leakage_risk_matrix": df_to_records(st.session_state.get("leakage_risk_matrix_df")),
    "profitability_heatmap": df_to_records(st.session_state.get("profitability_heatmap_df")),
    "revenue_forecast": df_to_records(st.session_state.get("revenue_forecast_df")),
    "cost_forecast": df_to_records(st.session_state.get("cost_forecast_df")),
    "profit_forecast": df_to_records(st.session_state.get("profit_forecast_df")),
    "consulting_workflow": df_to_records(st.session_state.get("consulting_workflow_df")),
}

# ==========================================================
# QUICK QUESTIONS
# ==========================================================
st.markdown("## Suggested Questions")

quick_questions = [
    "What are the top 5 management priorities from this review?",
    "Where is the biggest profit improvement opportunity?",
    "What leakage issues should management validate first?",
    "What cost-saving actions can be implemented within 90 days?",
    "Summarize the business diagnosis for the CEO.",
    "What should be included in the board-level executive summary?",
]

selected_question = st.selectbox(
    "Choose a suggested question or type your own below",
    [""] + quick_questions,
)

custom_question = st.text_area(
    "Ask ProfitIQ AI Assistant",
    value=selected_question,
    height=120,
    placeholder="Example: What are the most urgent risks and opportunities from this review?",
)

# ==========================================================
# RESPONSE SESSION STATE
# ==========================================================
if "ai_assistant_response" not in st.session_state:
    st.session_state["ai_assistant_response"] = ""


# ==========================================================
# AI RESPONSE
# ==========================================================
if st.button("Ask AI Assistant"):
    if not custom_question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Generating executive AI response..."):
            response = answer_business_question(
                question=custom_question,
                context_data=context_data,
            )

        st.session_state["ai_assistant_response"] = response

if st.session_state.get("ai_assistant_response"):
    st.markdown("## Executive AI Response")

    st.markdown(
        f"""
        <div style="
            background:#FFFFFF;
            padding:1.5rem;
            border-radius:18px;
            border:1px solid #E6EAF0;
            box-shadow:0 8px 24px rgba(0,0,0,0.04);
            line-height:1.8;
            color:#334155;
        ">
            {st.session_state["ai_assistant_response"]}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================================
# PRIVACY NOTE
# ==========================================================
st.caption(
    "ProfitIQ AI uses the available analysis results in this session to answer your question. "
)

# ==========================================================
# NAVIGATION
# ==========================================================
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Back: Consulting Workflow"):
        st.switch_page("pages/09_Consulting_Workflow.py")

with col2:
    if st.button("Go to Dashboard"):
        st.switch_page("pages/06_Opportunity_Dashboard.py")

with col3:
    if st.button("Go to Executive Report"):
        st.switch_page("pages/08_Executive_Report.py")