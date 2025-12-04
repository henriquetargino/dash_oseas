from ctypes import alignment
from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from app import *

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash_bootstrap_templates import template_from_url
import os

from graph_api import *


# =========  Data Ingestion  =========== #
fb_api = os.environ.get("FB_ACCESS_TOKEN")
ad_acc = os.environ.get("FB_AD_ACCOUNT_ID")

fb_api = GraphAPI(ad_acc, fb_api)

campaign_insights = pd.DataFrame(fb_api.get_insights(ad_acc)["data"])
adset_status = pd.DataFrame(fb_api.get_adset_status(ad_acc)["data"])
adset_insights = pd.DataFrame(fb_api.get_insights(ad_acc, "adset")["data"])
ads_insights = pd.DataFrame(fb_api.get_insights(ad_acc, "ad")["data"])


# =========  Layout  =========== #
layout = html.Div([
            dbc.Row([
                html.H3("Selecione o conjunto de anúncio:", style={"margin-top": "50px"}),
                dcc.Dropdown(
                    options=[{"label": i, "value": i} for i in adset_insights.adset_name.values],
                    value=adset_insights.adset_name.values[0],
                    id='dd-adset'),
                ], style={"margin-bottom": "30px"}),

            dbc.Row([
                dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Status"),
                            dbc.CardBody([
                                dbc.Button("", id="btn-adset-status"),
                            ], id="cb-status-adset", className="d-flex align-items-center justify-content-center")
                        ], color="light", className="h-100"),

                    ], width="auto"),

                dbc.Col([
                    dbc.Card([
                            dbc.CardHeader("Clicks"),
                            dbc.CardBody([
                                html.H4("", id="adset-clicks", className="data-value"),
                            ])
                        ], color="light", className="h-100"),

                    ], width="auto"),

                dbc.Col([
                    dbc.Card([
                            dbc.CardHeader("Spend"),
                            dbc.CardBody([
                                html.H4("", id="adset-spend", className="data-value"),
                            ])
                        ], color="light", className="h-100"),
                    ], width="auto"),
                
                dbc.Col([
                    dbc.Card([
                            dbc.CardHeader("Conversion"),
                            dbc.CardBody([
                                html.H5("", id="adset-conversions", className="data-value"),
                            ])
                        ], color="light", className="h-100"),
                    ], width="auto"),
            ], style={"margin-bottom": "20px"}),

            dbc.Row([
                dbc.Col([
                    html.H4("Selecione o indicador:"),
                    dcc.RadioItems(options=['Spend', 'CPC', 'CPM', 'Clicks', 'Conversion'], 
                                value='Conversion', id='adset-kind', 
                                inputStyle={"margin-right": "5px", "margin-left": "20px"}),
                ], md=6),
                
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
                        value='maximum', 
                        id='dd-date-preset-adset',
                        clearable=False
                    ),
                ], md=6),
            ], style={"margin-top": "50px"}),

            dbc.Row([            
                dbc.Col(dcc.Graph(id="graph-line-adset"), md=6),
                dbc.Col(dcc.Graph(id="graph-bar-adset"), md=6)
                ], style={"margin-top": "20px"}),
            ]) 

#========== Callbacks ================
@app.callback([
                Output("cb-status-adset", "children"),
                Output("adset-clicks", "children"),
                Output("adset-spend", "children"),
                Output("adset-conversions", "children"),
            ], 
                [Input("dd-adset", "value"),
                 Input("dd-date-preset-adset", "value")])
def render_page_content(adset, date_preset):
    status_row = adset_status[adset_status["name"] == adset]
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

    adset_id_row = adset_insights[adset_insights["adset_name"] == adset]
    if not adset_id_row.empty:
        adset_id = adset_id_row["adset_id"].values[0]
    else:
        return status_btn, "0", "R$ 0.00", "0"

    data_over_time = fb_api.get_data_over_time(adset_id, date_preset)
    df_temp = pd.DataFrame(data_over_time["data"])
    
    if df_temp.empty:
        return status_btn, "0", "R$ 0.00", "0"

    # --- VACINA 2: Garante colunas ---
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
                Output("graph-line-adset", "figure"),
                Output("graph-bar-adset", "figure"),
            ], 
                [Input("dd-adset", "value"),
                Input("adset-kind", "value"),
                Input("dd-date-preset-adset", "value")]
            )
def render_page_content(adset, adset_kind, date_preset):
    adset_id_row = adset_insights[adset_insights["adset_name"] == adset]
    if not adset_id_row.empty:
        adset_id = adset_id_row["adset_id"].values[0]
    else:
        return go.Figure(), go.Figure()

    adset_kind = adset_kind.lower()   
    data_over_time = fb_api.get_data_over_time(adset_id, date_preset)
    df_data = pd.DataFrame(data_over_time["data"])
    
    if df_data.empty:
        layout_vazio = go.Layout(template="plotly_dark", xaxis={"visible": False}, yaxis={"visible": False},
            annotations=[{"text": "Sem dados", "xref": "paper", "yref": "paper", "showarrow": False, "font": {"size": 20}}])
        return go.Figure(layout=layout_vazio), go.Figure(layout=layout_vazio)
    
    # --- VACINA 2 ---
    for col in ["clicks", "spend", "conversion", "impressions"]:
        if col not in df_data.columns:
            df_data[col] = 0
    # ----------------
        
    df_data["clicks"] = df_data["clicks"].astype(float)
    df_data["spend"] = df_data["spend"].astype(float)
    df_data["impressions"] = df_data["impressions"].astype(float)

    with np.errstate(divide='ignore', invalid='ignore'):
        df_data["cpc"] = np.where(df_data["clicks"]!=0, df_data["spend"] / df_data["clicks"], 0)
        df_data["cpm"] = np.where(df_data["impressions"]!=0, (df_data["spend"] / df_data["impressions"]) * 1000, 0)
    
    df_data = df_data.fillna(0)
    
    fig_line = px.line(df_data, x="date_start", y=adset_kind, template="plotly_dark")
    if adset_kind in ["spend", "cpc", "cpm"]:
        fig_line.update_layout(yaxis=dict(tickformat="R$.2f"))
    fig_line.update_layout(margin=go.layout.Margin(l=0, r=0, t=0, b=0))
    
    df_adset = ads_insights[ads_insights["adset_name"]== adset].copy()
    
    # --- VACINA PARA BARRAS ---
    for col in ["clicks", "spend", "conversion", "impressions"]:
        if col not in df_adset.columns:
            df_adset[col] = 0

    df_adset["clicks"] = df_adset["clicks"].astype(float)
    df_adset["spend"] = df_adset["spend"].astype(float)
    df_adset["impressions"] = df_adset["impressions"].astype(float)

    with np.errstate(divide='ignore', invalid='ignore'):
        df_adset["cpc"] = np.where(df_adset["clicks"]!=0, df_adset["spend"] / df_adset["clicks"], 0)
        df_adset["cpm"] = np.where(df_adset["impressions"]!=0, (df_adset["spend"] / df_adset["impressions"]) * 1000, 0)

    df_adset = df_adset.fillna(0)

    fig_adsets = px.bar(df_adset, y=adset_kind, x="ad_name", template="plotly_dark")
    if adset_kind in ["spend", "cpc", "cpm"]:
        fig_adsets.update_layout(yaxis=dict(tickformat="R$.2f"))

    fig_adsets.update_layout(margin=go.layout.Margin(l=0, r=0, t=0, b=0))
    return fig_line, fig_adsets