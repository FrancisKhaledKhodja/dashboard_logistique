import pandas as pd
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px

def creation_dataframe_taux_conformite(df):
    df_mag_avec_min = df[df["param_min_"] > 0]
    df_taux_conformite = df_mag_avec_min.pivot_table(index=["code_magasin", "libelle_magasin", "type_de_depot", "latitude", "longitude"], 
                            aggfunc={"code_article": "nunique", "param_min_": sum, "VALO MIN": sum, "QTE RUPTURE": sum, "VALO RUPTURE": sum}).reset_index()

    df_taux_conformite.columns = ["CODE MAGASIN", "LIBELLE MAGASIN", "TYPE DEPOT", "LATITUDE", "LONGITUDE",
                          "SOMME REF RUPTURE", "SOMME VALEUR STOCK MIN", "SOMME VALEUR RUPTURE", "NOMBRE REF", "SOMME QTE MIN"]

    df_taux_conformite = df_taux_conformite[["CODE MAGASIN", "LIBELLE MAGASIN", "TYPE DEPOT", "LATITUDE", "LONGITUDE", 
                                         "NOMBRE REF", "SOMME QTE MIN", "SOMME VALEUR STOCK MIN", 
                                         "SOMME REF RUPTURE", "SOMME VALEUR RUPTURE"]]

    df_taux_conformite["TAUX RUPTURE"] = df_taux_conformite.apply(lambda row: round(row["SOMME REF RUPTURE"] / row["NOMBRE REF"] * 100, 1), axis=1)
    df_taux_conformite["TAUX CONFORMITE"] = 100 - df_taux_conformite["TAUX RUPTURE"]

    return df_taux_conformite


def calcul_taux_conformite(df_taux_conformite, *type_depot):
    if len(type_depot) == 0:
        df_taux_conformite_type_depot = df_taux_conformite.copy()
    else:
        df_taux_conformite_type_depot = pd.DataFrame()
        for type_d in type_depot:
            df = df_taux_conformite[df_taux_conformite["TYPE DEPOT"] == type_d]
            df_taux_conformite_type_depot = pd.concat([df, df_taux_conformite_type_depot])

    taux_conformite_type_depot = "{}%".format(round(sum(df_taux_conformite_type_depot["SOMME QTE MIN"] * df_taux_conformite_type_depot["TAUX CONFORMITE"]) / df_taux_conformite_type_depot["SOMME QTE MIN"].sum(), 1))
    return taux_conformite_type_depot

def card_creation(titre, kpi):
    card = dbc.Card([
        dbc.CardHeader(titre, className="card_header"),
        dbc.CardBody(kpi, className="card_kpi")
    ], className="card")
    return card


def stat_sorties_article(data_frame, code_article, lib_motif=None):
    tcd = data_frame.copy()
    if lib_motif is not None and isinstance(lib_motif, str):
        lib_motif = [lib_motif]
    if lib_motif is not None:
        tcd0 = pd.DataFrame()
        for motif in lib_motif:
            tcd0 = pd.concat([tcd[tcd["lib_motif"] == motif], tcd0])
        tcd = tcd0.copy()
        tcd0 = None
    tcd = tcd[tcd["code_article"] == code_article]
    tcd = tcd.pivot_table(index=["dt_du_mvt_2", "lib_motif", "code_article", "libelle_article"], aggfunc={"qte_mvt": sum}).reset_index()

    data = []
    for motif in tcd["lib_motif"].unique():
        tcd0 = tcd[tcd["lib_motif"] == motif]
        data.append(go.Bar(name=motif, x = tcd0["dt_du_mvt_2"], y=tcd0["qte_mvt"]))
    
    fig = go.Figure(data=data, )
    fig.update_layout(barmode='stack', title="STATS DU CODE ART {}".format(code_article))
    fig.update_yaxes(range=[0, max(tcd["qte_mvt"]) * 1.2])
    return fig, tcd


def palmares_article(data_frame, nombre_mois_glissant, nombre_articles, type_mouvements=None):
    date_fin = data_frame["dt_du_mvt"].max()
    date_debut = data_frame["dt_du_mvt"].max() - pd.DateOffset(months=nombre_mois_glissant)
    if type_mouvements is not None:
        data_frame = data_frame[data_frame["lib_motif"].isin(type_mouvements)]
    tcd = data_frame[data_frame["dt_du_mvt"] >= date_debut].pivot_table(index=["code_article", "libelle_article"], aggfunc={"qte_mvt": sum}).reset_index().sort_values("qte_mvt", ascending=True)[-nombre_articles:]

    data = []
    
    fig = px.bar(data_frame=tcd, 
                 y = ["{} - {}".format(row["code_article"], row["libelle_article"][:60]) for i, row in tcd[["code_article", "libelle_article"]].iterrows()], 
                 x = tcd["qte_mvt"], 
                 orientation="h")
    
    return fig, tcd