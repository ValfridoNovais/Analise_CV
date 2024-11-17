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

# CSS para ajustar a tabela e caixas de entrada dinâmicas
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
    .correct-input {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.25rem;
        font-size: 1rem;
        width: 100%;
        border-radius: 4px;
        text-align: center;
    }
    .incorrect-input {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 0.25rem;
        font-size: 1rem;
        width: 100%;
        border-radius: 4px;
        text-align: center;
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
    return "VERDE" if abs(valor_calculado - valor_digitado) < 0.01 else "VERMELHO"

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

        # Cálculos do IMV ou IMT
        with st.expander("Cálculos do Indicador", expanded=True):
            for i, row in enumerate(rows):
                valor_calculado = truncar((df.loc[row, menu] / populacao) * 100000, 2)
                resposta_digitada = st.number_input(
                    f"{menu} {row}:",
                    min_value=0.0,
                    format="%.2f",
                    step=0.01,
                    key=f"resposta_{row}"
                )
                status = verificar_resposta(valor_calculado, resposta_digitada)

                # Exibir valor com cor dinâmica
                input_class = "correct-input" if status == "VERDE" else "incorrect-input"
                st.markdown(
                    f"<div class='{input_class}'>{resposta_digitada:.2f}</div>",
                    unsafe_allow_html=True,
                )

        # Cálculo da variação
        with st.expander("Cálculo da Variação", expanded=True):
            try:
                # Verifica se os valores de 2022 e 2023 são válidos
                if df.loc["2022", menu] > 0 and df.loc["2023", menu] > 0:
                    # Calcula a variação entre 2023 e 2022 com truncamento
                    variacao_calculada = truncar(((df.loc["2023", menu] - df.loc["2022", menu]) / df.loc["2022", menu]) * 100, 2)

                    # Mostra a fórmula
                    st.markdown("### Fórmula da Variação")
                    st.latex(r"\text{Variação} = \frac{\text{2023} - \text{2022}}{\text{2022}} \times 100")

                    # Campo para o aluno inserir a variação calculada
                    variacao_digitada = st.number_input(
                        "Digite a Variação Calculada (com 2 casas decimais):",
                        min_value=-100.0,
                        max_value=100.0,
                        format="%.2f",
                        step=0.01
                    )

                    # Verifica a resposta
                    if abs(variacao_calculada - variacao_digitada) < 0.01:
                        st.markdown(
                            f"<span style='color:green;font-weight:bold;'>Status: CORRETO ✅</span>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f"<span style='color:red;font-weight:bold;'>Status: INCORRETO ❌</span>",
                            unsafe_allow_html=True
                        )
                else:
                    st.warning(
                        "Os valores para 2022 e 2023 são 0 ou inválidos. Por favor, preencha os dados da tabela antes de calcular a variação."
                    )
            except KeyError as e:
                st.error(f"Erro no cálculo da variação: {e}. Verifique os dados da tabela.")
            except Exception as e:
                st.error(f"Erro inesperado: {e}")

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
