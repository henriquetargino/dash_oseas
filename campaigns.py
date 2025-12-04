from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from app import *

import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

from graph_api import *


# =========  Data Ingestion  =========== #
fb_api = os.environ.get("FB_ACCESS_TOKEN")
ad_acc = os.environ.get("FB_AD_ACCOUNT_ID")

fb_api = GraphAPI(ad_acc, fb_api)

campaign_insights = pd.DataFrame(fb_api.get_insights(ad_acc)["data"])
adset_insights = pd.DataFrame(fb_api.get_insights(ad_acc, "adset")["data"])
campaign_status = pd.DataFrame(fb_api.get_campaigns_status(ad_acc)["data"])


adset_insights.head(3)
# data_over_time = fb_api.get_data_over_time(23849930731190625)
first_campaign_id = campaign_insights["campaign_id"][0]
data_over_time = fb_api.get_data_over_time(first_campaign_id)["data"]


# =========  Layout  =========== #
layout = html.Div([
            dbc.Row([
                html.H3("Selecione a campanha:", style={"margin-top": "50px"}),
                dcc.Dropdown(
                    options=[{"label": i, "value": i} for i in campaign_insights.campaign_name.values],
                    value=campaign_insights.campaign_name.values[0],
                    id='dd-campaign'),
                ], style={"margin-bottom": "30px"}),

            dbc.Row([
                dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Status"),
                            # Adicionei padding no body para centralizar melhor
                            dbc.CardBody([], id="cb-status", className="d-flex align-items-center justify-content-center")
                        ], color="light", className="h-100"), # h-100 garante altura total
                    ], width="auto"),

                dbc.Col([
                    dbc.Card([
                            dbc.CardHeader("Clicks"),
                            dbc.CardBody([
                                # Troquei o style manual pela classe 'data-value' definida no CSS
                                html.H4("", id="campaign-clicks", className="data-value"),
                            ])
                        ], color="light", className="h-100"),
                    ], width="auto"),

                dbc.Col([
                    dbc.Card([
                            dbc.CardHeader("Spend"),
                            dbc.CardBody([
                                html.H4("", id="campaign-spend", className="data-value"),
                            ])
                        ], color="light", className="h-100"),
                    ], width="auto"),
                
                
                dbc.Col([
                    dbc.Card([
                            dbc.CardHeader("Conversion"),
                            dbc.CardBody([
                                html.H5("", id="campaign-conversions", className="data-value"),
                            ])
                        ], color="light", className="h-100"),
                    ], width="auto"),
            ], style={"margin-bottom": "20px"}), 


            dbc.Row([
                # Coluna da Esquerda: Indicadores
                dbc.Col([
                    html.H4("Selecione o indicador:"),
                    dcc.RadioItems(options=['Spend', 'CPC', 'CPM', 'Clicks', 'Conversion'], 
                                value='Conversion', id='campaign-kind', 
                                inputStyle={"margin-right": "5px", "margin-left": "20px"}),
                ], md=6),
                
                # Coluna da Direita: Período de Tempo (NOVO)
                dbc.Col([
                    html.H4("Selecione o Período:"),
                    dcc.Dropdown(
                        options=[
                            {"label": "Vitalício (Máximo)", "value": "maximum"},
                            {"label": "Hoje", "value": "today"},
                            {"label": "Ontem", "value": "yesterday"},
                            {"label": "Últimos 7 dias", "value": "last_7d"},
                            {"label": "Últimos 14 dias", "value": "last_14d"},
                            {"label": "Últimos 30 dias", "value": "last_30d"},
                            {"label": "Últimos 90 dias", "value": "last_90d"},
                            {"label": "Este Mês", "value": "this_month"},
                            {"label": "Mês Passado", "value": "last_month"},
                        ],
                        value='maximum',  # Valor padrão
                        id='dd-date-preset',
                        clearable=False
                    ),
                ], md=6),
            ], style={"margin-top": "20px"}),

            dbc.Row([            
                dbc.Col(dcc.Graph(id="graph-line-campaign"), md=6),
                dbc.Col(dcc.Graph(id="graph-bar-campaign"), md=6)
                ], style={"margin-top": "20px"}),
            ]) 

#========== Callbacks ================
@app.callback([
                Output("cb-status", "children"),
                Output("campaign-clicks", "children"), 
                Output("campaign-spend", "children"),
                Output("campaign-conversions", "children"),
            ], 
                [Input("dd-campaign", "value"),
                 Input("dd-date-preset", "value")])
