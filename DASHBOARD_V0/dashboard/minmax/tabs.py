import dash_bootstrap_components as dbc
from .tab_01.layout import layout as layout_tab_01 
from .tab_02.layout import layout as layout_tab_02
from .tab_02 import callbacks



tabs_minmax = dbc.Tabs([
    dbc.Tab([
        layout_tab_01
    ], label="ACCUEIL", tab_id="accueil_minmax"),
    dbc.Tab([
        layout_tab_02
        ], label="TAUX DE CONFORMITE", tab_id="taux_conformite_minmax"),

], id="tabs")