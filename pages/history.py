import json
import streamlit as st
from utils.db import get_user_history, delete_job

st.set_page_config(
    page_title="History",
    layout="wide",
    initial_sidebar_state="expanded",
)

if not st.session_state.get("logged_in"):
    st.warning("Please log in first.")
    st.switch_page("app.py")

user = st.session_state.user

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div style="text-align:center; padding: 0.5rem 0 1rem 0;">
            <span style="font-size:1.5rem; font-weight:800; color:#2D7DD2;">IDP Playground</span><br>
        </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown(f"**{user.get('full_name') or user.get('username')}**")
    st.caption(f"@{user.get('username')}")
    st.divider()
    if st.button("🔬 Playground", use_container_width=True):
        st.switch_page("pages/playground.py")
    if st.button("Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
    <div style="margin-bottom: 0.5rem;">
        <h2 style="margin-bottom:0; color:#F0F4F8;">📋 Job History</h2>
        <p style="color:#94A3B8; margin-top:0.2rem;">
            All your past OCR jobs. Download results anytime.
        </p>
    </div>
""", unsafe_allow_html=True)
st.divider()

history = get_user_history(user["id"])

if not history:
    st.markdown("""
        <div style="
            border: 1.5px dashed #2D7DD2;
            border-radius: 12px;
            padding: 48px 24px;
            text-align: center;
            color: #475569;
            background: #111827;
        ">
            <div style="font-size:2rem;">📭</div>
            <div style="margin-top:0.5rem;">No jobs yet. Go to the Playground to process your first document.</div>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

st.caption(f"{len(history)} job(s) found.")

# ─── Table header ─────────────────────────────────────────────────────────────
col_widths = [2, 1, 3, 1, 1, 1]
hcols = st.columns(col_widths)
for col, label in zip(hcols, ["Date", "Type", "Filename", "Status", "Download", "Delete"]):
    col.markdown(f"**{label}**")
st.divider()

# ─── Rows ─────────────────────────────────────────────────────────────────────
TYPE_COLORS = {"Insurance": "🟦", "Rent Roll": "🟩", "PFS": "🟨"}

for row in history:
    cols = st.columns(col_widths)

    cols[0].caption(row["created_at"].strftime("%Y-%m-%d %H:%M"))
    cols[1].markdown(f"{TYPE_COLORS.get(row['doc_type'], '⬜')} {row['doc_type']}")
    cols[2].caption(row["filename"])

    status = row["status"]
    if status == "fulfilled":
        cols[3].success("✓")
    elif status == "failed":
        cols[3].error("✗")
    else:
        cols[3].warning("~")

    with cols[4]:
        if row.get("result_json"):
            fname = row["filename"].replace(".pdf", "") + "_result.json"
            st.download_button(
                label="⬇️",
                data=row["result_json"].encode("utf-8"),
                file_name=fname,
                mime="application/json",
                key=f"dl_{row['id']}",
                help="Download result JSON",
            )
        else:
            st.caption("—")

    with cols[5]:
        if st.button("🗑️", key=f"del_{row['id']}", help="Remove from history"):
            delete_job(row["id"], user["id"])
            st.rerun()

    st.divider()

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
    <div style="text-align:center; margin-top:2rem; color:#475569; font-size:0.8rem;">
        © Doclus.ai · Intelligent Document Processing
    </div>
""", unsafe_allow_html=True)
