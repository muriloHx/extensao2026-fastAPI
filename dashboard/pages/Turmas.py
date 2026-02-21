import streamlit as st
import pandas as pd
from App import check_api_health, render_api_status, get_data
import requests

def configure_page():
    st.set_page_config(
        page_title="Gerenciar Turmas",
        page_icon="🏫",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": None,
            "Report a bug": None,
            "About": None,
        },
    )

def render_kpis(df):
    st.title("Gerenciar Turmas")
    st.metric("Total turmas", len(df))

def post_turma(turma_nome: str, ano: int) -> None:
    url = "http://127.0.0.1:8000/api/internal/turmas/"
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(
            url,
            json={"ano": ano, "turma":turma_nome},
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

def main():
    configure_page()
    render_api_status()
    df_turmas = get_data("turmas")
    df_turmas = df_turmas.set_index("id")


    render_kpis(df_turmas)

    st.table(df_turmas)



main()
