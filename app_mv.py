import streamlit as st
import pandas as pd
import random

# Configuração inicial
st.set_page_config(page_title="Indicadores de Criminalidade", layout="wide")

# Ocultar menu e rodapé do Streamlit
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# CSS para tabelas responsivas
responsive_table_style = """
    <style>
    .responsive-table {
        margin: auto;
        border-collapse: collapse;
        width: auto;
        max-width: 100%;
        table-layout: fixed;
    }
    .responsive-table th, .responsive-table td {
        border: 1px solid #ddd;
        text-align: center;
        padding: 8px;
        width: 26mm; /* Largura inicial fixa */
    }
    .responsive-table th {
        background-color: #f2f2f2;
    }
    </style>
"""
st.markdown(responsive_table_style, unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Menu de Indicadores")
menu = st.sidebar.selectbox(
    "Escolha o Indicador:",
    ["Selecione", "IMV", "ICCP", "IMT"]
)

# Função para gerar valores automaticamente
def gerar_valores_automaticos(min_val, max_val, rows, cols):
    return [[random.randint(min_val, max_val) for _ in range(len(cols))] for _ in range(len(rows))]

# Função para exibir tabelas responsivas
def exibir_tabela_responsiva(dataframe):
    html_table = dataframe.to_html(
        classes="responsive-table", 
        index=True, 
        justify="center", 
        escape=False
    )
    st.markdown(html_table, unsafe_allow_html=True)

# Tabela de IMV
if menu == "IMV":
    st.title("Tabela de IMV")
    st.markdown("**Formatação da tabela:**")
    st.markdown("- Linhas: Anos (2022, 2023)")
    st.markdown("- Colunas: MV")

    # Seleção de preenchimento
    escolha = st.radio(
        "Como deseja preencher os valores?",
        ["Manual", "Gerar Automaticamente"]
    )

    rows = ["2022", "2023"]
    cols = ["MV"]

    if escolha == "Manual":
        # Entrada manual de dados
        valores = []
        for row in rows:
            row_valores = []
            for col in cols:
                valor = st.number_input(f"Digite o valor para {col} no ano {row}:", min_value=0, step=1)
                row_valores.append(valor)
            valores.append(row_valores)
    else:
        # Geração automática de valores
        valores = gerar_valores_automaticos(50, 80, rows, cols)

    # Criar DataFrame
    df_imv = pd.DataFrame(valores, index=rows, columns=cols)
    exibir_tabela_responsiva(df_imv)

# Tabela de ICCP
elif menu == "ICCP":
    st.title("Tabela de ICCP")
    st.markdown("**Formatação da tabela:**")
    st.markdown("- Linhas: Natureza (Furto, Roubo, Extorsão)")
    st.markdown("- Colunas: Anos (2021, 2022, 2023)")

    # Seleção de preenchimento
    escolha = st.radio(
        "Como deseja preencher os valores?",
        ["Manual", "Gerar Automaticamente"]
    )

    rows = ["FURTO", "ROUBO", "EXTORSÃO"]
    cols = ["2021", "2022", "2023"]

    if escolha == "Manual":
        # Entrada manual de dados
        valores = []
        for row in rows:
            row_valores = []
            for col in cols:
                valor = st.number_input(f"Digite o valor para {row} no ano {col}:", min_value=0, step=1)
                row_valores.append(valor)
            valores.append(row_valores)
    else:
        # Geração automática de valores
        valores = []
        for row in rows:
            if row == "FURTO":
                valores.append([random.randint(1012, 2015) for _ in range(len(cols))])
            elif row == "ROUBO":
                valores.append([random.randint(80, 300) for _ in range(len(cols))])
            elif row == "EXTORSÃO":
                valores.append([random.randint(5, 30) for _ in range(len(cols))])

    # Criar DataFrame
    df_iccp = pd.DataFrame(valores, index=rows, columns=cols)
    exibir_tabela_responsiva(df_iccp)

# Tabela de IMT
elif menu == "IMT":
    st.title("Tabela de IMT")
    st.markdown("**Formatação da tabela:**")
    st.markdown("- Linhas: Anos (2022, 2023)")
    st.markdown("- Colunas: MT")

    # Seleção de preenchimento
    escolha = st.radio(
        "Como deseja preencher os valores?",
        ["Manual", "Gerar Automaticamente"]
    )

    rows = ["2022", "2023"]
    cols = ["MT"]

    if escolha == "Manual":
        # Entrada manual de dados
        valores = []
        for row in rows:
            row_valores = []
            for col in cols:
                valor = st.number_input(f"Digite o valor para {col} no ano {row}:", min_value=0, step=1)
                row_valores.append(valor)
            valores.append(row_valores)
    else:
        # Geração automática de valores
        valores = gerar_valores_automaticos(10, 30, rows, cols)

    # Criar DataFrame
    df_imt = pd.DataFrame(valores, index=rows, columns=cols)
    exibir_tabela_responsiva(df_imt)

# Mensagem padrão
else:
    st.write("Selecione um indicador na barra lateral para começar.")
