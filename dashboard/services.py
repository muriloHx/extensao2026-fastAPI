import requests
import streamlit as st
import pandas as pd

API_URL = "http://127.0.0.1:8000/api/internal"
headers = {"Content-Type": "application/json"}

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
    url = f"{API_URL}/{endpoint}/"
    try:
        response = requests.post(
            url,
            json=data,
            headers=headers,
            timeout=5,
        )

        if response.ok:
            add_toast(f"{response.status_code} | 🟢")
        else:
            try:
                detail = response.json().get("detail", "")
            except ValueError:
                detail = response.text

            add_toast(f"{response.status_code} | 🔴 {detail}")

    except requests.RequestException:
        add_toast("Erro ao se conectar com a API 🔴")

@st.cache_data()
def get_data(endpoint: str):
    try:
        r = requests.get(f"{API_URL}/{endpoint}/")
        r.raise_for_status()

        return pd.DataFrame(r.json())
    except requests.exceptions.RequestException:
        st.error("Erro ao buscar dados da API")
        st.stop()
        return pd.DataFrame()

def delete_data(id: int, endpoint: str):
    try:
        response = requests.delete(
            f"{API_URL}/{endpoint}/{id}",
            headers=headers,
            timeout=5
        )
        if response.ok:
           add_toast(f"{response.status_code} | 🟢")
        else:
            try:
                detail = response.json().get("detail", "")
            except ValueError:
                detail = response.text

            add_toast(f"{response.status_code} | 🔴 {detail}")

    except requests.RequestException:
        add_toast("Erro ao se conectar com a API 🔴")

def add_toast(mensagem: str):
    if 'toast' not in st.session_state:
        st.session_state['toast'] = mensagem

def render_toasts():
    if "toast" in st.session_state:
        st.toast(st.session_state["toast"])
        del st.session_state["toast"]
    if "balloons" in st.session_state:
        st.balloons()
        del st.session_state["balloons"]
