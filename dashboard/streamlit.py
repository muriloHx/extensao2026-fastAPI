import streamlit as st
import requests
import pandas as pd
from streamlit_autorefresh import st_autorefresh


API_URL = "http://127.0.0.1:8000/api/internal"

st_autorefresh(interval=10000, key="healthcheck")  # recarrega o script a cada 10 segundos

def check_api_health():
    try:
        r = requests.get(f"{API_URL}/health", timeout = 2)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False

api_online = check_api_health()

col1, col2 = st.sidebar.columns([3, 1], vertical_alignment="center")

with col1:
    if api_online:
        st.success("API Online")
    else:
        st.error("API Offline")

with col2:
    if st.button("↻", width="stretch", help="Recarrega o script, verificando se há conexão"):
        if check_api_health():
            st.toast("Conectado", icon="🟢")
        else:
            st.toast("Sem conexão com a API", icon="🔴")


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

# ---- Carregar dados ----
turmas = get_data("turmas")
jogos = get_data("jogos")
sessoes = get_data("sessoes")

# ---- Normalizar joins ----
df = sessoes.merge(
    turmas,
    left_on="turma_id",
    right_on="id",
    suffixes=("", "_turma"),
)

df = df.merge(
    jogos,
    left_on="jogo_id",
    right_on="id",
    suffixes=("", "_jogo"),
)

df.rename(columns={"nome": "jogo_nome"}, inplace=True)

# ---- Sidebar filtros ----
st.sidebar.header("Filtros")

anos = st.sidebar.multiselect(
    "Ano",
    sorted(df["ano"].dropna().unique())
)

jogos_sel = st.sidebar.multiselect(
    "Jogo",
    sorted(df["jogo_nome"].unique())
)

if anos:
    df = df[df["ano"].isin(anos)]

if jogos_sel:
    df = df[df["jogo_nome"].isin(jogos_sel)]

# ---- KPIs ----
st.title("Dashboard de Sessões")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Sessões", len(df))
col2.metric("Tempo Médio", round(df["tempo_total"].mean() or 0, 2))
col3.metric("Acertos Totais", int(df["acertos"].sum() or 0))
col4.metric("Erros Totais", int(df["erros"].sum() or 0))

# ---- Ranking de Jogos ----
st.subheader("Ranking de Jogos (por número de sessões)")

ranking = (
    df.groupby("jogo_nome")
      .size()
      .sort_values(ascending=False)
      .reset_index(name="total_sessoes")
)

st.dataframe(ranking, use_container_width=True)

# ---- Evolução por Data ----
st.subheader("Sessões por Dia")

df["data_execucao"] = pd.to_datetime(df["data_execucao"])
por_dia = (
    df.groupby(df["data_execucao"].dt.date)
      .size()
)

st.line_chart(por_dia)

# ---- Tabela detalhada ----
st.subheader("Dados detalhados")

st.dataframe(
    df[[
        "ano",
        "turma",
        "jogo_nome",
        "palavra",
        "dificuldade",
        "tempo_total",
        "acertos",
        "erros",
        "data_execucao",
    ]],
    use_container_width=True
)
