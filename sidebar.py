from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeChangerAIO
from app import app


style_sidebar = {"box-shadow": "2px 2px 10px 0px rgba(10, 9, 7, 0.10)",
                    "margin": "10px",
                    "padding": "10px",
                    "height": "100vh"}

# =========  Layout  =========== #
layout = dbc.Card(
    [
        html.Div([
            html.Img(src="/assets/logo.jpeg", style={"width": "80%", "height": "auto"})
        ], style={"textAlign": "center", "marginBottom": "10px", "marginTop": "15px"}),
        
        html.Hr(), 
        html.P("Painel de Controle", className="lead", style={"textAlign": "center"}),
        dbc.Nav(
            [
                dbc.NavLink("Campanhas", href="/", active="exact"),
                dbc.NavLink("Conjuntos (Adsets)", href="/adsets", active="exact"),
            ], vertical=True, pills=True, style={"margin-bottom": "50px"}),
    ], style=style_sidebar
)