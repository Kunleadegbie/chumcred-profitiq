import streamlit as st
from auth import login_user, is_logged_in
from modules.styling import apply_global_style

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="Login | Chumcred ProfitIQ",
    page_icon="🔐",
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

        .login-container {
            max-width: 500px;
            margin: auto;
            padding-top: 4rem;
        }

        .login-card {
            background: white;
            padding: 2rem;
            border-radius: 22px;
            border: 1px solid #E6EAF0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.06);
        }

        .login-title {
            font-size: 2rem;
            font-weight: 800;
            color: #0B1F3A;
            margin-bottom: 0.5rem;
            text-align: center;
        }

        .login-subtitle {
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
# LOGIN UI
# ==========================================================
st.markdown('<div class="login-container">', unsafe_allow_html=True)

st.markdown(
    """
    <div class="login-card">
        <div class="login-title">Chumcred ProfitIQ</div>
        <div class="login-subtitle">
            Login to access your Business Growth & Leakage Review Dashboard.
        </div>
    """,
    unsafe_allow_html=True,
)

email = st.text_input("Email Address")
password = st.text_input("Password", type="password")

login_btn = st.button("Login")

if login_btn:

    if not email or not password:
        st.warning("Please enter your email and password.")

    else:
        try:
            response = login_user(email, password)

            if response.user:
                st.success("Login successful.")

                st.switch_page("app.py")

            else:
                st.error("Invalid email or password.")

        except Exception as e:
            st.error(f"Login failed: {e}")

st.markdown("</div>", unsafe_allow_html=True)

# ==========================================================
# SIGNUP LINK
# ==========================================================
st.markdown("---")

col1, col2, col3 = st.columns([1,2,1])

with col2:
    st.write("Don't have an account?")

    if st.button("Create Account"):
        st.switch_page("pages/00_Signup.py")