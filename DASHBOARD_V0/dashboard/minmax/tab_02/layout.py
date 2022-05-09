import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table
from ..data.data import df_stock_good_m, df_taux_conformite
from ...divers.fonctions_diverses import calcul_taux_conformite, card_creation


taux_conformite_global = calcul_taux_conformite(df_taux_conformite)
taux_conformite_mplc = calcul_taux_conformite(df_taux_conformite, "NATIONAL")
taux_conformite_mag_locaux = calcul_taux_conformite(df_taux_conformite, "LOCAL")
taux_conformite_pds = calcul_taux_conformite(df_taux_conformite, "PIED DE SITE")
taux_conformite_reo_embarque = calcul_taux_conformite(df_taux_conformite, "REO", "EMBARQUE")

# Construction dropdown liste type de magasin
liste_type_mag = [{"label": "TOUS TYPES", "value": "TOUS TYPES"}]
liste_type_mag.extend([{"label": type_depot, "value": type_depot} for type_depot in df_stock_good_m["type_de_depot"].unique()])
dropdown_type_mag = dcc.Dropdown(options=liste_type_mag, value="TOUS TYPES", id="dropdown--type--depot")


layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            card_creation("TAUX DE CONFORMITE GLOBAL", taux_conformite_global)
        ], width=6),
        dbc.Col([
            dbc.CardGroup([
                card_creation("TAUX DE CONFORMITE MPLC", taux_conformite_mplc),
                card_creation("TAUX DE CONFORMITE MAG LOCAUX", taux_conformite_mag_locaux),
                card_creation("TAUX DE CONFORMITE PDS", taux_conformite_pds),
                card_creation("TAUX DE CONFORMITE REO ET EMBARQUES", taux_conformite_reo_embarque),
                ]),
        ], width=6),
    ]),
    dbc.Row([
        html.H3("TAUX DE CONFORMITE PAR MAGASIN"),
        dbc.Row([
            dbc.Col([
                dropdown_type_mag,
            ]),
            dbc.Col([
                dcc.Checklist(["Magasins avec rupture uniquement"], id="checklist--mag--rupture"),
            ])
        ]),
        
        html.Div(id="datatable--taux--conformite"),
        ]),
    dbc.Row([
        dbc.Col([
            html.Div(id="map--tdf"),
        ], width=6),
        dbc.Col([
            html.Div(id="affichage--magasin"),
        ], width=6)
        ]),
], fluid=True)