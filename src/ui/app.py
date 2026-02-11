"""RAG + MMM Platform — Streamlit entry point."""

import streamlit as st

st.set_page_config(
    page_title="RAG + MMM Platform",
    page_icon="📊",
    layout="wide",
)

st.title("RAG + MMM Platform")
st.markdown(
    """
    Welcome to the RAG + Marketing Mix Model platform.

    Use the sidebar to navigate between pages:
    - **RAG Chat** — Ask questions over your embedded documents
    - **MMM Dashboard** — View marketing mix model results
    - **Data Management** — Upload and manage datasets
    """
)
