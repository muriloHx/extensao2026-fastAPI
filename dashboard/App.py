import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from services import get_data, check_api_health, add_toast, render_toasts
import plotly.graph_objects as go

# =========================================================
# CONFIG
# =========================================================


def configure_page():
    st.set_page_config(
        page_title="Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": None,
            "Report a bug": None,
            "About": None,
        },
    )

# =========================================================
# DATA PROCESSING
# =========================================================
def load_and_prepare_data():
    turmas = get_data("turmas")
    jogos = get_data("jogos")
    sessoes = get_data("sessoes")
    alunos = get_data("alunos")

    alunos.rename(columns={"nome": "aluno_nome"}, inplace=True)
    jogos.rename(columns={"nome": "jogo_nome"}, inplace=True)

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
    df = df.merge(
        alunos,
        left_on="aluno_ra",
        right_on="ra",
        suffixes=("","_aluno"),
    )


    df["data_execucao"] = pd.to_datetime(df["data_execucao"])

    return df


def apply_filters(df_completo, filtros):
    df = df_completo.copy()

    if filtros["anos"]:
        df = df[df["ano"].isin(filtros["anos"])]

    if filtros["jogos"]:
        df = df[df["jogo_nome"].isin(filtros["jogos"])]

    if filtros["turmas"]:
        df = df[df["turma"].isin(filtros["turmas"])]

    if filtros["data_inicio"] and filtros["data_fim"]:
        mascara = (
            (df["data_execucao"].dt.date >= filtros["data_inicio"])
            & (df["data_execucao"].dt.date <= filtros["data_fim"])
        )
        df = df[mascara]

    return df


# =========================================================
# SIDEBAR
# =========================================================

def render_api_status():
    api_online = check_api_health()

    col1, col2 = st.sidebar.columns([3, 1], vertical_alignment="center")

    with col1:
        placeholder = st.empty()
        if not api_online:
            placeholder.error("API Offline")
        else:
            placeholder.success("API Online")

    if not api_online:
        st_autorefresh(interval=5000, key="healthcheck")

    with col2:
        if st.button(
            "↻",
            width="stretch",
            help="Recarrega o script",
            type="primary",
        ):
            if check_api_health():
                add_toast("Conectado", icon="🟢")
            else:
                add_toast("Sem conexão com a API", icon="🔴")


def render_filters(df_completo):
    with st.sidebar.expander("Filtros"):
        col1, col2 = st.columns(2)

        with col1:
            anos_sel = st.multiselect(
                "Ano",
                sorted(df_completo["ano"].dropna().unique()),
                placeholder="Selecione anos",
            )

        with col2:
            turma_sel = st.multiselect(
                "Turma",
                sorted(df_completo["turma"].dropna().unique()),
                placeholder="Selecione turmas",
            )

        jogos_sel = st.multiselect(
            "Jogo",
            sorted(df_completo["jogo_nome"].unique()),
            placeholder="Selecione jogos",
        )

        # Filtro de período
        data_min = df_completo["data_execucao"].min().date()
        data_max = df_completo["data_execucao"].max().date()

        data_inicio_sel = data_fim_sel = None

        col1, col2 = st.columns([3,1], vertical_alignment="bottom")
        try:
            with col1:
                data_inicio_sel, data_fim_sel = st.date_input(
                    "Período",
                    value=(data_min, data_max),
                    min_value=data_min,
                    max_value=data_max,
                    key="periodo",
                )
        except ValueError: #ao clicar no primeiro dia,só uma data é retornada, como se espera duas, gera um ValueError
            pass
        with col2:
            st.button(
                "↻",
                width="stretch",
                help="Recarrega o periodo completo",
                on_click=lambda: st.session_state.update(
                    {"periodo": (data_min, data_max)}
                ),
                key="reload_periodo",
            )

    return {
        "anos": anos_sel,
        "turmas": turma_sel,
        "jogos": jogos_sel,
        "data_inicio": data_inicio_sel if data_inicio_sel else None,
        "data_fim": data_fim_sel if data_fim_sel else None,
    }


# =========================================================
# DOWNLOAD
# =========================================================

def render_download_dialog(df, filtros):
    @st.dialog("Baixar dataframe atual (.CSV)", width="small")
    def download_dialog():
        st.subheader("Você está prestes a baixar o dataframe atual")

        filtros_df = pd.DataFrame(
            {
                "Anos": [filtros["anos"] or "Nenhum filtro"],
                "Turmas": [filtros["turmas"] or "Nenhum filtro"],
                "Jogos": [filtros["jogos"] or "Nenhum filtro"],
                "Periodo": [
                    f'{filtros["data_inicio"]} -> {filtros["data_fim"]}'
                    if filtros["data_inicio"] and filtros["data_fim"]
                    else "Nenhum filtro"
                ],
            },
            index=["Filtros Ativos"],
        )

        st.table(filtros_df)

        if st.download_button(
            "Baixar CSV",
            data=lambda: df.to_csv(index=False).encode("utf-8"),
            file_name=f"dados_{datetime.now().strftime('%Y-%m-%d')}.csv",
            mime="text/csv",
            type="primary",
            width="stretch",
            key="download_button_csv",
        ):
            st.session_state["balloons"] = True
            st.rerun()

    st.sidebar.button(
        "Baixar CSV",
        on_click=download_dialog,
        type="primary",
        width="stretch",
        key="sidebar_dialog_download_button"
    )


