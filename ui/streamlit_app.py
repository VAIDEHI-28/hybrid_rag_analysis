import sys
from pathlib import Path
import json
from datetime import datetime

# --------------------------------------------------
# Fix PYTHONPATH (VERY IMPORTANT for Streamlit)
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import streamlit as st

from ingestion.registry import DataRegistry
from ingestion.loader import load_excel_file
from ingestion.validator import validate_excel_files
from chains.hybrid_chain import HybridRAGChain

# --------------------------------------------------
# Config
# --------------------------------------------------
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

SESSIONS_DIR = Path("sessions")
SESSIONS_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title="Hybrid RAG Analytics Chatbot",
    layout="wide",
)

# --------------------------------------------------
# Helper functions for session persistence
# --------------------------------------------------
def list_sessions():
    return sorted(SESSIONS_DIR.glob("*.json"))

def load_session(session_id: str):
    path = SESSIONS_DIR / f"{session_id}.json"
    if not path.exists():
        return []
    return json.loads(path.read_text()).get("messages", [])

def save_session(session_id: str, messages):
    path = SESSIONS_DIR / f"{session_id}.json"
    payload = {
        "session_id": session_id,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "messages": messages,
    }
    path.write_text(json.dumps(payload, indent=2))

def new_session_id():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# --------------------------------------------------
# Sidebar – Session Selector
# --------------------------------------------------
st.sidebar.title("📂 Sessions")

existing_sessions = [f.stem for f in list_sessions()]

if "session_id" not in st.session_state:
    st.session_state.session_id = new_session_id()
    st.session_state.chat_history = []
    st.session_state.chain = None

selected_session = st.sidebar.selectbox(
    "Select a session",
    ["➕ New Session"] + existing_sessions,
)

if selected_session == "➕ New Session":
    st.session_state.session_id = new_session_id()
    st.session_state.chat_history = []
else:
    st.session_state.session_id = selected_session
    st.session_state.chat_history = load_session(selected_session)

st.sidebar.markdown(f"**Active session:** `{st.session_state.session_id}`")

# --------------------------------------------------
# Title
# --------------------------------------------------
st.title("🧠 Hybrid RAG Analytics Chatbot")
st.caption("Upload Excel data and ask analytical questions with guaranteed accuracy.")

# --------------------------------------------------
# Upload Section
# --------------------------------------------------
st.markdown("### 📂 Upload Excel Files")

uploaded_files = st.file_uploader(
    "Upload one or more Excel files",
    type=["xlsx", "xls"],
    accept_multiple_files=True,
)

# --------------------------------------------------
# Handle Upload
# --------------------------------------------------
if uploaded_files:
    # Replace uploads for THIS RUN (V1 behavior)
    for f in UPLOAD_DIR.glob("*"):
        f.unlink()

    saved_files = []

    for uploaded_file in uploaded_files:
        file_path = UPLOAD_DIR / uploaded_file.name
        file_path.write_bytes(uploaded_file.getbuffer())
        saved_files.append(file_path)

    try:
        validate_excel_files(saved_files)
    except Exception:
        st.error("❌ Invalid Excel file uploaded.")
        st.stop()

    registry = DataRegistry()

    for file_path in saved_files:
        sheets = load_excel_file(file_path)
        for sheet_name, df in sheets.items():
            registry.register_sheet(
                file_name=file_path.name,
                sheet_name=sheet_name,
                dataframe=df
            )

    data = registry.get_all_sheets()
    file = next(iter(data))
    sheet = next(iter(data[file]))
    df = data[file][sheet]

    st.session_state.chain = HybridRAGChain(df, registry)

    st.success("✅ Data uploaded successfully!")
    st.markdown("**Uploaded files:**")
    for f in saved_files:
        st.write(f"• {f.name}")

# --------------------------------------------------
# Chat Interface
# --------------------------------------------------
if st.session_state.chain:
    st.divider()
    st.markdown("### 💬 Analytics Chat")

    # Display previous messages
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    question = st.chat_input("Ask a question about your data")

    if question:
        # User message
        st.session_state.chat_history.append(
            {"role": "user", "content": question}
        )
        with st.chat_message("user"):
            st.markdown(question)

        # Assistant response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                try:
                    answer = st.session_state.chain.run(question)
                except Exception:
                    answer = "Something went wrong while processing the request."

                st.markdown(answer)

        st.session_state.chat_history.append(
            {"role": "assistant", "content": answer}
        )

        # Persist session
        save_session(
            st.session_state.session_id,
            st.session_state.chat_history
        )
