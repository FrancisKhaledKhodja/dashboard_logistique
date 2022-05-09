import pandas as pd
import os
import pickle

repertoire_data = r"data"
repertoire_data_minmax = "data\dataframes_app_minmax"

nom_df_stock = "stock.pickle"
nom_df_annuaire_mag = "annuaire_mag.pickle"

with open(os.path.join(repertoire_data, nom_df_stock), "rb") as f:
    df_stock = pickle.load(f)

with open(os.path.join(repertoire_data, nom_df_annuaire_mag), "rb") as f:
    df_annuaire_mag = pickle.load(f)

# Chargement des données

def creation_dataframe_valo_min_et_rupture_min(df):
    stock_good_m = df[(df["flag_stock_d_m"] == "M") & (df["code_qualite"].isin(["GOOD", "BLOQG"]))]
    stock_good_m = pd.merge(stock_good_m, df_annuaire_mag[["code_mag_speed", "latitude", "longitude"]], how="left", left_on="code_magasin", right_on="code_mag_speed")
    stock_good_m.drop("code_mag_speed", axis=1, inplace=True)
    stock_good_m_sans_lot = stock_good_m.pivot_table(index=['code_magasin', 'libelle_magasin', 'statut_magasin', 
                                                           'type_de_depot', 'proprietaire_stock_champs_calcule', 'code_article',
                                                           'description_article_tdf', 'statut_article', 'feuille_de_catalogue', "latitude", "longitude"], 
                                                     aggfunc={'pump': min, 'param_min_': min, 'param_max_': min, "qte_stock": sum, "valo_stock": sum}).reset_index()

    stock_good_m_sans_lot["VALO MIN"] = stock_good_m_sans_lot["param_min_"] * stock_good_m_sans_lot["pump"]
    stock_good_m_sans_lot['RUPTURE'] = stock_good_m_sans_lot.apply(lambda row: 1 if row["param_min_"] > row["qte_stock"] else 0, axis=1)
    stock_good_m_sans_lot["QTE RUPTURE"] = stock_good_m_sans_lot.apply(lambda row: row["param_min_"] - row["qte_stock"] if row["param_min_"] > row["qte_stock"] else 0, axis=1)
    stock_good_m_sans_lot["VALO RUPTURE"] = stock_good_m_sans_lot["QTE RUPTURE"] * stock_good_m_sans_lot["pump"]

    return stock_good_m_sans_lot

df_stock_good_m_sans_lot = creation_dataframe_valo_min_et_rupture_min(df_stock)

df_stock_good_m_sans_lot["type_de_depot"] = df_stock_good_m_sans_lot[['libelle_magasin', "type_de_depot"]].apply(lambda row: "DATACENTER" if "DATACENTER" in row["libelle_magasin"] else row["type_de_depot"], axis=1)
df_stock_good_m_sans_lot["type_de_depot"] = df_stock_good_m_sans_lot[['libelle_magasin', "type_de_depot"]].apply(lambda row: "TELEPORT" if "TELEPORT" in row["libelle_magasin"] else row["type_de_depot"], axis=1)

with open(os.path.join(repertoire_data_minmax, "df_stock_good_m_sans_lot.pickle"), "wb") as f:
    pickle.dump(df_stock_good_m_sans_lot, f)


def creation_dataframe_m_bad(df):
    stock_bad_m = df[(df["flag_stock_d_m"] == "M") & (df["code_qualite"].isin(["BAD", "BLOQB"]))]
    stock_bad_m = pd.merge(stock_bad_m, df_annuaire_mag[["code_mag_speed", "latitude", "longitude"]], how="left", left_on="code_magasin", right_on="code_mag_speed")
    stock_bad_m.drop("code_mag_speed", axis=1, inplace=True)
    stock_bad_m_sans_lot = stock_bad_m.pivot_table(index=['code_magasin', 'libelle_magasin', 'statut_magasin', 
                                                           'type_de_depot', 'proprietaire_stock_champs_calcule', 'code_article',
                                                           'description_article_tdf', 'statut_article', 'feuille_de_catalogue', "latitude", "longitude"], 
                                                     aggfunc={'pump': min, 'param_min_': min, 'param_max_': min, "qte_stock": sum, "valo_stock": sum}).reset_index()

    return stock_bad_m_sans_lot

df_stock_bad_m_sans_lot = creation_dataframe_m_bad(df_stock)

