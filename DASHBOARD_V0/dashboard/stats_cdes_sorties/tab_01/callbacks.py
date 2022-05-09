from dash import Output, Input, callback
from ...divers.fonctions_diverses import palmares_article, stat_sorties_article
from ..data.data import tcd_article_mag
from dash.exceptions import PreventUpdate



@callback(Output("id--graph--palmares", "figure"), [Input("id--choix--periode-palmares", "value"), Input("id--dropdown--type--sortie", "value")])
def graph_palmares_sorties(nombre_mois, type_sortie):
    if nombre_mois is None:
        raise PreventUpdate
    fig, _ = palmares_article(tcd_article_mag, nombre_mois, 20, type_sortie)
    return fig


@callback(Output("id--graph--stats--sorties", "figure"), [Input("id--graph--palmares", "hoverData"), Input("id--dropdown--type--sortie", "value")])
def graph_stats_sorties(hover_data, type_sortie):
    if hover_data is None:
        raise PreventUpdate
    code_article = hover_data["points"][0]["y"].split("-")[0].strip()
    fig, _ = stat_sorties_article(tcd_article_mag, code_article, type_sortie)
    return fig
    