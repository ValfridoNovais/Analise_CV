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
# Adicionando uma imagem no sidebar
st.sidebar.image(
    "C:/Repositorios_GitHube/MeusProjetos/Analise_CV/APM2.png", 
    caption="Logo da Análise CV",  # Legenda opcional
    use_column_width=True  # Ajusta automaticamente à largura do sidebar
)

st.sidebar.title("Menu de Indicadores")
st.sidebar.markdown("# Menu de Indicadores")
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

# Layout principal para IMV e IMT
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
        

        # Cálculos do IMV ou IMT
        with st.expander("Cálculos do Indicador", expanded=True):
            st.markdown("### Fórmula")
            st.latex(rf"{menu} = \frac{{\text{{{menu}}}}}{{\text{{POP}}}} \times 100.000")
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

if menu == "ICCP":
    # Título e instruções
    st.title("Tabela de ICCP")
    st.markdown("**Formatação da tabela:**")
    st.markdown("- **Linhas:** Natureza (FURTO, ROUBO, EXTORSÃO)")
    st.markdown("- **Colunas:** Anos (2021, 2022, 2023)")

    # Divisão da página
    col1, col2 = st.columns([1, 1])  # Divisão da página em duas colunas

    # Coluna 1: Entrada de População e Tabela de Valores
    with col1:
        # Entrada de População
        populacao = st.number_input("Digite o valor da População (POP):", min_value=1, step=1, value=344355)

        st.markdown("### Tabela de Valores")

        # Configuração da tabela
        rows = ["FURTO", "ROUBO", "EXTORSÃO"]
        cols = ["2021", "2022", "2023"]

        # Inicializar estado da sessão
        if f"valores_ICCP" not in st.session_state:
            st.session_state["valores_ICCP"] = None  # Inicializa como None para indicar que a tabela ainda não foi gerada

        # Botão para gerar valores automáticos
        if st.button("Gerar Tabela"):
            valores = []
            for row in rows:
                if row == "FURTO":
                    valores.append([random.randint(1012, 2015) for _ in range(len(cols))])
                elif row == "ROUBO":
                    valores.append([random.randint(80, 300) for _ in range(len(cols))])
                elif row == "EXTORSÃO":
                    valores.append([random.randint(5, 30) for _ in range(len(cols))])
            st.session_state["valores_ICCP"] = valores

        # Verificar se a tabela foi gerada
        if st.session_state["valores_ICCP"] is not None:
            # Recuperar valores da tabela
            valores = st.session_state["valores_ICCP"]

            # Criar DataFrame
            df_iccp = pd.DataFrame(valores, index=rows, columns=cols)

            # Exibir a tabela
            st.markdown(df_iccp.to_html(classes="custom-table", index=True, escape=False), unsafe_allow_html=True)

    # Coluna 2: Cálculos e Fórmulas
    with col2:
        # Verificar se a tabela foi gerada
        if st.session_state["valores_ICCP"] is not None:
            st.markdown("### Cálculos e Fórmulas")

            # Cálculo do Fator FURTO/ROUBO
            with st.expander("Cálculos do fator (F ∝ R)", expanded=True):
                st.markdown("#### Cálculo do Fator F ∝ R")
                fatores = {}
                for ano_atual, ano_anterior in [("2022", "2021"), ("2023", "2022")]:
                    try:
                        furto = df_iccp.loc["FURTO", ano_anterior]
                        roubo = df_iccp.loc["ROUBO", ano_anterior]

                        if roubo > 0:
                            fator_calculado = truncar(furto / roubo, 2)
                            fatores[ano_atual] = fator_calculado
                            fator_digitado = st.number_input(
                                f"Digite o F ∝ R para {ano_atual} (baseado em {ano_anterior}):",
                                min_value=0.0,
                                format="%.2f",
                                step=0.01,
                                key=f"fator_{ano_atual}"
                            )
                            status_fator = verificar_resposta(fator_calculado, fator_digitado)
                            input_class = "correct-input" if status_fator == "VERDE" else "incorrect-input"
                            st.markdown(f"<div class='{input_class}'>{fator_digitado:.2f}</div>", unsafe_allow_html=True)
                        else:
                            st.warning(f"O valor de ROUBO em {ano_anterior} é zero. Não é possível calcular o fator para {ano_atual}.")
                    except KeyError:
                        st.error("Os valores necessários para o cálculo do fator não estão preenchidos.")
                    except Exception as e:
                        st.error(f"Erro ao calcular o Fator F ∝ R: {e}")

            # Fórmula do ICCP
            with st.expander("Cálculos do ICCP", expanded=True):
                st.markdown("#### Fórmula do ICCP")
                st.latex(r"""
                    \text{ICCP} = \frac{{(\text{ROUBO} \cdot \text{F ∝ R}) + (\text{EXTORSÃO} \cdot \text{F ∝ R}) + \text{FURTO}}}{{\text{POP}}} \times 100
                """)

                # Cálculo do ICCP
                for ano_atual, ano_anterior in [("2022", "2021"), ("2023", "2022")]:
                    try:
                        if ano_atual in fatores:
                            fator = fatores[ano_atual]
                            furto = df_iccp.loc["FURTO", ano_atual]
                            roubo = df_iccp.loc["ROUBO", ano_atual]
                            extorsao = df_iccp.loc["EXTORSÃO", ano_atual]

                            iccp_calculado = truncar(((roubo * fator) + (extorsao * fator) + furto) / populacao * 100, 2)
                            iccp_digitado = st.number_input(
                                f"Digite o ICCP Calculado para {ano_atual}:",
                                min_value=0.0,
                                format="%.2f",
                                step=0.01,
                                key=f"iccp_{ano_atual}"
                            )
                            status_iccp = verificar_resposta(iccp_calculado, iccp_digitado)
                            input_class = "correct-input" if status_iccp == "VERDE" else "incorrect-input"
                            st.markdown(f"<div class='{input_class}'>{iccp_digitado:.2f}</div>", unsafe_allow_html=True)
                    except KeyError:
                        st.error("Os valores necessários para o cálculo do ICCP não estão preenchidos.")
                    except Exception as e:
                        st.error(f"Erro ao calcular o ICCP: {e}")

            # Cálculo da Variação
            with st.expander("Cálculo da Variação", expanded=True):
                try:
                    furto_2022 = df_iccp.loc["FURTO", "2022"]
                    furto_2023 = df_iccp.loc["FURTO", "2023"]

                    variacao_calculada = truncar(((furto_2023 - furto_2022) / furto_2022) * 100, 2)
                    variacao_digitada = st.number_input(
                        "Digite a variação calculada de FURTO (com 2 casas decimais):",
                        min_value=-100.0,
                        max_value=100.0,
                        format="%.2f",
                        step=0.01
                    )
                    status_variacao = verificar_resposta(variacao_calculada, variacao_digitada)
                    input_class = "correct-input" if status_variacao == "VERDE" else "incorrect-input"
                    st.markdown(f"<div class='{input_class}'>{variacao_digitada:.2f}</div>", unsafe_allow_html=True)
                except KeyError:
                    st.error("Os valores necessários para calcular a variação estão zerados ou inválidos.")
                except Exception as e:
                    st.error(f"Erro ao calcular a variação: {e}")
        else:
            st.warning("Por favor, gere a tabela antes de realizar cálculos.")
