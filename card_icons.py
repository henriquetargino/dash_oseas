from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from pyrsistent import b
from app import *
import pandas as pd
from graph_api import *
import os
# FONT_AWESOME = "https://use.fontawesome.com/releases/v5.10.2/css/all.css"
# dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.1/dbc.min.css")

# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY, FONT_AWESOME, dbc_css],
#         suppress_callback_exceptions=True)



# =========  Data Ingestion  =========== #
fb_api = os.environ.get("FB_ACCESS_TOKEN")
ad_acc = os.environ.get("FB_AD_ACCOUNT_ID")

fb_api = GraphAPI(ad_acc, fb_api)

campaign_insights = pd.DataFrame(fb_api.get_campaign_insights(ad_acc)["data"])
campaign_status = pd.DataFrame(fb_api.get_campaigns_status(ad_acc)["data"])
first_campaign_id = campaign_insights["campaign_id"][0]
data_over_time = fb_api.get_data_over_time(first_campaign_id)["data"]


card_icon = {
    "color": "white",
    "textAlign": "center",
    "fontSize": 30,
    "margin": "auto",
}

# =========  Layout  =========== #
layout = dbc.Container([
            dbc.Row([
                html.H3("Selecione a campanha:", style={"margin-top": "50px"}),
                dcc.Dropdown(
                    options=[{"label": i, "value": i} for i in campaign_insights.campaign_name.values],
                    id='dd-campaign', style={"margin-bottom": "20px"}),
                # html.Hr(),
            ]),

            dbc.Row([
                dbc.Col([
                    dbc.CardGroup([
                            dbc.Card([
                                    html.H5("Status"),
                                    html.P("", id="p-campaign-status", className="card-text"),
                            ]),
                            dbc.Card(
                                html.Div(className="fa fa-list", style=card_icon), 
                                color="primary",
                                style={"maxWidth": 75, "height": 100},
                            )])
                    ]),

                dbc.Col([
                    dbc.CardGroup([
                            dbc.Card([
                                    html.H5("Card 1"),
                                    html.P("This card has some text content", className="card-text")]
                            ),
                            dbc.Card(
                                html.Div(className="fa fa-list", style=card_icon), 
                                color="info",
                                style={"maxWidth": 75})
                            ])
                    ]),

                dbc.Col([
                    dbc.CardGroup([
                            dbc.Card([
                                    html.H5("Card 1"),
                                    html.P("This card has some text content")
                                ]),
                            dbc.Card(
                                html.Div(className="fa fa-list", style=card_icon), 
                                color="secondary",
                                style={"maxWidth": 75},
                            )])
                    ]),
            ]),

            dbc.Row([
                dbc.Col([
                        dcc.Graph(id="graph-line-campaign")
                ], md=9),

                dbc.Col([
                    dcc.Graph(id="graph-bar-campaign")
                ], md=3)
            ])
        ]) 

# ========== Components ================
@app.callback(Output("p-campaign-status", "children"), 
                [Input("dd-campaign", "value")])
def render_page_content(value):
    return campaign_status[campaign_status["name"] == value]["status"]