with open(os.path.join(repertoire_data_minmax, "df_stock_bad_m_sans_lot.pickle"), "wb") as f:
    pickle.dump(df_stock_bad_m_sans_lot, f)

def creation_dataframe_minmax_par_type_mag(df):
    df_stock_avec_minmax = df[df["param_min_"] > 0]

    df_stock_type_depot = df_stock_avec_minmax.pivot_table(index=["type_de_depot"], aggfunc={"code_magasin": "nunique", "param_min_": sum, "VALO MIN": sum}).reset_index()
    df_stock_type_depot.columns = ["TYPE DEPOT", "VALEUR MIN", "NBRE MAG", "QTE MIN"]
    df_stock_type_depot = df_stock_type_depot[["TYPE DEPOT","NBRE MAG", "QTE MIN", "VALEUR MIN"]]
    df_stock_type_depot_format = df_stock_type_depot.copy()
    df_stock_type_depot_format["QTE MIN"] = df_stock_type_depot_format["QTE MIN"].apply(lambda x: "{:,}".format(int(x)).replace(",", " "))
    df_stock_type_depot_format["VALEUR MIN"] = df_stock_type_depot_format["VALEUR MIN"].apply(lambda x: "{:,} €".format(int(x)).replace(",", " "))

    return df_stock_type_depot_format

df_stock_type_depot_format = creation_dataframe_minmax_par_type_mag(df_stock_good_m_sans_lot)

with open(os.path.join(repertoire_data_minmax, "df_stock_type_depot_format.pickle"), "wb") as f:
    pickle.dump(df_stock_type_depot_format, f)


def creation_dataframe_minmax_par_proprietaire(df):
    df_minmax_par_proprietaire = df[df["param_min_"] > 0].pivot_table(index=["proprietaire_stock_champs_calcule"], aggfunc={"code_magasin": "nunique", "code_article": "nunique", "param_min_": sum}).reset_index()
    df_minmax_par_proprietaire.columns = ["PROPRIETAIRE STOCK", "NOMBRE DE CODE ARTICLE", "NOMBRE DE MAGASINS", "SOMME DES MIN"]
    df_minmax_par_proprietaire_format = df_minmax_par_proprietaire.copy()
    df_minmax_par_proprietaire_format["NOMBRE DE CODE ARTICLE"] = df_minmax_par_proprietaire_format.apply(lambda row: "{:,}".format(int(row["NOMBRE DE CODE ARTICLE"])).replace(',', " "), axis=1)
    df_minmax_par_proprietaire_format["SOMME DES MIN"] = df_minmax_par_proprietaire_format.apply(lambda row: "{:,}".format(int(row["SOMME DES MIN"])).replace(',', " "), axis=1)

    return df_minmax_par_proprietaire_format

df_minmax_par_proprietaire_format = creation_dataframe_minmax_par_proprietaire(df_stock_good_m_sans_lot)

with open(os.path.join(repertoire_data_minmax, "df_minmax_par_proprietaire_format.pickle"), "wb") as f:
    pickle.dump(df_minmax_par_proprietaire_format, f)


def creation_dataframe_minmax_par_mag(df):
    df_minmax_par_mag = df[df["param_min_"] > 0].pivot_table(index=["code_magasin", "libelle_magasin", "statut_magasin", "type_de_depot", "latitude", "longitude"], 
                                     aggfunc={"code_article": "nunique", "param_min_": sum, "VALO MIN": sum, "RUPTURE": sum}).reset_index()
    df_minmax_par_mag.rename(mapper={"VALO MIN": "valeur_des_min", "code_article": "nbre_ref", "param_min_": "somme_min", "RUPTURE": "nbre_ref_rupture"}, axis=1, inplace=True)
    df_minmax_par_mag["taux_rupture"] = df_minmax_par_mag.apply(lambda row: round(row["nbre_ref_rupture"] / row["nbre_ref"] * 100, 1), axis=1)
    
    return df_minmax_par_mag

df_minmax_par_mag = creation_dataframe_minmax_par_mag(df_stock_good_m_sans_lot)

with open(os.path.join(repertoire_data_minmax, "df_minmax_par_mag.pickle"), "wb") as f:
    pickle.dump(df_minmax_par_mag, f)


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

df_taux_conformite = creation_dataframe_taux_conformite(df_stock_good_m_sans_lot)

with open(os.path.join(repertoire_data_minmax, "df_taux_conformite.pickle"), "wb") as f:
    pickle.dump(df_taux_conformite, f)


