import os
import pickle
import pandas as pd
from ...divers.fonctions_diverses import creation_dataframe_taux_conformite

nom_fichier_stock = "stock.pickle"
nom_fichier_annuaire = "annuaire_mag.pickle"

with open(os.path.join(os.getcwd(), "DASHBOARD_V0/dashboard/data", nom_fichier_stock), "rb") as f:
    df_stock = pickle.load(f)

with open(os.path.join(os.getcwd(), "DASHBOARD_V0/dashboard/data", nom_fichier_annuaire), "rb") as f:
    df_annuaire_mag = pickle.load(f)

def creation_dataframe_valo_min_et_rupture_min(df):
    stock_good_m = df[(df["flag_stock_d_m"] == "M") & (df["code_qualite"].isin(["GOOD", "BLOQG"]))]
    stock_good_m = pd.merge(stock_good_m, df_annuaire_mag[["code_mag_speed", "latitude", "longitude"]], how="left", left_on="code_magasin", right_on="code_mag_speed")
    stock_good_m.drop("code_mag_speed", axis=1, inplace=True)
    stock_good_m_sans_lot = stock_good_m.pivot_table(index=['code_magasin', 'libelle_magasin', 'statut_magasin', 
                                                           'type_de_depot', 'proprietaire_stock_champs_calcule', 'code_article',
                                                           'description_article_tdf', 'statut_article', 'feuille_de_catalogue', "latitude", "longitude"], 
                                                     aggfunc={'pump': min, 'param_min_': min, 'param_max_': min, "qte_stock": sum, "valo_stock": sum}).reset_index()
    
    stock_good_m_sans_lot["QTE MIN DISPO"] = stock_good_m_sans_lot[["param_min_", "qte_stock"]].apply(lambda x: min(x), axis=1)
    stock_good_m_sans_lot["VALO MIN"] = stock_good_m_sans_lot["param_min_"] * stock_good_m_sans_lot["pump"]
    stock_good_m_sans_lot["VALO MIN DISPO"] = stock_good_m_sans_lot[["param_min_", "qte_stock"]].apply(lambda x: min(x), axis=1) * stock_good_m_sans_lot["pump"]
    stock_good_m_sans_lot['RUPTURE'] = stock_good_m_sans_lot.apply(lambda row: 1 if row["param_min_"] > row["qte_stock"] else 0, axis=1)
    stock_good_m_sans_lot["QTE RUPTURE"] = stock_good_m_sans_lot.apply(lambda row: row["param_min_"] - row["qte_stock"] if row["param_min_"] > row["qte_stock"] else 0, axis=1)
    stock_good_m_sans_lot["VALO RUPTURE"] = stock_good_m_sans_lot["QTE RUPTURE"] * stock_good_m_sans_lot["pump"]

    return stock_good_m_sans_lot


def creation_dataframe_m_bad(df):
    stock_bad_m = df[(df["flag_stock_d_m"] == "M") & (df["code_qualite"].isin(["BAD", "BLOQB"]))]
    stock_bad_m = pd.merge(stock_bad_m, df_annuaire_mag[["code_mag_speed", "latitude", "longitude"]], how="left", left_on="code_magasin", right_on="code_mag_speed")
    stock_bad_m.drop("code_mag_speed", axis=1, inplace=True)
    stock_bad_m_sans_lot = stock_bad_m.pivot_table(index=['code_magasin', 'libelle_magasin', 'statut_magasin', 
                                                           'type_de_depot', 'proprietaire_stock_champs_calcule', 'code_article',
                                                           'description_article_tdf', 'statut_article', 'feuille_de_catalogue', "latitude", "longitude"], 
                                                     aggfunc={'pump': min, 'param_min_': min, 'param_max_': min, "qte_stock": sum, "valo_stock": sum}).reset_index()

    return stock_bad_m_sans_lot


### TAB TAUX DE CONFORMITE ###

df_stock_good_m = creation_dataframe_valo_min_et_rupture_min(df_stock)
df_stock_good_m["type_de_depot"] = df_stock_good_m[['libelle_magasin', "type_de_depot"]].apply(lambda row: "DATACENTER" if "DATACENTER" in row["libelle_magasin"] else row["type_de_depot"], axis=1)
df_stock_good_m["type_de_depot"] = df_stock_good_m[['libelle_magasin', "type_de_depot"]].apply(lambda row: "TELEPORT" if "TELEPORT" in row["libelle_magasin"] else row["type_de_depot"], axis=1)

df_stock_bad_m = creation_dataframe_m_bad(df_stock)

stock_good_m_mplc = df_stock_good_m[df_stock_good_m["code_magasin"] == "MPLC"]
stock_good_m_mplc.rename({"qte_stock": "qte_stock_good_mplc"}, axis=1, inplace=True)

stock_bad_m_mplc = df_stock_bad_m[df_stock_bad_m["code_magasin"] == "MPLC"]
stock_bad_m_mplc.rename({"qte_stock": "qte_stock_bad_mplc"}, axis=1, inplace=True)

stock_bad_m_reparateurs = df_stock_bad_m[df_stock_bad_m["type_de_depot"].isin(['REPARATEUR EXTERNE', 'REPARATEUR INTERNE'])]
stock_bad_m_reparateurs = stock_bad_m_reparateurs.pivot_table(index=["code_article", "description_article_tdf", "statut_article", "pump"], aggfunc={"qte_stock": sum}).reset_index()
stock_bad_m_reparateurs.rename({"qte_stock": "qte_stock_bad_reparateurs"}, axis=1, inplace=True)

stock_bad_m_autres = df_stock_bad_m[(df_stock_bad_m["code_magasin"] != "MPLC") & (~df_stock_bad_m["type_de_depot"].isin(['REPARATEUR EXTERNE', 'REPARATEUR INTERNE']))]
stock_bad_m_autres = stock_bad_m_autres.pivot_table(index=["code_article", "description_article_tdf", "statut_article", "pump"], aggfunc={"qte_stock": sum}).reset_index()
stock_bad_m_autres.rename({"qte_stock": "qte_stock_bad_autres"}, axis=1, inplace=True)

df_taux_conformite = creation_dataframe_taux_conformite(df_stock_good_m)

### TAB ACCUEIL ###

nombre_mag_avec_min = len(df_stock_good_m[df_stock_good_m["param_min_"] > 0]["code_magasin"].unique())
somme_qte_min = df_stock_good_m["param_min_"].sum()
valeur_des_min = df_stock_good_m["VALO MIN"].sum()
nombre_ref_avec_min = len(df_stock_good_m[df_stock_good_m["param_min_"] > 0]["code_article"].unique())