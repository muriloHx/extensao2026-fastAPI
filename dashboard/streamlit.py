import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": None,
    }
)



API_URL = "http://127.0.0.1:8000/api/internal"

st_autorefresh(interval=10000, key="healthcheck")  # recarrega o script a cada 10 segundos

@st.dialog("Baixar dataframe atual (.CSV)", width="medium")
def download_dialog():
    st.subheader("Você está prestes a baixar o dataframe atual")
    st.write("Filtros ativos:")
    filtros = pd.DataFrame(
        {
            "Anos": [anos_sel if anos_sel else "Nenhum filtro"],
            "Turmas": [turma_sel if turma_sel else "Nenhum filtro"],
            "Jogos": [jogos_sel if jogos_sel else "Nenhum filtro"],
            "Periodo": [
                f"{data_inicio_sel} -> {data_fim_sel}"
                if (data_inicio_sel is not None and data_fim_sel is not None)
                else "Nenhum filtro"
            ],
        },
        index=["Filtros Ativos"]
    )

    st.table(filtros)

    st.download_button(
        "Baixar CSV",
        data=lambda: df.to_csv(index=False).encode("utf-8"),
        file_name=f"dados{datetime.now().strftime("%Y-%M-%D")}.csv",
        mime="text/csv",
        type="primary",
        width="stretch"
    )

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
    if st.button("↻",
        width="stretch",
        help="Recarrega o script, verificando se há conexão",
        type="primary"):
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
df["data_execucao"] = pd.to_datetime(df["data_execucao"])


# ---- Sidebar filtros ----
with st.sidebar.expander("Filtros"):
    #filtro anos e turma
    col1, col2 = st.columns(2)
    with col1:
        anos_sel = st.multiselect(
            "Ano",
            sorted(df["ano"].dropna().unique()),
            placeholder="Selecione anos"

        )
    with col2:
        turma_sel = st.multiselect(
            "Turma",
            sorted(df["turma"].dropna().unique()),
            placeholder="Selecione turmas"
        )
    #filtro jogos
    jogos_sel = st.multiselect(
        "Jogo",
        sorted(df["jogo_nome"].unique()),
        placeholder="Selecione jogos"
    )

    #sel turma
    if anos_sel:
        df = df[df["ano"].isin(anos_sel)]

    if jogos_sel:
        df = df[df["jogo_nome"].isin(jogos_sel)]

    #filtro periodo
    col1, col2 = st.columns([3,1], vertical_alignment="bottom")
    data_min = df["data_execucao"].min().date()
    data_max = df["data_execucao"].max().date()
    data_inicio_sel, data_fim_sel = None, None

    if "periodo" not in st.session_state:
        st.session_state["periodo"] = (data_min, data_max)

    try:
        with col1:
            data_inicio_sel, data_fim_sel = st.date_input(
                "Período",
                value=(data_min, data_max),
                min_value=data_min,
                max_value=data_max,
                key = "periodo"
            )
    except ValueError:
        pass
    if data_inicio_sel is not None and data_fim_sel is not None:
        mascara = ((df["data_execucao"].dt.date >= data_inicio_sel) &
            (df["data_execucao"].dt.date <= data_fim_sel))
        df = df[mascara]
    with col2:
        st.button("↻", width="stretch", help="Recarrega o periodo completo",
            on_click=lambda: st.session_state.update(
                {"periodo": (data_min, data_max)}
            ))





st.sidebar.button("Baixar CSV", on_click=download_dialog, type="primary",width="stretch")



# ---- KPIs ----
st.title("Dashboard de Sessões")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Sessões", len(df))
col2.metric("Tempo Médio", round(df["tempo_total"].mean() or 0, 2))
col3.metric("Acertos Totais", int(df["acertos"].sum() or 0))
col4.metric("Erros Totais", int(df["erros"].sum() or 0))

st.divider()

# ---- Ranking de Jogos ----
st.subheader("Ranking de Jogos (por número de sessões)")

ranking = (
    df.groupby("jogo_nome")
      .size()
      .sort_values(ascending=False)
      .reset_index(name="total_sessoes")
)

st.dataframe(ranking, width="stretch")
# ---- Evolução por Data ----
st.subheader("Sessões por Dia")

por_dia = (
    df.groupby(df["data_execucao"].dt.date)
      .size()
)

st.line_chart(por_dia)

st.divider()

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
    width="stretch"
)
