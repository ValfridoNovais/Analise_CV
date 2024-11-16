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
@st.cache_data  # Atualizado para usar st.cache_data
def carregar_dados(arquivo):
    df = pd.read_csv(arquivo, delimiter=';')
    
    # Verifica se as colunas necessárias estão presentes
    colunas_necessarias = {"LATITUDE", "LONGITUDE", "DATA_FATO", "CODIGO_NATUREZA_PRINCIPAL", "SETOR", "UNID_REGISTRO_NIVEL_6"}
    if not colunas_necessarias.issubset(df.columns):
        st.error("O arquivo CSV deve conter as colunas necessárias: LATITUDE, LONGITUDE, DATA_FATO, CODIGO_NATUREZA_PRINCIPAL, SETOR e UNID_REGISTRO_NIVEL_6.")
        return None
    
    # Filtra apenas os crimes violentos
    naturezas_crimes_violentos = {"B01121", "B02001", "B01148", "C01157", "C01158", "D01213", "D01217", "C01159"}
    df = df[df["CODIGO_NATUREZA_PRINCIPAL"].isin(naturezas_crimes_violentos)]
    
    # Converte DATA_FATO para datetime
    df["DATA_FATO"] = pd.to_datetime(df["DATA_FATO"], format="%d/%m/%Y", errors="coerce")
    
    # Limpa e converte LATITUDE e LONGITUDE para valores numéricos
    df["LATITUDE"] = pd.to_numeric(df["LATITUDE"].str.replace(",", ".", regex=False), errors="coerce")
    df["LONGITUDE"] = pd.to_numeric(df["LONGITUDE"].str.replace(",", ".", regex=False), errors="coerce")
    
    # Remove linhas com valores inválidos
    df = df.dropna(subset=["LATITUDE", "LONGITUDE", "DATA_FATO"])
    
    return df

# Layout principal
st.sidebar.title("Navegação")
pagina = st.sidebar.radio("Escolha uma página", ["Introdução", "Análise por Local", "Análise por Tempo", "Análise por Tipo de Crime"])

# Upload de arquivo
st.sidebar.title("Upload de Arquivo")
arquivo = st.sidebar.file_uploader("Faça upload do arquivo CSV", type=["csv"])
dados = carregar_dados(arquivo) if arquivo else None

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

# Filtros globais
if dados is not None:
    setores = st.sidebar.multiselect("Selecione Setores", options=["Todos"] + dados["SETOR"].dropna().unique().tolist(), default="Todos")
    unidades = st.sidebar.multiselect("Selecione Unidades (UNID_REGISTRO_NIVEL_6)", options=["Todos"] + dados["UNID_REGISTRO_NIVEL_6"].dropna().unique().tolist(), default="Todos")
    
    # Aplica os filtros
    if "Todos" not in setores:
        dados = dados[dados["SETOR"].isin(setores)]
    if "Todos" not in unidades:
        dados = dados[dados["UNID_REGISTRO_NIVEL_6"].isin(unidades)]

# Página 1: Análise por Local
if pagina == "Análise por Local" and dados is not None:
    st.title("Análise por Local")
    
    st.subheader("Gráfico de Barras: Crimes por Região")
    barra_local = dados["SETOR"].value_counts().reset_index(name="QUANTIDADE")
    barra_local.rename(columns={"index": "SETOR"}, inplace=True)  # Renomeia a coluna index para SETOR
    fig_barra = px.bar(barra_local, x="SETOR", y="QUANTIDADE", labels={"SETOR": "Setor", "QUANTIDADE": "Quantidade"})
    st.plotly_chart(fig_barra)
    
    st.subheader("Gráfico de Pizza: Distribuição de Crimes por Setor")
    fig_pizza = px.pie(barra_local, names="SETOR", values="QUANTIDADE")
    st.plotly_chart(fig_pizza)
    
    st.subheader("Mapa Interativo")
    mapa = folium.Map(location=[dados["LATITUDE"].mean(), dados["LONGITUDE"].mean()], zoom_start=12)
    for _, row in dados.iterrows():
        folium.Marker([row["LATITUDE"], row["LONGITUDE"]], popup=row["CODIGO_NATUREZA_PRINCIPAL"]).add_to(mapa)
    folium_static(mapa)

# Página 2: Análise por Tempo
if pagina == "Análise por Tempo" and dados is not None:
    st.title("Análise por Tempo")
    
    st.subheader("Gráfico de Barras: Crimes por Mês")
    barra_tempo = dados["MES_DESCRICAO"].value_counts().reset_index(name="QUANTIDADE")
    barra_tempo.rename(columns={"index": "MES_DESCRICAO"}, inplace=True)
    fig_barra_tempo = px.bar(barra_tempo, x="MES_DESCRICAO", y="QUANTIDADE", labels={"MES_DESCRICAO": "Mês", "QUANTIDADE": "Quantidade"})
    st.plotly_chart(fig_barra_tempo)
    
    st.subheader("Gráfico de Linha: Evolução dos Crimes")
    evolucao_tempo = dados.groupby(dados["DATA_FATO"].dt.date).size().reset_index(name="QUANTIDADE")
    evolucao_tempo.rename(columns={"DATA_FATO": "DATA"}, inplace=True)
    fig_linha_tempo = px.line(evolucao_tempo, x="DATA", y="QUANTIDADE", labels={"DATA": "Data", "QUANTIDADE": "Crimes"})
    st.plotly_chart(fig_linha_tempo)

# Página 3: Análise por Tipo de Crime
if pagina == "Análise por Tipo de Crime" and dados is not None:
    st.title("Análise por Tipo de Crime")
    
    st.subheader("Gráfico de Barras: Ocorrências por Tipo de Crime")
    barra_tipo = dados["CODIGO_NATUREZA_PRINCIPAL"].value_counts().reset_index(name="QUANTIDADE")
    barra_tipo.rename(columns={"index": "CODIGO_NATUREZA_PRINCIPAL"}, inplace=True)
    fig_barra_tipo = px.bar(barra_tipo, x="CODIGO_NATUREZA_PRINCIPAL", y="QUANTIDADE", labels={"CODIGO_NATUREZA_PRINCIPAL": "Tipo de Crime", "QUANTIDADE": "Quantidade"})
    st.plotly_chart(fig_barra_tipo)
    
    st.subheader("Gráfico de Pizza: Distribuição por Tipo de Crime")
    fig_pizza_tipo = px.pie(barra_tipo, names="CODIGO_NATUREZA_PRINCIPAL", values="QUANTIDADE")
    st.plotly_chart(fig_pizza_tipo)
    
    st.subheader("Mapa Interativo")
    mapa_tipo = folium.Map(location=[dados["LATITUDE"].mean(), dados["LONGITUDE"].mean()], zoom_start=12)
    for _, row in dados.iterrows():
        folium.Marker([row["LATITUDE"], row["LONGITUDE"]], popup=row["CODIGO_NATUREZA_PRINCIPAL"]).add_to(mapa_tipo)
    folium_static(mapa_tipo)

# Mensagem caso não tenha dados carregados
if dados is None and pagina != "Introdução":
    st.warning("Por favor, faça o upload de um arquivo CSV para visualizar as análises.")
