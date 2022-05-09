from dash import Dash

import dash_bootstrap_components as dbc

import os

external_stylesheets = [dbc.themes.BOOTSTRAP, os.path.join(os.getcwd(), "dashboard/assets/style.css")]

app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=external_stylesheets)
