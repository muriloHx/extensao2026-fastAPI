import os
from typing import Any, Dict

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

# =========================================================
# CONFIG
# =========================================================

load_dotenv()

API_KEY = os.getenv("INTERNAL_API_KEY")
API_URL = "http://127.0.0.1:8000/api/internal"

HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY,
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)


# =========================================================
# HELPERS
# =========================================================


def _url(endpoint: str) -> str:
    return f"{API_URL}/{endpoint}/"


def _handle_response(response: requests.Response) -> None:
    if response.ok:
        add_toast(f"{response.status_code} | 🟢")
        return

    try:
        detail = response.json().get("detail", "")
    except ValueError:
        detail = response.text

    add_toast(f"{response.status_code} | 🔴 {detail}")


def _request(method: str, url: str, **kwargs) -> requests.Response | None:
    try:
        response = SESSION.request(method, url, timeout=5, **kwargs)
        return response
    except requests.RequestException:
        add_toast("Erro ao se conectar com a API 🔴")
        return None


# =========================================================
# API
# =========================================================


def check_api_health() -> bool:
    response = _request("GET", f"{API_URL}/health")
    return bool(response and response.status_code == 200)


def post_data(data: Dict[str, Any], endpoint: str) -> None:
    response = _request("POST", _url(endpoint), json=data)
    if response:
        _handle_response(response)


def delete_data(item_id: int, endpoint: str) -> None:
    response = _request("DELETE", f"{_url(endpoint)}{item_id}")
    if response:
        _handle_response(response)


@st.cache_data(show_spinner=False)
def get_data(endpoint: str) -> pd.DataFrame:
    response = _request("GET", _url(endpoint))

    if not response:
        st.error("Erro ao buscar dados da API")
        st.stop()

    try:
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except requests.RequestException:
        st.error("Erro ao buscar dados da API")
        st.stop()

    return pd.DataFrame()


# =========================================================
# TOAST SYSTEM
# =========================================================


def add_toast(*args, **kwargs) -> None:
    st.session_state.setdefault("toasts", []).append((args, kwargs))


def render_toasts() -> None:
    for args, kwargs in st.session_state.pop("toasts", []):
        st.toast(*args, **kwargs)

    if st.session_state.pop("balloons", False):
        st.balloons()
