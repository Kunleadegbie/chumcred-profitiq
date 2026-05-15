import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


def get_supabase_client() -> Client:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError(
            "Missing Supabase credentials. Please set SUPABASE_URL and SUPABASE_ANON_KEY in your .env file."
        )

    supabase = create_client(supabase_url, supabase_key)

    # Attach logged-in user's access token so RLS sees the user as authenticated
    access_token = st.session_state.get("access_token")

    if access_token:
        try:
            supabase.postgrest.auth(access_token)
        except Exception:
            pass

    return supabase