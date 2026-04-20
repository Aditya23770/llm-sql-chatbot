import streamlit as st
import requests
import pandas as pd

# ---------------------------------------------------------------------------
# Config — reads from st.secrets on Streamlit Cloud, falls back to env vars
# ---------------------------------------------------------------------------
try:
    BACKEND_URL = st.secrets["BACKEND_URL"]
    API_KEY = st.secrets["API_KEY"]
except Exception:
    import os
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
    API_KEY = os.getenv("API_KEY", "")

PROVIDERS = ["groq", "openai", "anthropic"]

# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Data-Whisperer", page_icon="🗄️", layout="centered")
st.title("Data-Whisperer")
st.caption("Ask questions about your data in plain English.")

with st.form("query_form"):
    user_query = st.text_input("Your question", placeholder="Show me all female customers from Mumbai")
    provider = st.selectbox("LLM provider", PROVIDERS, index=0)
    submitted = st.form_submit_button("Run query")

if submitted and user_query.strip():
    with st.spinner("Thinking…"):
        try:
            resp = requests.post(
                f"{BACKEND_URL}/query",
                json={"query": user_query, "provider": provider},
                headers={"X-API-Key": API_KEY},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.HTTPError as exc:
            st.error(f"Backend error {exc.response.status_code}: {exc.response.text}")
            st.stop()
        except Exception as exc:
            st.error(f"Request failed: {exc}")
            st.stop()

    if data.get("cached"):
        st.info("Result served from cache")

    st.subheader("Generated SQL")
    st.code(data["sql_query"], language="sql")

    results = data.get("results", [])
    if results:
        st.subheader(f"Results ({len(results)} row{'s' if len(results) != 1 else ''})")
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.warning("Query returned no results.")
