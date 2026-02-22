import requests
import streamlit as st
import pandas as pd

API_URL = "http://127.0.0.1:8000/api/internal"

# =========================================================
# API
# =========================================================

def check_api_health():
    try:
        r = requests.get(f"{API_URL}/health", timeout=2)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False

def post_data(data: dict, endpoint: str) -> None:
    headers = {"Content-Type": "application/json"}
    url = f"{API_URL}/{endpoint}/"
    try:
        response = requests.post(
            url,
            json=data,
            headers=headers,
            timeout=5,
        )

        if response.ok:
            st.toast(f"{response.status_code} | 🟢")
        else:
            try:
                detail = response.json().get("detail", "")
            except ValueError:
                detail = response.text

            st.toast(f"{response.status_code} | 🔴 {detail}")

    except requests.RequestException:
        st.toast("Erro ao se conectar com a API 🔴")

@st.cache_data
def get_data(endpoint):
    try:
        r = requests.get(f"{API_URL}/{endpoint}/")
        r.raise_for_status()

        return pd.DataFrame(r.json())
    except requests.exceptions.RequestException:
        st.error("Erro ao buscar dados da API")
        st.stop()
        return pd.DataFrame()
