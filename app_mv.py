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

# CSS para ajustar a tabela
table_style = """
    <style>
    .custom-table {
        margin: auto;
        border-collapse: collapse;
        table-layout: fixed;
        width: 100%; /* Faz com que a tabela ocupe 100% da coluna */
        max-width: 100%; /* Impede que a tabela ultrapasse os limites */
    }
    .custom-table th, .custom-table td {
        border: 1px solid #ddd;
        text-align: center;
        padding: 8px;
        width: 26mm; /* Controla a largura máxima de cada coluna */
    }
    .custom-table th {
        background-color: #f2f2f2;
    }
    </style>
"""
st.markdown(table_style, unsafe_allow_html=True)

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
    col1, col2 = st.columns([1, 1])  # Ajusta as proporções das colunas

    # Definir população
    with col1:
        populacao = st.number_input("Digite o valor da População (POP):", min_value=1, step=1, value=344355)

        # Configuração da tabela
        rows = ["2022", "2023"]
        cols = [menu]

        # Inicializar estado da sessão
        if f"valores_{menu}" not in st.session_state:
            st.session_state[f"valores_{menu}"] = [[0] * len(cols) for _ in range(len(rows))]

        # Botão para gerar ou resetar valores
        if st.button("Gerar Valores"):
            if menu == "IMT":
                 st.session_state[f"valores_{menu}"] = gerar_valores_automaticos(10, 30, rows, cols)
            elif menu == "IMV":
                st.session_state[f"valores_{menu}"] = gerar_valores_automaticos(50, 80, rows, cols)


        # Recuperar os valores da tabela do estado da sessão
        valores = st.session_state[f"valores_{menu}"]

        # Criar DataFrame
        df = pd.DataFrame(valores, index=rows, columns=cols)

        # Mostrar tabela formatada
        st.markdown("### Tabela de Valores")
        st.markdown(df.to_html(classes="custom-table", index=True, escape=False), unsafe_allow_html=True)

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
            #st.markdown(f"Valor Calculado (truncado): {valor_calculado:.2f}")

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
