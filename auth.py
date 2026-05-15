import streamlit as st
from supabase_config import get_supabase_client


def get_current_user():
    return st.session_state.get("user")


def is_logged_in():
    return st.session_state.get("user") is not None


def signup_user(email, password, full_name="", role="company_admin"):
    supabase = get_supabase_client()

    response = supabase.auth.sign_up(
        {
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "full_name": full_name,
                    "role": role,
                }
            },
        }
    )

    return response


def login_user(email, password):
    supabase = get_supabase_client()

    response = supabase.auth.sign_in_with_password(
        {
            "email": email,
            "password": password,
        }
    )

    if response.user:
        st.session_state["user"] = response.user
        st.session_state["access_token"] = response.session.access_token
        st.session_state["refresh_token"] = response.session.refresh_token

        load_user_profile(response.user.id)

    return response


def logout_user():
    supabase = get_supabase_client()

    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    st.session_state.clear()


def load_user_profile(user_id):
    supabase = get_supabase_client()

    result = (
        supabase.table("user_profiles")
        .select("*")
        .eq("id", user_id)
        .execute()
    )

    if result.data and len(result.data) > 0:
        st.session_state["user_profile"] = result.data[0]
        return result.data[0]

    user = st.session_state.get("user")

    fallback_profile = {
        "id": user_id,
        "email": user.email if user else "",
        "full_name": user.email if user else "User",
        "role": "company_admin",
        "is_active": True,
    }

    st.session_state["user_profile"] = fallback_profile
    return fallback_profile


def get_user_profile():
    return st.session_state.get("user_profile")


def get_user_role():
    profile = get_user_profile()
    if not profile:
        return None

    return profile.get("role")


def require_login():
    if not is_logged_in():
        st.warning("Please login to access this page.")

        if st.button("Go to Login"):
            st.switch_page("pages/00_Login.py")

        st.stop()


def require_role(allowed_roles):
    require_login()

    role = get_user_role()

    if role not in allowed_roles:
        st.error("You do not have permission to access this page.")
        st.stop()


def show_user_bar():
    profile = get_user_profile()

    if profile:
        full_name = profile.get("full_name") or "User"
        role = profile.get("role") or "User"

        col1, col2 = st.columns([4, 1])

        with col1:
            st.caption(f"Logged in as: {full_name} | Role: {role}")

        with col2:
            if st.button("Logout"):
                logout_user()
                st.switch_page("pages/00_Login.py")