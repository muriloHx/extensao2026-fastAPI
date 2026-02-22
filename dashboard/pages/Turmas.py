import streamlit as st
import pandas as pd
from services import get_data, post_data
from App import render_api_status
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
    col1, col2, col3, _ = st.columns([1,1,1,2])
    with col1:
        st.metric("Total turmas", len(df))
    with col2:
        st.metric("Total anos", len(df["ano"].unique()))
    with col3:
        st.metric("Total seção", len(df["turma"].unique()))

def render_forms():
    col1, col2 = st.columns(2)

    with col1:
        with st.form("post_turma_form", enter_to_submit=False):
            st.subheader("Adicione Turmas")
            turma = st.text_input("Turma", placeholder="Ex: B")
            ano = st.number_input("Ano", placeholder="Ex: 5", min_value=1)

            submitted = st.form_submit_button("Adicionar")

            if submitted:
                data = {"ano": ano, "turma": turma}
                post_data(data, "turmas")

def main():
    configure_page()
    render_api_status()
    df_turmas = get_data("turmas")
    df_turmas = df_turmas.set_index("id")


    render_kpis(df_turmas)
    render_forms()
    st.table(df_turmas)


with st.spinner("Carregando"):
    main()
