import pickle
import os
import pandas as pd

nom_fichier_sorties = "sorties.pickle"
nom_fichier_dico_pim = "dico_pim.pickle"

with open(os.path.join(os.getcwd(), "dashboard/data", nom_fichier_sorties), "rb") as f:
    sorties = pickle.load(f)

with open(os.path.join(os.getcwd(), "dashboard/data", nom_fichier_dico_pim), "rb") as f:
    dico_pim = pickle.load(f)


tcd_article_mag = sorties.pivot_table(index=["dt_du_mvt", "lib_motif", "code_article", "code_tiers_emplacement"], aggfunc={"qte_mvt": sum}).reset_index()
tcd_article_mag["dt_du_mvt"] = pd.to_datetime(tcd_article_mag["dt_du_mvt"])
tcd_article_mag["annee"] = tcd_article_mag["dt_du_mvt"].dt.year
tcd_article_mag["semaine"] = tcd_article_mag["dt_du_mvt"].dt.isocalendar().week
tcd_article_mag["annee-semaine"] = tcd_article_mag.apply(lambda row: "{}-0{}".format(row["annee"], row["semaine"]) if row["semaine"] < 10 else "{}-{}".format(row["annee"], row["semaine"]) , axis=1)
tcd_article_mag["libelle_article"] = tcd_article_mag["code_article"].apply(lambda x: dico_pim[x]["libelle_court_article"] if x in dico_pim else "")
