import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static

# Configuração da página
st.set_page_config(
    page_title="Análise de Crimes Violentos",
    layout="wide",
)

# Função para carregar e validar dados
@st.cache_data
def carregar_dados(arquivo):
    df = pd.read_csv(arquivo, delimiter=';')
    colunas_necessarias = {"LATITUDE", "LONGITUDE", "DATA_FATO", "CODIGO_NATUREZA_PRINCIPAL", "SETOR", "UNID_REGISTRO_NIVEL_6"}
    if not colunas_necessarias.issubset(df.columns):
        st.error("O arquivo CSV deve conter as colunas necessárias: LATITUDE, LONGITUDE, DATA_FATO, CODIGO_NATUREZA_PRINCIPAL, SETOR e UNID_REGISTRO_NIVEL_6.")
        return None
    
    naturezas_crimes_violentos = {"B01121", "B02001", "B01148", "C01157", "C01158", "D01213", "D01217", "C01159"}
    df = df[df["CODIGO_NATUREZA_PRINCIPAL"].isin(naturezas_crimes_violentos)]
    df["DATA_FATO"] = pd.to_datetime(df["DATA_FATO"], format="%d/%m/%Y", errors="coerce")
    df["LATITUDE"] = pd.to_numeric(df["LATITUDE"].str.replace(",", ".", regex=False), errors="coerce")
    df["LONGITUDE"] = pd.to_numeric(df["LONGITUDE"].str.replace(",", ".", regex=False), errors="coerce")
    df = df.dropna(subset=["LATITUDE", "LONGITUDE", "DATA_FATO"])
    return df

# Layout principal
st.sidebar.title("Navegação")
pagina = st.sidebar.radio("Escolha uma página", ["Introdução", "Análise por Local", "Análise por Tempo", "Análise por Tipo de Crime"])

# Upload de arquivo
st.sidebar.title("Upload de Arquivo")
arquivo = st.sidebar.file_uploader("Faça upload do arquivo CSV", type=["csv"])
dados = carregar_dados(arquivo) if arquivo else None

# Inicialização do estado de sessão
if "filtro_setor" not in st.session_state:
    st.session_state["filtro_setor"] = None

# Introdução
if pagina == "Introdução":
    st.title("Análise de Crimes Violentos")
    st.markdown("""
        Este aplicativo permite analisar dados sobre crimes violentos de maneira interativa.
        Você pode navegar entre as páginas:
        - **Análise por Local**: Explore os dados geograficamente.
        - **Análise por Tempo**: Analise tendências temporais.
        - **Análise por Tipo de Crime**: Veja detalhes baseados nos tipos de crimes.
        
        Faça o upload de um arquivo CSV contendo os dados para começar.
    """)

# Página 1: Análise por Local
if pagina == "Análise por Local" and dados is not None:
    st.title("Análise por Local")
    
    # Aplicar filtro de setor se houver
    if st.session_state["filtro_setor"]:
        dados = dados[dados["SETOR"] == st.session_state["filtro_setor"]]
    
    st.subheader("Gráfico de Barras: Crimes por Região")
    barra_local = dados["SETOR"].value_counts().reset_index(name="QUANTIDADE")
    barra_local.rename(columns={"index": "SETOR"}, inplace=True)
    fig_barra = px.bar(barra_local, x="SETOR", y="QUANTIDADE", labels={"SETOR": "Setor", "QUANTIDADE": "Quantidade"})
    
    # Atualizar filtro ao clicar no gráfico
    selected_point = st.plotly_chart(fig_barra, use_container_width=True)
    if selected_point is not None and len(selected_point["points"]) > 0:
        st.session_state["filtro_setor"] = selected_point["points"][0]["x"]
        st.experimental_rerun()

    st.subheader("Gráfico de Pizza: Distribuição de Crimes por Setor")
    fig_pizza = px.pie(barra_local, names="SETOR", values="QUANTIDADE")
    st.plotly_chart(fig_pizza, use_container_width=True)
    
    st.subheader("Mapa Interativo")
    mapa = folium.Map(location=[dados["LATITUDE"].mean(), dados["LONGITUDE"].mean()], zoom_start=12)
    for _, row in dados.iterrows():
        folium.Marker([row["LATITUDE"], row["LONGITUDE"]], popup=row["CODIGO_NATUREZA_PRINCIPAL"]).add_to(mapa)
    folium_static(mapa)

# Página 2 e Página 3 seguem a mesma lógica de dinamicidade
