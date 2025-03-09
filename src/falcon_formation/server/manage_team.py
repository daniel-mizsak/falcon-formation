"""
Dash app interface managing team metadata.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import asyncio

from dash import Dash, Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from falcon_formation.data_models import TeamMetadata
from falcon_formation.server import database, holdsport_api, parse_search_parameters, server  # TODO: Add telegram API

manage_team_app = Dash(__name__, server=server, url_base_pathname="/manage_team/")
manage_team_app.layout = html.Div(
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
        html.H2("Team Metadata"),
        html.P("Activity name:"),
        dcc.Dropdown(
            id="activity-name-dropdown",
            className="dropdown-input",
            options=[],
            value="",
            multi=False,
            clearable=False,
        ),
        html.Br(),
        html.P("Jersey color for the first team:"),
        dcc.Input(
            id="jersey-color-1-input",
            className="dropdown-input",
            type="text",
            placeholder="Jersey Color 1",
        ),
        html.Br(),
        html.P("Jersey color for the second team:"),
        dcc.Input(
            id="jersey-color-2-input",
            className="dropdown-input",
            type="text",
            placeholder="Jersey Color 2",
        ),
        html.Br(),
        html.P("Telegram Chat ID:  (Can be obtained through the Telegram API)"),
        dcc.Input(
            id="telegram-chat-id-input",
            className="dropdown-input",
            type="number",
            placeholder="Telegram Chat ID",
        ),
        html.Button(
            "Update",
            id="update-button",
            className="submit-button",
            n_clicks=0,
        ),
        dcc.ConfirmDialog(
            id="update-confirm",
            message="Team metadata updated!",
        ),
    ],
)


@manage_team_app.callback(  # type:ignore[misc]
    [
        Output("url", "pathname"),
        Output("team-id", "data"),
        Output("loading-output", "children", allow_duplicate=True),
    ],
    [
        Input("url", "pathname"),
        Input("url", "search"),
    ],
    prevent_initial_call="initial_duplicate",
)
def redirect_invalid_url(pathname: str, search: str) -> tuple[str, int | None, None]:
    """Redirect to the main page if cannot validate team id against the database or Holdsport API."""
    team_id = parse_search_parameters(search)
    if team_id is None:
        return ("/", None, None)

    if database.team_metadata_exists(team_id):
        return (pathname, team_id, None)

    holdsport_teams = asyncio.run(holdsport_api.get_teams())
    for holdsport_team in holdsport_teams:
        if int(holdsport_team["_id"]) == team_id:
            team_metadata = TeamMetadata.from_dict(holdsport_team)
            database.insert_team_metadata(team_metadata)
            return (pathname, team_id, None)
    return ("/", None, None)


@manage_team_app.callback(  # type:ignore[misc]
    [
        Output("activity-name-dropdown", "options"),
        Output("activity-name-dropdown", "value"),
        Output("jersey-color-1-input", "value"),
        Output("jersey-color-2-input", "value"),
        Output("telegram-chat-id-input", "value"),
        Output("loading-output", "children", allow_duplicate=True),
    ],
    [
        Input("team-id", "data"),
    ],
    prevent_initial_call=True,
)
def display_team_metadata(team_id: int) -> tuple[list[dict[str, str]], str, str, str, int, None]:
    """Load and display the metadata of the team.

    Also makes sure that the activity name is in the list of possible activity names.
    """
    if not team_id:
        raise PreventUpdate

    team_metadata = database.load_team_metadata(team_id)
    if team_metadata is None:
        raise PreventUpdate

    # Get list of possible activity names and populate the dropdown
    activity_names = asyncio.run(holdsport_api.get_activity_names_with_minimum_occurrences(team_id))
    activity_name_dropdown_options = [{"label": name, "value": name} for name in activity_names]

    if team_metadata.activity_name not in activity_names:
        team_metadata.activity_name = activity_names[0]
    database.update_team_metadata(team_metadata)

    return (
        activity_name_dropdown_options,
        team_metadata.activity_name,
        team_metadata.jersey_color_1,
        team_metadata.jersey_color_2,
        team_metadata.telegram_chat_id,
        None,
    )


@manage_team_app.callback(  # type:ignore[misc]
    [
        Output("update-confirm", "displayed"),
    ],
    [
        Input("update-button", "n_clicks"),
    ],
    [
        State("team-id", "data"),
        State("activity-name-dropdown", "value"),
        State("jersey-color-1-input", "value"),
        State("jersey-color-2-input", "value"),
        State("telegram-chat-id-input", "value"),
    ],
)
def update_team_metadata(  # noqa: PLR0913
    n_clicks: int,
    team_id: int,
    activity_name: str,
    jersey_color_1: str,
    jersey_color_2: str,
    telegram_chat_id: int,
) -> tuple[bool]:
    """Update the metadata of the team in the database."""
    if n_clicks > 0:
        team_metadata = database.load_team_metadata(team_id)
        if team_metadata is None:
            return (False,)

        team_metadata.activity_name = activity_name
        team_metadata.jersey_color_1 = jersey_color_1.strip()
        team_metadata.jersey_color_2 = jersey_color_2.strip()
        team_metadata.telegram_chat_id = telegram_chat_id

        save_team_metadata_result = database.update_team_metadata(team_metadata)
        if save_team_metadata_result.modified_count > 0:
            return (True,)
    return (False,)
