import dash_bootstrap_components as dbc
from dash import html, dcc
from ...divers.fonctions_diverses import stat_sorties_article, palmares_article
from ..data.data import tcd_article_mag



fig_stats_sorties, tcd_stats_sorties = stat_sorties_article(tcd_article_mag)
fig_palmares, tcd_palmares = palmares_article(tcd_article_mag, 12, 20)


layout = dbc.Container([
    html.H2("STATISTIQUES SORTIES"),
    dbc.Row([
        html.H3("PALMARES SORTIES"),
        dcc.Dropdown(options=[{"label": motif, "value": motif}for motif in tcd_article_mag["lib_motif"].unique()], multi=True,id="id--dropdown--type--sortie"),
        dcc.RadioItems(options=[{"label": "3 mois", "value": 3}, 
                                {"label": "6 mois", "value": 6}, 
                                {"label": "12 mois", "value": 12}, 
                                {"label": "24 mois", "value": 24}], 
                       id="id--choix--periode-palmares", 
                       value=3),
        dcc.Graph(id="id--graph--palmares")
    ]),
    dbc.Row([
        dcc.Graph(id="id--graph--stats--sorties")
        ])
    
], fluid=True)