import streamlit as st
import pandas as pd
from datetime import date, timedelta
from modules.openai_ai import generate_ai_action_plan

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="Action Plan Tracker | Chumcred ProfitIQ",
    page_icon="✅",
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
from modules.supabase_helpers import get_or_create_active_project, save_action_plan

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
        <div class="page-title">Action Plan Tracker</div>
        <div class="page-subtitle">
            Convert findings from revenue analysis, leakage detection, and cost review into a practical
            90-day profit improvement action plan with owners, timelines, status, and impact tracking.
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
# GET PRIORITY ACTIONS
# ==========================================================
priority_df = st.session_state.get("priority_action_df")

if priority_df is None or priority_df.empty:
    st.warning("No priority actions found yet. Please complete the Opportunity Dashboard first.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Go to Opportunity Dashboard"):
            st.switch_page("pages/06_Opportunity_Dashboard.py")
    with col2:
        if st.button("Go to Revenue Analysis"):
            st.switch_page("pages/03_Revenue_Analysis.py")

    st.stop()

# ==========================================================
# INITIALIZE ACTION PLAN
# ==========================================================
if "action_plan_df" not in st.session_state:
    action_rows = []

    for idx, row in priority_df.reset_index(drop=True).iterrows():
        action_rows.append(
            {
                "Action ID": f"ACT-{idx + 1:03d}",
                "Source": row.get("Source", ""),
                "Issue Area": row.get("Issue Area", ""),
                "Observation": row.get("Observation", ""),
                "Recommended Action": row.get("Recommended Action", ""),
                "Priority": row.get("Priority", "Review"),
                "Expected Impact": row.get("Estimated Impact", 0),
                "Action Owner": "",
                "Department": "",
                "Start Date": date.today(),
                "Due Date": date.today() + timedelta(days=30),
                "Status": "Not Started",
                "Actual Impact": 0,
                "Management Comment": "",
            }
        )

    st.session_state.action_plan_df = pd.DataFrame(action_rows)

# ==========================================================
# SUMMARY KPIs
# ==========================================================
action_df = st.session_state.action_plan_df.copy()

total_actions = len(action_df)
completed_actions = len(action_df[action_df["Status"] == "Completed"])
in_progress_actions = len(action_df[action_df["Status"] == "In Progress"])
not_started_actions = len(action_df[action_df["Status"] == "Not Started"])
total_expected_impact = pd.to_numeric(action_df["Expected Impact"], errors="coerce").fillna(0).sum()
total_actual_impact = pd.to_numeric(action_df["Actual Impact"], errors="coerce").fillna(0).sum()

st.markdown("## 90-Day Action Plan Summary")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Actions", total_actions)
col2.metric("Completed", completed_actions)
col3.metric("In Progress", in_progress_actions)
col4.metric("Not Started", not_started_actions)

col1, col2, col3 = st.columns(3)
col1.metric("Expected Impact", f"₦{total_expected_impact:,.0f}")
col2.metric("Actual Impact Captured", f"₦{total_actual_impact:,.0f}")
achievement_rate = (total_actual_impact / total_expected_impact * 100) if total_expected_impact > 0 else 0
col3.metric("Impact Achievement", f"{achievement_rate:.1f}%")

# ==========================================================
# EDIT ACTION PLAN
# ==========================================================
st.markdown("## Update 90-Day Action Plan")

st.info(
    "Use the table below to assign owners, departments, timelines, status, actual impact, and management comments."
)

edited_df = st.data_editor(
    action_df,
    use_container_width=True,
    num_rows="dynamic",
    column_config={
        "Expected Impact": st.column_config.NumberColumn(
            "Expected Impact",
            format="₦%.0f",
            min_value=0,
        ),
        "Actual Impact": st.column_config.NumberColumn(
            "Actual Impact",
            format="₦%.0f",
            min_value=0,
        ),
        "Start Date": st.column_config.DateColumn("Start Date"),
        "Due Date": st.column_config.DateColumn("Due Date"),
        "Status": st.column_config.SelectboxColumn(
            "Status",
            options=[
                "Not Started",
                "In Progress",
                "Pending Management Approval",
                "Completed",
                "Deferred",
                "Dropped",
            ],
        ),
        "Priority": st.column_config.SelectboxColumn(
            "Priority",
            options=["High", "Medium", "Low", "Review"],
        ),
    },
)

