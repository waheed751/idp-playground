import json
import streamlit as st
from utils.db import get_user_history, delete_job
from utils.ocr_api import get_job_result

st.set_page_config(
    page_title="Job History",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Auth guard ───────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    st.warning("Please log in first.")
    st.switch_page("app.py")

user = st.session_state.user

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"**{user.get('full_name') or user.get('username')}**")
    st.caption(f"@{user.get('username')}")
    st.divider()
    if st.button("🔬 Playground", use_container_width=True):
        st.switch_page("pages/playground.py")
    if st.button("Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("## 📋 Job History")
st.caption("All your past jobs. Click Download to save JSON results.")
st.divider()

# ─── Fetch history ────────────────────────────────────────────────────────────
history = get_user_history(user["id"])

if not history:
    st.info("No jobs yet. Go to the Playground to process your first document.")
    st.stop()

st.caption(f"{len(history)} job(s) found.")

# ─── Table header ─────────────────────────────────────────────────────────────
col_widths = [2, 1, 3, 1, 1, 1]
hcols = st.columns(col_widths)
for col, label in zip(hcols, ["Date", "Type", "Filename", "Status", "Download", "Delete"]):
    col.markdown(f"**{label}**")

st.divider()

# ─── History rows ─────────────────────────────────────────────────────────────
for row in history:
    cols = st.columns(col_widths)

    # Date
    cols[0].caption(str(row["created_at"].strftime("%Y-%m-%d %H:%M")))

    # Doc type badge
    doc_type = row["doc_type"]
    color = {"Insurance": "🟦", "Rent Roll": "🟩", "PFS": "🟨"}.get(doc_type, "⬜")
    cols[1].markdown(f"{color} {doc_type}")

    # Filename
    cols[2].caption(row["filename"])

    # Status
    status = row["status"]
    if status == "fulfilled":
        cols[3].success("✓ success")
    elif status == "failed":
        cols[3].error("✗")
    else:
        cols[3].warning("~")

    # Download button — served directly from DB
    with cols[4]:
        if row.get("result_json"):
            fname = row["filename"].replace(".pdf", "") + "_result.json"
            st.download_button(
                label="⬇️ Download",
                data=row["result_json"].encode("utf-8"),
                file_name=fname,
                mime="application/json",
                key=f"dl_{row['id']}",
                help="Download result JSON",
            )
        else:
            st.caption("—")
        

    # Delete button
    with cols[5]:
        if st.button("🗑️", key=f"del_{row['id']}", help="Remove from history"):
            delete_job(row["id"], user["id"])
            st.session_state.pop(f"download_data_{row['id']}", None)
            st.rerun()

    st.divider()
