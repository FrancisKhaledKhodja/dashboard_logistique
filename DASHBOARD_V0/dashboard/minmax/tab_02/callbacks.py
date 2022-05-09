from ..data.data import df_stock_good_m, stock_good_m_mplc, stock_bad_m_mplc, stock_bad_m_reparateurs, stock_bad_m_autres, df_taux_conformite

from dash.dependencies import Output, Input
from dash import html, callback, dash_table
from dash.dash_table import DataTable
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash.exceptions import PreventUpdate
from ...divers.fonctions_diverses import card_creation


@callback(Output("map--tdf", "children"), [Input("dropdown--type--depot", "value"), Input("tabs", "active_tab"), Input("checklist--mag--rupture", "value")])
def map_tdf(type_depot, active_tab, filtre_mag_avec_rupture):
    if type_depot is None:
        raise PreventUpdate
    if active_tab == "taux_conformite_minmax":
        tcd = df_stock_good_m.pivot_table(index=["code_magasin", "libelle_magasin", "type_de_depot", "latitude", "longitude"], aggfunc=sum).reset_index()
        if type_depot != "TOUS TYPES":
            tcd = tcd[tcd["type_de_depot"] == type_depot]
        if filtre_mag_avec_rupture is not None and "Magasins avec rupture uniquement" in filtre_mag_avec_rupture:
            tcd = tcd[tcd["RUPTURE"] > 0]
        children = [dl.TileLayer()]
        markers = []
        for _, row in tcd.iterrows():
            taux_rupture = df_stock_good_m[df_stock_good_m["code_magasin"] == row["code_magasin"]]["RUPTURE"].sum() / len(df_stock_good_m[df_stock_good_m["code_magasin"] == row["code_magasin"]]) > 0
            if taux_rupture == 0 :
                color = "blue"
            elif taux_rupture > 0:
                color = "orange"
            circlemarker = dl.Circle(center=(row["latitude"], row["longitude"]), color=color, radius=10000)
            children.append(circlemarker)
            marker = {"lat": row["latitude"], 
                  "lon": row["longitude"], 
                  "name": row["code_magasin"], 
                  "tooltip": "{}<br>{}".format(row['code_magasin'], row["libelle_magasin"])}
            markers.append(marker)

        geojson = dl.GeoJSON(data=dlx.dicts_to_geojson(markers), id="markers--magasins", cluster=True)
        children.append(geojson)
        map_tdf = dl.Map(children=children, center=[45, 3], zoom=5, style={"height": "80vh", "width": "100%"}, )

        return map_tdf


@callback(Output("affichage--magasin", "children"), [Input("markers--magasins", "hover_feature")])
def affichage_magasin(features):
    if features is None or "name" not in features["properties"]:
        raise PreventUpdate
    code_mag = features["properties"]["name"]
    df_stock_mag = df_stock_good_m[df_stock_good_m["code_magasin"] == code_mag]
    nbre_de_ref = len(df_stock_mag)
    nbre_art_en_rupture = df_stock_mag["RUPTURE"].sum()

    card_group = dbc.CardGroup([
        card_creation("Code magasin", code_mag),
        card_creation("Nombre de références avec un min", nbre_de_ref),
        card_creation("Nombre de références en rupture", nbre_art_en_rupture),
    ])

    colonnes = ["code_article", "description_article_tdf", "statut_article", "pump", "param_min_", "qte_stock"]
    df_stock_mag_rupture = df_stock_mag[df_stock_mag["RUPTURE"] > 0][colonnes]

    df_stock_mag_rupture = df_stock_mag_rupture.merge(stock_good_m_mplc[["code_article", "qte_stock_good_mplc"]], how="left", on="code_article")
    df_stock_mag_rupture = df_stock_mag_rupture.merge(stock_bad_m_mplc[["code_article", "qte_stock_bad_mplc"]], how="left", on="code_article")
    df_stock_mag_rupture = df_stock_mag_rupture.merge(stock_bad_m_reparateurs[["code_article", "qte_stock_bad_reparateurs"]], how="left", on="code_article")
    df_stock_mag_rupture = df_stock_mag_rupture.merge(stock_bad_m_autres[["code_article", "qte_stock_bad_autres"]], how="left", on="code_article")

    datatable = DataTable(columns=[{"name": col.replace("_", " "), "id": col} for col in df_stock_mag_rupture.columns], 
                          data=df_stock_mag_rupture.to_dict("records"),
                          export_format="xlsx",
                          filter_action="native",
                          sort_action="native",
                          page_size=10,
                          style_header={"whiteSpace": "normal", "height": "auto"},
                          style_data_conditional=[{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(220, 220, 220)',}],
                          style_data={'whiteSpace': 'normal','height': 'auto'}, 
                          style_cell_conditional=[{"if": {"column_id": "code_article"}, "width": "100px"}, 
                                                  {"if": {"column_id": "description_article_tdf"}, "width": "200px"}, 
                                                  {"if": {"column_id": "statut_article"}, "width": "80px"}, 
                                                  {"if": {"column_id": "pump"}, "width": "50px"}, 
                                                  {"if": {"column_id": "param_min_"}, "width": "50px"}, 
                                                  {"if": {"column_id": "qte_stock"}, "width": "50px"}, 
                                                  {"if": {"column_id": "qte_stock_good_mplc"}, "width": "50px"}, 
                                                  {"if": {"column_id": "qte_stock_bad_mplc"}, "width": "50px"}, 
                                                  {"if": {"column_id": "qte_stock_bad_reparateurs"}, "width": "50px"}, 
                                                  {"if": {"column_id": "qte_stock_bad_autres"}, "width": "50px"}])

    display_info_mag = html.Div([
        dbc.Row([
            card_group,
        ]),
        dbc.Row([
            html.H3("Liste des articles en rupture"),
            datatable,
        ])
    ])

    return display_info_mag


@callback(Output("datatable--taux--conformite", "children"), [Input("dropdown--type--depot", "value"), Input("checklist--mag--rupture", "value")])
def actualisation_datatable_taux_conformite(type_de_depot, filtre_mag_avec_rupture):
    if type_de_depot == "TOUS TYPES":
        df_taux_conformite_par_type = df_taux_conformite.copy()
    else:
        df_taux_conformite_par_type = df_taux_conformite[df_taux_conformite["TYPE DEPOT"] == type_de_depot]

    if filtre_mag_avec_rupture is not None and "Magasins avec rupture uniquement" in filtre_mag_avec_rupture:
        df_taux_conformite_par_type = df_taux_conformite_par_type[df_taux_conformite_par_type["SOMME REF RUPTURE"] > 0]

    colonnes = ["CODE MAGASIN", "LIBELLE MAGASIN", "TYPE DEPOT", "NOMBRE REF", "SOMME QTE MIN", "SOMME VALEUR STOCK MIN", "SOMME REF RUPTURE", "SOMME VALEUR RUPTURE", "TAUX RUPTURE", "TAUX CONFORMITE"]

    datatable_taux_conformite = dash_table.DataTable(data=df_taux_conformite_par_type.to_dict("records"), 
                                                 columns=[{"name": col, "id": col} for col in colonnes],
                                                 sort_action="native", 
                                                 page_size=10, 
                                                 id="datatable_taux_conformite")

    return datatable_taux_conformite