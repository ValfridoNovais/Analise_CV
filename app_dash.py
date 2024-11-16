from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px
import folium
from dash import Dash
import dash_bootstrap_components as dbc
import io
import base64  # Corrigido: Importação adicionada

# Inicializar o app Dash
app = DashProxy(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Função para carregar e validar dados
def carregar_dados_conteudo(conteudo):
    # Decodificar o conteúdo do arquivo
    content_type, content_string = conteudo.split(',')
    decoded = io.StringIO(io.BytesIO(base64.b64decode(content_string)).read().decode('utf-8'))
    df = pd.read_csv(decoded, delimiter=';')

    colunas_necessarias = {"LATITUDE", "LONGITUDE", "DATA_FATO", "CODIGO_NATUREZA_PRINCIPAL", "SETOR", "UNID_REGISTRO_NIVEL_6"}
    if not colunas_necessarias.issubset(df.columns):
        raise ValueError("O arquivo CSV deve conter as colunas necessárias.")
    
    # Filtros de crimes violentos
    naturezas_crimes_violentos = {"B01121", "B02001", "B01148", "C01157", "C01158", "D01213", "D01217", "C01159"}
    df = df[df["CODIGO_NATUREZA_PRINCIPAL"].isin(naturezas_crimes_violentos)]
    
    # Conversões e limpeza
    df["DATA_FATO"] = pd.to_datetime(df["DATA_FATO"], format="%d/%m/%Y", errors="coerce")
    df["LATITUDE"] = pd.to_numeric(df["LATITUDE"].str.replace(",", ".", regex=False), errors="coerce")
    df["LONGITUDE"] = pd.to_numeric(df["LONGITUDE"].str.replace(",", ".", regex=False), errors="coerce")
    df = df.dropna(subset=["LATITUDE", "LONGITUDE", "DATA_FATO"])
    return df

# Layout do aplicativo
app.layout = html.Div([
    html.H1("Análise de Crimes Violentos", style={"textAlign": "center"}),

    # Componente para upload do arquivo
    html.Div([
        html.Label("Faça upload do arquivo CSV:"),
        dcc.Upload(
            id="upload-dados",
            children=html.Button("Carregar Arquivo"),
            multiple=False
        ),
        html.Div(id="mensagem-upload", style={"color": "red"})
    ], style={"padding": "10px"}),

    # Dropdowns para filtros
    html.Div([
        html.Label("Selecione o Setor:"),
        dcc.Dropdown(id="filtro-setor", multi=False),
        html.Label("Selecione a Unidade:"),
        dcc.Dropdown(id="filtro-unidade", multi=False),
    ], style={"padding": "10px"}),

    # Gráficos
    html.Div([
        dcc.Graph(id="grafico-barras"),
        dcc.Graph(id="grafico-pizza"),
    ]),

    # Mapa interativo
    html.Div(id="mapa-interativo", style={"height": "500px"}),
])

# Callbacks para carregar dados do arquivo e atualizar opções dos filtros
@app.callback(
    [Output("filtro-setor", "options"),
     Output("filtro-unidade", "options"),
     Output("mensagem-upload", "children")],
    [Input("upload-dados", "contents")],
    [State("upload-dados", "filename")]
)
def carregar_dados(contents, filename):
    if contents is None:
        return [], [], "Nenhum arquivo carregado."
    
    try:
        df = carregar_dados_conteudo(contents)
        setores = [{"label": s, "value": s} for s in sorted(df["SETOR"].unique())]
        unidades = [{"label": u, "value": u} for u in sorted(df["UNID_REGISTRO_NIVEL_6"].unique())]
        return setores, unidades, f"Arquivo {filename} carregado com sucesso!"
    except Exception as e:
        return [], [], f"Erro ao carregar o arquivo: {str(e)}"

# Callbacks para atualizar gráficos e mapa
@app.callback(
    [Output("grafico-barras", "figure"),
     Output("grafico-pizza", "figure"),
     Output("mapa-interativo", "children")],
    [Input("filtro-setor", "value"),
     Input("filtro-unidade", "value"),
     Input("upload-dados", "contents")],
    [State("upload-dados", "filename")]
)
def atualizar_graficos(setor, unidade, contents, filename):
    if contents is None:
        return {}, {}, "Nenhum arquivo carregado para visualização."
    
    try:
        df_filtrado = carregar_dados_conteudo(contents)
        if setor:
            df_filtrado = df_filtrado[df_filtrado["SETOR"] == setor]
        if unidade:
            df_filtrado = df_filtrado[df_filtrado["UNID_REGISTRO_NIVEL_6"] == unidade]
        
        # Gráfico de Barras
        barra_local = df_filtrado["SETOR"].value_counts().reset_index(name="QUANTIDADE")
        barra_local.rename(columns={"index": "SETOR"}, inplace=True)
        fig_barras = px.bar(barra_local, x="SETOR", y="QUANTIDADE", labels={"SETOR": "Setor", "QUANTIDADE": "Quantidade"})
        
        # Gráfico de Pizza
        fig_pizza = px.pie(barra_local, names="SETOR", values="QUANTIDADE")
        
        # Mapa interativo
        mapa = folium.Map(location=[df_filtrado["LATITUDE"].mean(), df_filtrado["LONGITUDE"].mean()], zoom_start=12)
        for _, row in df_filtrado.iterrows():
            folium.Marker([row["LATITUDE"], row["LONGITUDE"]], popup=row["CODIGO_NATUREZA_PRINCIPAL"]).add_to(mapa)
        mapa_html = folium_static(mapa)._repr_html_()
        
        return fig_barras, fig_pizza, html.Iframe(srcDoc=mapa_html, width="100%", height="500px")
    except Exception as e:
        return {}, {}, f"Erro ao processar os dados: {str(e)}"

# Rodar o aplicativo
if __name__ == "__main__":
    app.run_server(debug=True)