def render_page_content(campaign, date_preset):
    # 1. Recupera o Status
    status_row = campaign_status[campaign_status["name"] == campaign]
    if not status_row.empty:
        status_value = status_row["status"].values[0]
    else:
        status_value = "UNKNOWN"
    
    if status_value == "PAUSED":
        status_btn = dbc.Button("PAUSED", color="error", size="sm")
    elif status_value == "ACTIVE": 
        status_btn = dbc.Button("ACTIVE", color="primary", size="sm")
    else:
        status_btn = dbc.Button(status_value, color="secondary", size="sm")

    # 2. Busca os dados
    campaign_id = campaign_status[campaign_status["name"] == campaign]["id"].values[0]
    data_over_time = fb_api.get_data_over_time(campaign_id, date_preset)
    df_temp = pd.DataFrame(data_over_time["data"])
    
    # --- VACINA 1: DataFrame vazio ---
    if df_temp.empty:
        return status_btn, "0", "R$ 0.00", "0"

    # --- VACINA 2: Colunas inexistentes (O ERRO ESTAVA AQUI) ---
    # Garantimos que as colunas existam, preenchendo com 0 se faltarem
    for col in ["clicks", "spend", "conversion"]:
        if col not in df_temp.columns:
            df_temp[col] = 0
    
    clicks_total = df_temp["clicks"].astype(float).sum()
    spend_total = df_temp["spend"].astype(float).sum()
    conversions_total = df_temp["conversion"].astype(float).sum()

    spend_text = "R$ " + "{:,.2f}".format(spend_total).replace(",", "X").replace(".", ",").replace("X", ".")

    clicks_text = "{:,.0f}".format(clicks_total).replace(",", ".")
    conversions_text = "{:,.0f}".format(conversions_total).replace(",", ".")

    return status_btn, clicks_text, spend_text, conversions_text
    

@app.callback([
                Output("graph-line-campaign", "figure"),
                Output("graph-bar-campaign", "figure"),
            ], 
                [Input("dd-campaign", "value"),
                Input("campaign-kind", "value"),
                Input("dd-date-preset", "value")]
            )
def render_page_content(campaign, campaign_kind, date_preset):
    campaign_kind = campaign_kind.lower()
    campaign_id = campaign_status[campaign_status["name"] == campaign]["id"].values[0]
    
    data_over_time = fb_api.get_data_over_time(campaign_id, date_preset)
    df_data = pd.DataFrame(data_over_time["data"])

    # Vacina Gráfico Vazio
    if df_data.empty:
        layout_vazio = go.Layout(template="plotly_dark", xaxis={"visible": False}, yaxis={"visible": False},
            annotations=[{"text": "Sem dados", "xref": "paper", "yref": "paper", "showarrow": False, "font": {"size": 20}}])
        return go.Figure(layout=layout_vazio), go.Figure(layout=layout_vazio)

    # --- VACINA 2: Garante colunas para o gráfico ---
    for col in ["clicks", "spend", "conversion", "impressions"]:
        if col not in df_data.columns:
            df_data[col] = 0
    # ------------------------------------------------

    # Conversão de Tipos
    df_data["clicks"] = df_data["clicks"].astype(float)
    df_data["spend"] = df_data["spend"].astype(float)
    df_data["impressions"] = df_data["impressions"].astype(float)

    # Cálculo Manual (CPC/CPM)
    with np.errstate(divide='ignore', invalid='ignore'):
        df_data["cpc"] = np.where(df_data["clicks"]!=0, df_data["spend"] / df_data["clicks"], 0)
        df_data["cpm"] = np.where(df_data["impressions"]!=0, (df_data["spend"] / df_data["impressions"]) * 1000, 0)

    df_data = df_data.fillna(0)

    # Gráfico de Linha
    fig_line = px.line(df_data, x="date_start", y=campaign_kind, template="plotly_dark")
    if campaign_kind in ["spend", "cpc", "cpm"]:
        fig_line.update_layout(yaxis=dict(tickformat="R$.2f"))
    fig_line.update_layout(margin=go.layout.Margin(l=0, r=0, t=0, b=0))

    # Gráfico de Barras
    df_adset = adset_insights[adset_insights["campaign_name"]== campaign].copy()
    
    # Vacina Colunas Adsets
    for col in ["clicks", "spend", "conversion", "impressions"]:
        if col not in df_adset.columns:
            df_adset[col] = 0

    df_adset["clicks"] = df_adset["clicks"].astype(float)
    df_adset["spend"] = df_adset["spend"].astype(float)
    df_adset["impressions"] = df_adset["impressions"].astype(float)
    
    # Cálculos Adsets
    with np.errstate(divide='ignore', invalid='ignore'):
        df_adset["cpc"] = np.where(df_adset["clicks"]!=0, df_adset["spend"] / df_adset["clicks"], 0)
        df_adset["cpm"] = np.where(df_adset["impressions"]!=0, (df_adset["spend"] / df_adset["impressions"]) * 1000, 0)
    
    df_adset = df_adset.fillna(0)

    fig_adsets = px.bar(df_adset, y=campaign_kind, x="adset_id", template="plotly_dark")
    if campaign_kind in ["spend", "cpc", "cpm"]:
        fig_adsets.update_layout(yaxis=dict(tickformat="R$.2f"))
    fig_adsets.update_layout(margin=go.layout.Margin(l=0, r=0, t=0, b=0))
    
    return fig_line, fig_adsets