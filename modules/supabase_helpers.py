import pandas as pd
import streamlit as st
from supabase_config import get_supabase_client


def get_user_context():
    user = st.session_state.get("user")
    profile = st.session_state.get("user_profile", {})

    return {
        "user_id": user.id if user else None,
        "company_id": profile.get("company_id"),
        "role": profile.get("role"),
    }


def dataframe_to_json(df):
    if df is None or df.empty:
        return []

    clean_df = df.copy()
    clean_df = clean_df.where(pd.notnull(clean_df), None)

    return clean_df.to_dict(orient="records")


def save_uploaded_dataset(project_id, dataset_type, file_name, df):
    supabase = get_supabase_client()
    ctx = get_user_context()

    payload = {
        "company_id": ctx["company_id"],
        "project_id": project_id,
        "uploaded_by": ctx["user_id"],
        "dataset_type": dataset_type,
        "file_name": file_name,
        "row_count": len(df) if df is not None else 0,
        "column_count": len(df.columns) if df is not None else 0,
        "data_json": dataframe_to_json(df),
    }

    return supabase.table("uploaded_datasets").insert(payload).execute()


def save_analysis_output(project_id, analysis_type, total_value, df):
    supabase = get_supabase_client()
    ctx = get_user_context()

    payload = {
        "company_id": ctx["company_id"],
        "project_id": project_id,
        "created_by": ctx["user_id"],
        "analysis_type": analysis_type,
        "total_value": float(total_value) if total_value else 0,
        "output_json": dataframe_to_json(df),
    }

    return supabase.table("analysis_outputs").insert(payload).execute()


def save_action_plan(project_id, action_df):
    supabase = get_supabase_client()
    ctx = get_user_context()

    if action_df is None or action_df.empty:
        return None

    records = []

    for _, row in action_df.iterrows():
        records.append(
            {
                "company_id": ctx["company_id"],
                "project_id": project_id,
                "created_by": ctx["user_id"],
                "action_id": row.get("Action ID"),
                "source": row.get("Source"),
                "issue_area": row.get("Issue Area"),
                "observation": row.get("Observation"),
                "recommended_action": row.get("Recommended Action"),
                "priority": row.get("Priority"),
                "expected_impact": float(row.get("Expected Impact", 0) or 0),
                "action_owner": row.get("Action Owner", ""),
                "department": row.get("Department", ""),
                "start_date": str(row.get("Start Date")) if row.get("Start Date") else None,
                "due_date": str(row.get("Due Date")) if row.get("Due Date") else None,
                "status": row.get("Status", "Not Started"),
                "actual_impact": float(row.get("Actual Impact", 0) or 0),
                "management_comment": row.get("Management Comment", ""),
            }
        )

    return supabase.table("action_plans").insert(records).execute()


def save_generated_report(project_id, report_name, report_type, report_summary):
    supabase = get_supabase_client()
    ctx = get_user_context()

    payload = {
        "company_id": ctx["company_id"],
        "project_id": project_id,
        "created_by": ctx["user_id"],
        "report_name": report_name,
        "report_type": report_type,
        "report_summary": report_summary,
    }

    return supabase.table("generated_reports").insert(payload).execute()


def create_review_project(project_name, review_start_date=None, review_end_date=None, notes=""):
    supabase = get_supabase_client()
    ctx = get_user_context()

    payload = {
        "company_id": ctx["company_id"],
        "created_by": ctx["user_id"],
        "project_name": project_name,
        "review_status": "Draft",
        "review_start_date": str(review_start_date) if review_start_date else None,
        "review_end_date": str(review_end_date) if review_end_date else None,
        "notes": notes,
    }

    return supabase.table("review_projects").insert(payload).execute()


def get_or_create_active_project():
    supabase = get_supabase_client()
    ctx = get_user_context()

    existing = (
        supabase.table("review_projects")
        .select("*")
        .eq("company_id", ctx["company_id"])
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if existing.data:
        return existing.data[0]

    created = create_review_project("Default ProfitIQ Review")

    if created.data:
        return created.data[0]

    return None


def fetch_uploaded_datasets(project_id):
    supabase = get_supabase_client()

    return (
        supabase.table("uploaded_datasets")
        .select("*")
        .eq("project_id", project_id)
        .order("created_at", desc=True)
        .execute()
    )


def fetch_analysis_outputs(project_id):
    supabase = get_supabase_client()

    return (
        supabase.table("analysis_outputs")
        .select("*")
        .eq("project_id", project_id)
        .order("created_at", desc=True)
        .execute()
    )


def fetch_action_plans(project_id):
    supabase = get_supabase_client()

    return (
        supabase.table("action_plans")
        .select("*")
        .eq("project_id", project_id)
        .order("created_at", desc=True)
        .execute()
    )

# ==========================================================
# LOAD COMPANY PROFILE
# ==========================================================
def load_company_profile(user_id):
    try:
        response = (
            supabase.table("companies")
            .select("*")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )

        if response.data and len(response.data) > 0:
            return response.data[0]

        return {}

    except Exception as e:
        print(f"Load company profile failed: {e}")
        return {}