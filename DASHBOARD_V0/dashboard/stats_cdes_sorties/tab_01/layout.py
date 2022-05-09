import dash_bootstrap_components as dbc
from dash import html, dcc
from ...divers.fonctions_diverses import stat_sorties_article, palmares_article
from ..data.data import tcd_article_mag

dropdown_choix_type_mag =  dcc.Dropdown(options=[{"label": motif, "value": motif}for motif in tcd_article_mag["lib_motif"].unique()], multi=True,id="id--dropdown--type--sortie")
radio_items_choix_periode_palmares = dcc.RadioItems(options=[{"label": "3 mois", "value": 3}, 
                                                             {"label": "6 mois", "value": 6}, 
                                                             {"label": "12 mois", "value": 12}, 
                                                             {"label": "24 mois", "value": 24}], 
                                                    id="id--choix--periode-palmares", 
                                                    value=3)

layout = dbc.Container([
    dbc.Row([
        html.H3("PALMARES SORTIES"),
        dbc.Col([
            dropdown_choix_type_mag
            ], width=6),
        dbc.Col([
            radio_items_choix_periode_palmares
            ], width=6),
        dcc.Graph(id="id--graph--palmares")
    ]),
    dbc.Row([
        dcc.Graph(id="id--graph--stats--sorties")
        ])
    
], fluid=True)