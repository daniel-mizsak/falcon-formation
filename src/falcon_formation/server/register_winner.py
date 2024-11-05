"""
Info.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from dash import Dash, html

from falcon_formation.server import server

register_winner_app = Dash(__name__, server=server, url_base_pathname="/register_winner/")
register_winner_app.layout = html.Div(
    [
        html.H1("Register Winner"),
    ],
)