# =========================================================
# DASHBOARD
# =========================================================

def render_kpis(df):
    st.title("Dashboard de Sessões")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Sessões", len(df))
    col2.metric("Tempo Médio", round(df["tempo_total"].mean() or 0, 2))
    col3.metric("Acertos Totais", int(df["acertos"].sum() or 0))
    col4.metric("Erros Totais", int(df["erros"].sum() or 0))
    with col5:
        if st.button("Recarregar dados", type="primary", key="reload_cache_app"):
            print("Recarregar dados")
            st.session_state.pop("df_completo", None)
            st.rerun()

    st.divider()


def render_ranking(df):
    st.subheader("Ranking de Jogos (por número de sessões)")

    ranking = (
        df.groupby("jogo_nome")
        .size()
        .sort_values(ascending=False)
        .reset_index(name="total_sessoes")
    )

    st.dataframe(ranking, width="stretch")


def render_evolution(df):
    st.subheader("Sessões por Dia")

    por_dia = df.groupby(df["data_execucao"].dt.date).size()
    st.line_chart(por_dia)

    st.divider()

def render_acertos_turma(df):
    df = df.copy()
    df["taxa_acerto"] = df["acertos"] / (df["acertos"] + df["erros"])

    turma_stats = (
        df.groupby("turma")
        .agg(
            taxa_acerto=("taxa_acerto", "mean"),
            total_sessoes=("acertos", "count"),
        )
        .reset_index()
        .sort_values("taxa_acerto", ascending=False)
    )
    turma_stats["taxa_acerto_pct"] = (turma_stats["taxa_acerto"] * 100).round(1)

    media_geral = turma_stats["taxa_acerto_pct"].mean()
    melhor = turma_stats.iloc[0]
    pior = turma_stats.iloc[-1]


    help_melhor_turma = "A turma com maior taxa de acerto média. Calculada fazendo acertos / (acertos + erros) em cada sessão, depois tirando a média de todas as sessões daquela turma. A que tiver a maior média aparece aqui."
    help_media_geral = "A média das taxas de acerto de todas as turmas, usada como linha de referência no gráfico. Turmas acima dela ficam verdes, abaixo ficam vermelhas."
    help_atencao = "O oposto da melhor turma: a que tem a menor taxa de acerto média, ou seja, a que mais erra proporcionalmente."
    col1, col2, col3 = st.columns(3)
    col1.metric("Melhor turma", melhor["turma"], f"{melhor['taxa_acerto_pct']}%", help = help_melhor_turma)
    col2.metric("Média geral", f"{media_geral:.1f}%", help = help_media_geral)
    col3.metric("Atenção", pior["turma"], f"{pior['taxa_acerto_pct']}%", delta_color="inverse", help = help_atencao)


    cores = [
        "#1D9E75" if v >= media_geral else "#E24B4A"
        for v in turma_stats["taxa_acerto_pct"]
    ]

    fig = go.Figure()
    fig.add_bar(
        x=turma_stats["turma"],
        y=turma_stats["taxa_acerto_pct"],
        marker_color=cores,
        hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
    )
    fig.add_hline(
        y=media_geral,
        line_dash="dash",
        line_color="gray",
        line_width=1.5,
        annotation_text=f"média {media_geral:.1f}%",
        annotation_position="top right",
    )
    fig.update_layout(
        yaxis=dict(range=[0, 100], ticksuffix="%", title="taxa de acerto"),
        xaxis_title="turma",
        showlegend=False,
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig, width="stretch")


def render_table(df):
    st.subheader("Dados detalhados")

    st.dataframe(
        df[
            [
                "ano",
                "turma",
                "aluno_nome",
                "aluno_ra",
                "jogo_nome",
                "palavra",
                "dificuldade",
                "tempo_total",
                "acertos",
                "erros",
                "data_execucao",

            ]
        ],
        width="stretch",
        placeholder="",
    )



# =========================================================
# MAIN
# =========================================================
def main():
    configure_page()
    render_api_status()

    if "df_completo" not in st.session_state:
        st.session_state["df_completo"] = load_and_prepare_data()

    df_completo = st.session_state["df_completo"]
    filtros = render_filters(df_completo)
    df = apply_filters(df_completo, filtros)

    render_toasts()
    render_download_dialog(df, filtros)

    render_kpis(df)
    col1, col2 = st.columns(2)

    with col1:
        render_ranking(df)
    with col2:
        render_evolution(df)

    st.subheader("Turmas")
    render_acertos_turma(df)

    render_table(df)


with st.spinner("Carregando"):
    main()
