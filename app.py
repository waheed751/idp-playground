import streamlit as st
from utils.db import init_db, verify_user, create_user

st.set_page_config(
    page_title="IDP Playground",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.logged_in:
    st.switch_page("pages/playground.py")

# ─── Branding ─────────────────────────────────────────────────────────────────
st.markdown("""
    <div style="text-align:center; padding: 2rem 0 1rem 0;">
        <h1 style="font-size: 2.2rem; font-weight: 800; color: #2D7DD2; margin-bottom: 0;">
            Intelligent Document Processing
        </h1>
        
    </div>
""", unsafe_allow_html=True)

st.divider()
st.markdown("#### Sign in to your account")
username = st.text_input("Username", key="login_username")
password = st.text_input("Password", type="password", key="login_password")
if st.button("Login", use_container_width=True, type="primary"):
    if not username or not password:
        st.error("Please enter both username and password.")
    else:
        user = verify_user(username, password)
        if user:
            st.session_state.clear()
            st.session_state.logged_in = True
            st.session_state.user = dict(user)
            st.rerun()
        else:
            st.error("Invalid username or password.")
st.markdown("""
    <div style="text-align:center; margin-top: 3rem; color: #475569; font-size: 0.8rem;">
        All rights reserved
    </div>
""", unsafe_allow_html=True)
