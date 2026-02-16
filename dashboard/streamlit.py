import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()
API = os.getenv("API_SENHA_GERAL")

def get_dataframe_api(endpoint: str) -> pd.DataFrame:
    URL = "http://127.0.0.1:8000/api"
    headers = {"X-API-Key": API}
    response = requests.get(f"{URL}{endpoint}", headers = headers)
    if response.status_code == 200:
        data = response.json()
        return pd.DataFrame(data)
    else:
        st.error(f"Erro ao buscar dados - [{response.status_code}]")
        return None

st.title("Dashboard")
turmas_df = get_dataframe_api("/internal/turmas")

if turmas_df is not None:
    st.subheader("Lista de Turmas")
    for _, row in turmas_df.iterrows():
        st.write(f"{row['turma']} -- {row['ano']}")
