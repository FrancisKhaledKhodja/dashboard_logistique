import dash_bootstrap_components as dbc
from dash import html
from .tab_01.layout import layout as layout_tab_01
from .tab_01 import callbacks


tabs_stats_sorties = dbc.Tabs([
    dbc.Tab(layout_tab_01, label="PALMARES"),
    ])