# ==========================================================
# SAVE ACTION PLAN
# ==========================================================
if st.button("Save Updated Action Plan"):
    st.session_state.action_plan_df = edited_df

    project = st.session_state.get("active_project")

    if not project:
        st.warning("Action plan saved locally, but no active Supabase project was found.")
    else:
        try:
            save_action_plan(
                project_id=project.get("id"),
                action_df=edited_df,
            )
            st.success("Action plan updated and saved successfully to Supabase.")
        except Exception as e:
            st.error(f"Action plan updated locally, but Supabase save failed: {e}")

# ==========================================================
# STATUS SUMMARY
# ==========================================================
st.markdown("## Status Summary")

status_summary = (
    edited_df.groupby("Status", as_index=False)
    .agg(
        Actions=("Action ID", "count"),
        Expected_Impact=("Expected Impact", "sum"),
        Actual_Impact=("Actual Impact", "sum"),
    )
)

st.dataframe(status_summary, use_container_width=True)

# ==========================================================
# PRIORITY SUMMARY
# ==========================================================
st.markdown("## Priority Summary")

priority_summary = (
    edited_df.groupby("Priority", as_index=False)
    .agg(
        Actions=("Action ID", "count"),
        Expected_Impact=("Expected Impact", "sum"),
        Actual_Impact=("Actual Impact", "sum"),
    )
)

st.dataframe(priority_summary, use_container_width=True)

# ==========================================================
# INITIALIZE AI SESSION STATE
# ==========================================================
if "ai_action_plan_commentary" not in st.session_state:
    st.session_state["ai_action_plan_commentary"] = ""

# ==========================================================
# AI PREMIUM ACTION PLAN COMMENTARY
# ==========================================================
st.markdown("## AI Premium Action Plan Commentary")

if st.button("Generate AI 90-Day Execution Commentary"):
    company_profile = st.session_state.get("company_profile", {})
    company_name = company_profile.get("company_name", "the company")

    with st.spinner("Generating AI-powered action plan commentary..."):
        ai_action_plan_commentary = generate_ai_action_plan(
            company_name=company_name,
            priority_action_df=edited_df,
            leakage_df=st.session_state.get("leakage_df"),
            cost_saving_df=st.session_state.get("cost_saving_df"),
            revenue_opportunity_df=st.session_state.get("revenue_opportunity_df"),
        )

    st.session_state["ai_action_plan_commentary"] = ai_action_plan_commentary

# ==========================================================
# DISPLAY SAVED AI COMMENTARY
# ==========================================================
if st.session_state.get("ai_action_plan_commentary"):
    st.markdown("### Generated 90-Day Execution Commentary")
    st.markdown(st.session_state["ai_action_plan_commentary"])

# ==========================================================
# 90-DAY EXECUTION GUIDANCE
# ==========================================================
st.markdown("## Recommended Execution Discipline")

st.write("✅ Hold weekly review meetings with action owners.")
st.write("✅ Focus first on High Priority and high-impact items.")
st.write("✅ Validate every leakage before recovery or escalation.")
st.write("✅ Track actual savings, recoveries, and revenue improvement.")
st.write("✅ Report progress to management every two weeks.")
st.write("✅ Close the 90-day review with a final executive report.")

# ==========================================================
# NAVIGATION
# ==========================================================
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Back: Opportunity Dashboard"):
        st.switch_page("pages/06_Opportunity_Dashboard.py")

with col2:
    if st.button("Next: Executive Report"):
        st.switch_page("pages/08_Executive_Report.py")

with col3:
    if st.button("Back to Home"):
        st.switch_page("app.py")