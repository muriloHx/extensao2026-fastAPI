import streamlit as st
import pandas as pd
from services import get_data, post_data, delete_data, render_toasts
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
    col1, col2, col3, col4 = st.columns([2,2,2,2])
    with col1:
        st.metric("Total turmas", len(df))
    with col2:
        st.metric("Total anos", len(df["ano"].unique()))
    with col3:
        st.metric("Total seção", len(df["turma"].unique()))
    with col4:
        if st.button("Recarregar dados", type="primary", key="reload_cache_turmas"):
            st.cache_data.clear()

def render_forms():
    col1, col2 = st.columns(2)

    with col1:
        with st.form("post_turma_form", enter_to_submit=False):
            st.subheader("Adicione Turmas")
            ano = st.number_input("Ano", placeholder="Ex: 5", min_value=1, value=None)
            turma = st.text_input("Turma", placeholder="Ex: B")

            submitted = st.form_submit_button("Adicionar")

            if submitted:
                data = {"ano": ano, "turma": turma}
                post_data(data, "turmas")

    with col2:
        with st.form("delete_turma_form", enter_to_submit=False):
            st.subheader("Excluir Turmas")
            id = st.number_input("ID", placeholder="Ex: 10", min_value=0, value=None)
            st.space("large")
            if st.form_submit_button("Excluir"):
                dialog_confirm(id)

# =========================================================
# UTILS
# =========================================================

@st.dialog("Excluir Turma", width="small")
def dialog_confirm(id):
    st.warning("Isso apagará todas as sessões associadas com essa turma!")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Sim", type="primary"):
            delete_data(id, "turmas")
            st.rerun()
    with c2:
        if st.button("Cancelar"):
            st.rerun()

# =========================================================
# MAIN
# =========================================================

def main():
    configure_page()
    render_api_status()
    df_turmas = get_data("turmas")
    df_turmas = df_turmas.set_index("id")

    render_toasts()
    render_kpis(df_turmas)
    render_forms()
    st.table(df_turmas)




with st.spinner("Carregando"):
    main()
