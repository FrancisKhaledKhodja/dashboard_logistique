import dash_bootstrap_components as dbc
from ..data.data import nombre_mag_avec_min, nombre_ref_avec_min, somme_qte_min, valeur_des_min
from ..data.data import df_stock_good_m
import plotly.express as px
from dash import html, dcc
from ...divers.fonctions_diverses import card_creation

### GRAPH MONTANT MIN MAX PAR TYPE DE DEPOT ###
tcd_minmax_par_type_depot = df_stock_good_m.pivot_table(index=["type_de_depot"], aggfunc={"code_magasin": "nunique", "param_min_": sum, "VALO MIN": sum, "VALO MIN DISPO": sum, "VALO RUPTURE": sum}).reset_index()
tcd_minmax_par_type_depot = tcd_minmax_par_type_depot.rename({"type_de_depot": "TYPE DEPOT", "VALO MIN": "VALEUR DES MIN", "VALO MIN DISPO": "VALEUR DES MIN DISPONIBLE", "VALO RUPTURE": "VALEUR DES MIN EN RUPTURE", "code_magasin": "NBRE DE MAG", "param_min_": "SOMME DES MIN"}, axis=1)
tcd_minmax_par_type_depot = tcd_minmax_par_type_depot[["TYPE DEPOT", "SOMME DES MIN", "VALEUR DES MIN", "VALEUR DES MIN DISPONIBLE", "VALEUR DES MIN EN RUPTURE"]]
tcd_minmax_par_type_depot = tcd_minmax_par_type_depot[tcd_minmax_par_type_depot["SOMME DES MIN"] > 0].sort_values("VALEUR DES MIN")

graph_minmax_par_type_depot = px.bar(data_frame=tcd_minmax_par_type_depot, x=["VALEUR DES MIN DISPONIBLE", "VALEUR DES MIN EN RUPTURE"], y="TYPE DEPOT", orientation="h", text_auto=".2s")

### GRAP QUANTITE MIN MAX PAR PROPRIETAIRE ###
tcd_minmax_par_proprietaire = df_stock_good_m.pivot_table(index="proprietaire_stock_champs_calcule", aggfunc={"code_magasin":"nunique", "param_min_": sum , "QTE MIN DISPO": sum, "QTE RUPTURE": sum}).reset_index()
tcd_minmax_par_proprietaire = tcd_minmax_par_proprietaire.rename({"proprietaire_stock_champs_calcule": "PROPRIETAIRE STOCK", "code_magasin": "NBRE DE MAG", "param_min_": "SOMME DES MIN", "QTE MIN DISPO": "QTE MIN DISPONIBLE"}, axis=1)
tcd_minmax_par_proprietaire = tcd_minmax_par_proprietaire[tcd_minmax_par_proprietaire["SOMME DES MIN"] > 0].sort_values("SOMME DES MIN")


graph_minmax_par_proprietaire = px.bar(data_frame=tcd_minmax_par_proprietaire, x=["QTE MIN DISPONIBLE", "QTE RUPTURE"], y="PROPRIETAIRE STOCK", orientation="h", log_x=True, text_auto=".2s")

layout = dbc.Container([
    dbc.Row([
        dbc.CardGroup([
            card_creation("Nombre de magasins avec des min", nombre_mag_avec_min),
            card_creation("Quantité min", "{:,}".format(int(somme_qte_min)).replace(",", " ")),
            card_creation("Valeur des quantités min", "{:,}€".format(int(valeur_des_min)).replace(",", " ")),
            card_creation("Nombre de références avec un min", "{:,}".format(nombre_ref_avec_min).replace(',', ' ')),
            ])
        ]),
    dbc.Row([
        dbc.Col([
            html.H3("MONTANT DES MIN MAX PAR TYPE DE DEPOT"),
            dcc.Graph(figure=graph_minmax_par_type_depot)
        ]),
        dbc.Col([
            html.H3("QUANTITE DES MIN PAR PROPRIETAIRE"),
            dcc.Graph(figure=graph_minmax_par_proprietaire),
        ])
    ])
], fluid=True)
