from dashboard.index import app
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output
from dashboard.minmax.tabs import tabs_minmax
from dashboard.stats_cdes_sorties.tabs import tabs_stats_sorties


header = html.Div([
    html.H1("INDICATEURS LOGISTIQUES", id="id_h1_header_app"),
    dbc.Nav([
        dbc.NavLink("MIN MAX", href="/minmax"),
        dbc.NavLink("STATS SORTIES", href="/stats_cdes_sorties"),
        ])
    ])

app.layout = dbc.Container([
    dcc.Location(id="url"),
    dbc.Row([
        header
        ]),
    dbc.Row([
        html.Div(id="page-content")
        ]),
], fluid=True)

@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def render_page_content(pathname):
    if pathname == "/minmax":
        return tabs_minmax
    elif pathname == "/stats_cdes_sorties":
        return tabs_stats_sorties
    else:
        return None
