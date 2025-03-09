"""
Dash app interface for registering the winner of a specific practice.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from dash import Dash, Input, Output, dcc, html

from falcon_formation.server import database, parse_search_parameters, server

register_winner_app = Dash(__name__, server=server, url_base_pathname="/register_winner/")
register_winner_app.layout = html.Div(
    [
        # Metadata
        dcc.Location(id="url", refresh=True),
        dcc.Store(id="team-id", data=None),
        dcc.Loading(
            id="loading",
            className="loading",
            type="default",
            children=[
                html.Div(id="loading-output"),
            ],
        ),
        # Layout
        html.H2(id="register-winner-title"),
        dcc.Dropdown(
            id="winner-input-dropdown",
            className="dropdown-input",
        ),
        html.Br(),
        html.Button(
            "Submit",
            id="submit-button",
            className="submit-button",
            n_clicks=0,
        ),
        dcc.ConfirmDialog(
            id="submit-confirm",
        ),
    ],
)


@register_winner_app.callback(  # type:ignore[misc]
    [
        Output("url", "pathname"),
        Output("team-id", "data"),
    ],
    [
        Input("url", "pathname"),
        Input("url", "search"),
    ],
)
def redirect_invalid_url(pathname: str, search: str) -> tuple[str, int | None]:
    """Redirect to the main page if cannot validate team id against the database."""
    team_id = parse_search_parameters(search)
    if team_id is None:
        return ("/", None)

    if not database.team_metadata_exists(team_id):
        return ("/", None)

    return (pathname, team_id)