def creation_dataframe_article_en_rupture(df):
    df_articles_en_rupture = df[df["RUPTURE"] > 0].pivot_table(index=["code_article", "description_article_tdf", "statut_article"], 
                                                                              aggfunc={"code_magasin": "nunique", "QTE RUPTURE": sum, "VALO RUPTURE": sum}).reset_index()

    df_articles_en_rupture.columns = ["CODE ARTICLE", "LIBELLE ARTICLE", "STATUT ARTICLE", "QTE EN RUPTURE", "VALEUR STOCK EN RUPTURE", "NOMBRE DE MAGASIN EN RUPTURE"]
    df_articles_en_rupture = df_articles_en_rupture[["CODE ARTICLE", "LIBELLE ARTICLE", "STATUT ARTICLE", "NOMBRE DE MAGASIN EN RUPTURE", "QTE EN RUPTURE", "VALEUR STOCK EN RUPTURE"]]
    df_articles_en_rupture.sort_values("NOMBRE DE MAGASIN EN RUPTURE", ascending=False, inplace=True)
    
    tcd_bad = df_stock_bad_m_sans_lot.pivot_table(index=["code_article", "description_article_tdf", "type_de_depot"], aggfunc={"qte_stock": sum}).reset_index()

    tcd_bad_reparateur= tcd_bad[tcd_bad["type_de_depot"].isin(["REPARATEUR EXTERNE", "REPARATEUR INTERNE"])].pivot_table(index=["code_article", "description_article_tdf"], aggfunc={"qte_stock": sum}).reset_index()

    tcd_bad_autres = tcd_bad[~tcd_bad["type_de_depot"].isin(["REPARATEUR EXTERNE", "REPARATEUR INTERNE"])].pivot_table(index=["code_article", "description_article_tdf"], aggfunc={"qte_stock": sum}).reset_index()

    tcd_good_mplc = df_stock_good_m_sans_lot[df_stock_good_m_sans_lot["code_magasin"] == "MPLC"].pivot_table(index=["code_article", "description_article_tdf"], aggfunc={"qte_stock": sum}).reset_index()

    df_articles_en_rupture = pd.merge(df_articles_en_rupture, tcd_good_mplc[["code_article", "qte_stock"]], left_on="CODE ARTICLE", right_on=["code_article"], how="left")
    df_articles_en_rupture.drop("code_article", axis=1, inplace=True)
    df_articles_en_rupture.rename({"qte_stock": "QTE GOOD MPLC"}, axis=1, inplace=True)

    df_articles_en_rupture = pd.merge(df_articles_en_rupture, tcd_bad_reparateur[["code_article", "qte_stock"]], left_on="CODE ARTICLE", right_on="code_article", how="left")
    df_articles_en_rupture.drop("code_article", axis=1, inplace=True)
    df_articles_en_rupture.rename({"qte_stock": "QTE BAD REPARATEUR"}, axis=1, inplace=True)

    df_articles_en_rupture = pd.merge(df_articles_en_rupture, tcd_bad_autres[["code_article", "qte_stock"]], left_on="CODE ARTICLE", right_on="code_article", how="left")
    df_articles_en_rupture.drop("code_article", axis=1, inplace=True)
    df_articles_en_rupture.rename({"qte_stock": "QTE BAD AUTRES"}, axis=1, inplace=True)
    
    df_articles_en_rupture["VALEUR STOCK EN RUPTURE"] = df_articles_en_rupture["VALEUR STOCK EN RUPTURE"].astype(int)
    df_articles_en_rupture["QTE EN RUPTURE"] = df_articles_en_rupture["QTE EN RUPTURE"].astype(int)

    df_articles_en_rupture["QTE GOOD MPLC"] = df_articles_en_rupture["QTE GOOD MPLC"].fillna(0).astype(int)
    df_articles_en_rupture["QTE BAD REPARATEUR"] = df_articles_en_rupture["QTE BAD REPARATEUR"].fillna(0).astype(int)
    df_articles_en_rupture["QTE BAD AUTRES"] = df_articles_en_rupture["QTE BAD AUTRES"].fillna(0).astype(int)
    
    return df_articles_en_rupture

df_articles_en_rupture = creation_dataframe_article_en_rupture(df_stock_good_m_sans_lot)

with open(os.path.join(repertoire_data_minmax, "df_articles_en_rupture.pickle"), "wb") as f:
    pickle.dump(df_articles_en_rupture, f)
