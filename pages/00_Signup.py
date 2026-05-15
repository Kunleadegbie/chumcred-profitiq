import streamlit as st
from auth import signup_user, is_logged_in
from modules.styling import apply_global_style

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="Signup | Chumcred ProfitIQ",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ==========================================================
# GLOBAL STYLE
# ==========================================================
apply_global_style()

# ==========================================================
# REDIRECT IF ALREADY LOGGED IN
# ==========================================================
if is_logged_in():
    st.success("You are already logged in.")

    if st.button("Go to Dashboard"):
        st.switch_page("pages/01_Company_Profile.py")

    st.stop()

# ==========================================================
# CUSTOM STYLING
# ==========================================================
st.markdown(
    """
    <style>
        .signup-container {
            max-width: 560px;
            margin: auto;
            padding-top: 3rem;
        }

        .signup-card {
            background: white;
            padding: 2rem;
            border-radius: 22px;
            border: 1px solid #E6EAF0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.06);
        }

        .signup-title {
            font-size: 2rem;
            font-weight: 800;
            color: #0B1F3A;
            margin-bottom: 0.5rem;
            text-align: center;
        }

        .signup-subtitle {
            text-align: center;
            color: #5B6575;
            margin-bottom: 2rem;
            line-height: 1.6;
        }

        div.stButton > button {
            background-color: #123C69;
            color: white;
            border-radius: 12px;
            border: none;
            font-weight: 700;
            padding: 0.75rem 1rem;
            width: 100%;
        }

        div.stButton > button:hover {
            background-color: #1D70A2;
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================================
# SIGNUP UI
# ==========================================================
st.markdown('<div class="signup-container">', unsafe_allow_html=True)

st.markdown(
    """
    <div class="signup-card">
        <div class="signup-title">Create ProfitIQ Account</div>
        <div class="signup-subtitle">
            Register to start a Business Growth & Leakage Review for your company.
        </div>
    """,
    unsafe_allow_html=True,
)

full_name = st.text_input("Full Name")
company_name = st.text_input("Company Name")
email = st.text_input("Email Address")
password = st.text_input("Password", type="password")
confirm_password = st.text_input("Confirm Password", type="password")

signup_btn = st.button("Create Account")

if signup_btn:
    if not full_name or not company_name or not email or not password or not confirm_password:
        st.warning("Please complete all fields.")

    elif password != confirm_password:
        st.error("Passwords do not match.")

    elif len(password) < 6:
        st.error("Password must be at least 6 characters.")

    else:
        try:
            response = signup_user(
                email=email,
                password=password,
                full_name=full_name,
                role="company_admin",
            )

            if response.user:
                st.success(
                    "Account created successfully. Please check your email to confirm your account before login."
                )
                st.info(
                    "After confirming your email, return to the login page and sign in."
                )

            else:
                st.warning("Signup submitted. Please check your email for confirmation.")

        except Exception as e:
            st.error(f"Signup failed: {e}")

st.markdown("</div>", unsafe_allow_html=True)

# ==========================================================
# LOGIN LINK
# ==========================================================
st.markdown("---")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.write("Already have an account?")

    if st.button("Go to Login"):
        st.switch_page("pages/00_Login.py")