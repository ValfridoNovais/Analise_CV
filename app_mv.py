import streamlit as st
import pandas as pd
import random
import math  # Para truncar os valores calculados

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

# Sidebar
st.sidebar.title("Menu de Indicadores")
menu = st.sidebar.selectbox(
    "Escolha o Indicador:",
    ["Selecione", "IMV", "ICCP", "IMT"]
)

# Função para gerar valores automaticamente
def gerar_valores_automaticos(min_val, max_val, rows, cols):
    return [[random.randint(min_val, max_val) for _ in range(len(cols))] for _ in range(len(rows))]

# Função para truncar valores na 2ª casa decimal
def truncar(valor, casas=2):
    fator = 10 ** casas
    return math.trunc(valor * fator) / fator

# Função para verificar resposta
def verificar_resposta(valor_calculado, valor_digitado):
    return "VERDE" if abs(valor_calculado - valor_digitado) < 0.1 else "VERMELHO"

# Layout principal
if menu == "IMV" or menu == "IMT":
    # Instruções
    st.title(f"Tabela de {menu}")
    st.markdown("**Formatação da tabela:**")
    st.markdown("- Linhas: Anos (2022, 2023)")
    st.markdown(f"- Colunas: {menu}")

    # Divisão da página
    col1, col2 = st.columns(2)

    # Definir população
    with col1:
        populacao = st.number_input("Digite o valor da População (POP):", min_value=1, step=1, value=100000)

    # Seleção de preenchimento
    escolha = st.radio(
        "Como deseja preencher os valores?",
        ["Manual", "Gerar Automaticamente"]
    )

    rows = ["2022", "2023"]
    cols = [menu]

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
    df = pd.DataFrame(valores, index=rows, columns=cols)

    # Mostrar tabela
    st.markdown("### Tabela de Valores")
    st.table(df)

    # Exibição de fórmula e cálculos
    with col2:
        st.markdown("### Fórmula")
        st.latex(rf"{menu} = \frac{{\text{{{menu}}}}}{{\text{{POP}}}} \times 100.000")

        st.markdown("### Cálculos")
        for i, row in enumerate(rows):
            valor_calculado = truncar((df.loc[row, menu] / populacao) * 100000, 2)
            resposta_digitada = st.number_input(f"{menu} {row}:", min_value=0.0, format="%.2f", step=1.0, key=f"resposta_{row}")
            status = verificar_resposta(valor_calculado, resposta_digitada)
            st.markdown(f"Status: <span style='color:{status.lower()}'>{status}</span>", unsafe_allow_html=True)
            st.markdown(f"Valor Calculado (truncado): {valor_calculado:.2f}")

# Tabela de ICCP
elif menu == "ICCP":
    st.title("Tabela de ICCP")
    st.markdown("**Formatação da tabela:**")
    st.markdown("- Linhas: Natureza (Furto, Roubo, Extorsão)")
    st.markdown("- Colunas: Anos (2021, 2022, 2023)")

    # Espaço para personalização futura
    st.markdown("**Área de cálculos será implementada posteriormente.**")
else:
    st.write("Selecione um indicador na barra lateral para começar.")
