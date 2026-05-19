import json
import streamlit as st
from utils.doc_types import DOC_TYPES, DOC_TYPE_NAMES
from utils.s3_upload import upload_fileobj_to_s3
from utils.ocr_api import submit_ocr_job, poll_until_done, get_job_result
from utils.db import save_job

st.set_page_config(
    page_title="IDP Playground",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Auth guard ───────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    st.warning("Please log in first.")
    st.switch_page("app.py")

user = st.session_state.user

# ─── Session state defaults ───────────────────────────────────────────────────
for key, val in {
    "ocr_result": None,
    "uploaded_s3_uri": None,
    "uploaded_filename": None,
    "selected_doc_type": DOC_TYPE_NAMES[0],
    "structure_input": json.dumps(DOC_TYPES[DOC_TYPE_NAMES[0]]["structure"], indent=2),
    "validation_result": None,
    "confirmed_mismatch": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

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

    if st.session_state["uploaded_s3_uri"]:
        st.divider()
        st.caption("📎 Uploaded file:")
        st.code(st.session_state["uploaded_filename"], language=None)

    st.divider()
    if st.button("📋 History", use_container_width=True):
        st.switch_page("pages/history.py")
    if st.button("Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
    <div style="margin-bottom: 0.5rem;">
        <h2 style="margin-bottom:0; color:#F0F4F8;">📄 IDP Playground</h2>
        <p style="color:#94A3B8; margin-top:0.2rem;">
            Select document type → upload PDF → extract structured data with AI
        </p>
    </div>
""", unsafe_allow_html=True)
st.divider()

col_left, col_right = st.columns([1, 1], gap="large")

# ══════════════════════════════════════════════════════════════════════════════
# LEFT COLUMN
# ══════════════════════════════════════════════════════════════════════════════
with col_left:

    st.markdown("### Step 1 — Document type")
    selected = st.selectbox(
        "Document type",
        options=DOC_TYPE_NAMES,
        index=DOC_TYPE_NAMES.index(st.session_state["selected_doc_type"]),
        key="doc_type_selector",
    )

    if selected != st.session_state["selected_doc_type"]:
        st.session_state["selected_doc_type"] = selected
        st.session_state["structure_input"] = json.dumps(DOC_TYPES[selected]["structure"], indent=2)
        st.session_state["uploaded_s3_uri"] = None
        st.session_state["uploaded_filename"] = None
        st.session_state["ocr_result"] = None
        st.session_state["validation_result"] = None
        st.session_state["confirmed_mismatch"] = False
        st.rerun()

    doc_config = DOC_TYPES[selected]

    st.markdown("### Step 2 — Edit structure")
    st.caption("Default extraction schema. Edit freely — changes will be sent to the API.")

    structure_input = st.text_area(
        "JSON structure",
        value=st.session_state["structure_input"],
        height=300,
        key="structure_editor",
    )
    st.session_state["structure_input"] = structure_input

    structure_valid = True
    parsed_structure = {}
    try:
        parsed_structure = json.loads(structure_input)
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON: {e}")
        structure_valid = False

    if structure_valid:
        st.success("JSON is valid ✓")

    st.divider()
    st.markdown("### Step 3 — Upload PDF")

    run_validation = st.checkbox(
        "Validate document type before uploading",
        value=False,
        help="Runs local OCR to check if PDF matches selected type."
    )

    uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"])

    if uploaded_file:
        st.caption(f"`{uploaded_file.name}` — {round(uploaded_file.size / 1024, 1)} KB")

        if run_validation and st.session_state["validation_result"] is None:
            if st.button("🔍 Validate document", use_container_width=True):
                with st.spinner("Running local OCR to classify document..."):
                    from utils.classifier import validate_doc_type
                    pdf_bytes = uploaded_file.read()
                    uploaded_file.seek(0)
                    val_result = validate_doc_type(pdf_bytes, selected, doc_config["classifier_label"])
                    st.session_state["validation_result"] = val_result
                    st.session_state["confirmed_mismatch"] = False
                st.rerun()

        val = st.session_state.get("validation_result")
        if val:
            if val["error"]:
                st.warning(f"Validation error: {val['error']}. You can still upload.")
            elif val["matches"]:
                st.success(f"✅ Detected as **{val['detected']}** — matches!")
            else:
                st.warning(f"⚠️ Detected as **{val['detected']}** but you selected **{selected}**. Proceed anyway?")
                if st.button("Yes, proceed anyway", type="secondary", use_container_width=True):
                    st.session_state["confirmed_mismatch"] = True
                    st.rerun()

        can_upload = True
        if run_validation:
            val = st.session_state.get("validation_result")
            if val is None:
                can_upload = False
            elif not val["matches"] and not st.session_state["confirmed_mismatch"]:
                can_upload = False

        if can_upload:
            if st.button("⬆️ Upload", use_container_width=True, type="primary"):
                with st.spinner(f"Uploading to `{doc_config['s3_folder']}/`..."):
                    result = upload_fileobj_to_s3(uploaded_file, uploaded_file.name, doc_config["s3_folder"])
                if result["success"]:
                    st.session_state["uploaded_s3_uri"] = result["s3_uri"]
                    st.session_state["uploaded_filename"] = result["filename"]
                    st.session_state["ocr_result"] = None
                    st.session_state["validation_result"] = None
                    st.session_state["confirmed_mismatch"] = False
                    st.success(f"✅ Uploaded ")
                else:
                    st.error(f"Upload failed: {result['error']}")

    if st.session_state["uploaded_s3_uri"]:
        st.divider()
        st.markdown("### Step 4 — Run OCR")
        st.info(f"**File:** `{st.session_state['uploaded_filename']}`", icon="✅")
        st.caption(f"Type: `{doc_config['api_type']}`")

        if st.button("🚀 Run ", type="primary", use_container_width=True, disabled=not structure_valid):
            with st.spinner("Submitting job..."):
                try:
                    job_response = submit_ocr_job(
                        st.session_state["uploaded_s3_uri"],
                        doc_config["api_type"],
                        parsed_structure
                    )
                    callback_url = job_response.get("callback_url", "")
                    job_id = callback_url.split("/")[-1]
                    st.session_state["job_id"] = job_id
                    st.session_state["ocr_result"] = None
                    st.success(f"Job submitted")
                except Exception as e:
                    st.error(f"Failed to submit: {e}")
                    st.stop()

            with st.spinner("Processing... polling every 3 seconds"):
                try:
                    result = poll_until_done(job_id, max_wait=120, interval=3)
                    st.session_state["ocr_result"] = result
                    try:
                        import json as _json
                        save_job(
                            user_id=user["id"],
                            job_id=job_id,
                            doc_type=selected,
                            filename=st.session_state["uploaded_filename"],
                            status=result.get("status", "fulfilled"),
                            result_json=_json.dumps(result),
                        )
                    except Exception as e:
                        st.warning(f"Could not save to history: {e}")
                    st.rerun()
                except TimeoutError:
                    st.error("Timed out. Fetch manually using the job ID above.")
                except Exception as e:
                    st.error(f"Error: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# RIGHT COLUMN — Results
# ══════════════════════════════════════════════════════════════════════════════
with col_right:
    st.markdown("### Results")

    result = st.session_state.get("ocr_result")

    if not result:
        st.markdown("""
            <div style="
                border: 1.5px dashed #2D7DD2;
                border-radius: 12px;
                padding: 64px 24px;
                text-align: center;
                color: #475569;
                background: #111827;
            ">
                <div style="font-size:2rem;">🧠</div>
                <div style="margin-top:0.5rem;">Results will appear here after processing.</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        status = result.get("status", "unknown")
        if status == "fulfilled":
            st.success(f"✅ Status: {status}")
        elif status == "failed":
            st.error(f"❌ Status: {status} — {result.get('error_message', '')}")
        else:
            st.warning(f"⏳ Status: {status}")

        filename = st.session_state.get("uploaded_filename", "result").replace(".pdf", "")
        st.download_button(
            label="⬇️ Download JSON",
            data=json.dumps(result, indent=2).encode("utf-8"),
            file_name=f"{filename}_result.json",
            mime="application/json",
            use_container_width=True,
        )
        st.divider()
        st.json(result)
