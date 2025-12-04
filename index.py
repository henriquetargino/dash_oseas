from dash import html, dcc
import dash
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from app import *
import sidebar, campaigns, adsets

# =========  Layout  =========== #
content = html.Div(id="page-content")

app.layout = dbc.Container(children=[
    dbc.Row([

        dbc.Col([
            dcc.Location(id="url"), 
            sidebar.layout
        ], md=2),

        dbc.Col([
            content
        ], md=10, style={"padding": "26px"})
    ])
], fluid=True, style={"padding": "0px"})


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/" or pathname == "/campaigns":
        return campaigns.layout
    elif pathname == "/adsets":
        return adsets.layout
    else:
        return campaigns.layout

if __name__ == "__main__":
    app.run(port=8051, host='0.0.0.0', debug=True)