"""
Dash app interface for adding extra players to the team.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import datetime
from pathlib import Path

from dash import Dash, Input, Output, State, ctx, dash_table, dcc, html
from dash.exceptions import PreventUpdate

from falcon_formation.data_models import Player
from falcon_formation.data_operations import load_config, load_team_data, save_team_data
from falcon_formation.holdsport_api import get_upcoming_practice_dates
from falcon_formation.server import available_teams, server

# Load configuration values
config_path = ".env"


add_guests_app = Dash(__name__, server=server, url_base_pathname="/add_guests/")
add_guests_app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=True),
        dcc.Store(id="redirect-flag", data=False),
        dcc.Loading(
            id="loading",
            className="loading",
            type="default",
            children=[
                html.Div(id="loading-output"),
            ],
        ),
        html.Label("Practice date:"),
        html.Br(),
        dcc.DatePickerSingle(
            id="practice-date-picker",
            first_day_of_week=1,
        ),
        html.Br(),
        html.Br(),
        html.Label("Player data:"),
        dash_table.DataTable(
            id="player-data-table",
            columns=[
                {"name": "Player Name", "id": "name"},
                {"name": "Skill Level", "id": "skill"},
                {"name": "Positions", "id": "positions"},
            ],
            data=[],
            row_deletable=True,
        ),
        html.Br(),
        html.Label("Player name:"),
        html.Br(),
        dcc.Input(
            id="player-name-input",
            className="player-input",
            placeholder="Enter player name...",
            type="text",
        ),
        html.Br(),
        html.Br(),
        html.Label("Skill Level:"),
        dcc.Dropdown(
            id="player-skill-dropdown",
            className="player-input",
            options=[{"label": v, "value": k} for k, v in Player.SKILL_OPTIONS.items()],
        ),
        html.Br(),
        html.Label("Positions:"),
        dcc.Dropdown(
            id="player-positions-dropdown",
            className="player-input",
            options=[{"label": v, "value": k} for k, v in Player.POSITION_OPTIONS.items()],
            multi=True,
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


@add_guests_app.callback(  # type: ignore[misc]
    [
        Output("url", "pathname"),
        Output("redirect-flag", "data"),
    ],
    [
        Input("url", "pathname"),
    ],
)
def redirect_invalid_url(pathname: str) -> tuple[str, bool]:
    """Redirect to the home page if the URL path is invalid."""
    team_name = pathname.split("/")[-1]
    if team_name not in available_teams:
        return "/", True
    return pathname, False


@add_guests_app.callback(  # type: ignore[misc]
    [
        Output("loading-output", "children"),
        Output("practice-date-picker", "min_date_allowed"),
        Output("practice-date-picker", "max_date_allowed"),
        Output("practice-date-picker", "date"),
        Output("practice-date-picker", "disabled_days"),
    ],
    [
        Input("redirect-flag", "data"),
        Input("url", "pathname"),
    ],
)
def update_date_picker(
    redirect_flag: bool,  # noqa: FBT001
    url_pathname: str,
) -> tuple[
    None,
    datetime.date,
    datetime.date,
    datetime.date,
    list[datetime.date],
]:
    """Update the date picker based on the practice dates of the team.

    Args:
        redirect_flag (bool): Flag indicating if the URL path is invalid.
        url_pathname (str): URL path containing the team name.

    Returns:
        tuple[None, datetime.date, datetime.date, datetime.date, list[datetime.date]]:
        Tuple containing loading, minimum allowed date, maximum allowed date, initial date, and disabled days.
    """
    if redirect_flag:
        raise PreventUpdate

    team_name = url_pathname.split("/")[-1]
    team_id, activity_name, auth, _ = load_config(config_path, team_name)
    upcoming_practice_dates = get_upcoming_practice_dates(team_id, auth, activity_name)

    min_allowed_date = upcoming_practice_dates[0]
    max_allowed_date = upcoming_practice_dates[-1]
    initial_date = min_allowed_date

    disabled_days = []
    for i in range((max_allowed_date - min_allowed_date).days):
        date = min_allowed_date + datetime.timedelta(days=i)
        if date not in upcoming_practice_dates:
            disabled_days.append(date)

    return None, min_allowed_date, max_allowed_date, initial_date, disabled_days


@add_guests_app.callback(  # type: ignore[misc]
    [
        Output("submit-button", "disabled"),
    ],
    [
        Input("player-name-input", "value"),
        Input("player-skill-dropdown", "value"),
        Input("player-positions-dropdown", "value"),
    ],
    [
        State("player-data-table", "data"),
    ],
)
def update_submit_button_disabled_status(
    name: str,
    skill: int,
    positions: list[str],
    data_table: list[dict[str, str]],
) -> tuple[bool]:
    """Make the submit button disabled if the player data is not complete.

    Args:
        name (str): Name of the player.
        skill (int): Skill level of the player.
        positions (list[str]): Positions played by the player.
        data_table (list[dict[str, str]]): Data table containing the player data.

    Returns:
        tuple[bool]: Tuple containing the disabled status of the submit button.
    """
    if not all([name, skill, positions]):
        return (True,)
    if name in [row["name"] for row in data_table]:
        return (True,)
    return (False,)


@add_guests_app.callback(  # type: ignore[misc]
    [
        Output("submit-confirm", "message"),
        Output("submit-confirm", "displayed"),
    ],
    [
        Input("submit-button", "n_clicks"),
    ],
    [
        State("practice-date-picker", "date"),
        State("player-name-input", "value"),
        State("player-skill-dropdown", "value"),
        State("player-positions-dropdown", "value"),
    ],
)
def update_submit_confirm_message(
    n_clicks: int,
    practice_date: datetime.date,
    name: str,
    skill: int,
    positions: list[str],
) -> tuple[str, bool]:
    """Create confirmation message for the submit button and update its content.

    Args:
        n_clicks (int): Number of clicks on the submit button.
        practice_date (datetime.date): Selected date of the practice.
        name (str): Name of the player.
        skill (int): Skill level of the player.
        positions (list[str]): Positions played by the player.

    Returns:
        tuple[str, bool]: Tuple containing the confirmation message and the displayed status of the confirmation dialog.
    """
    if n_clicks:
        player_tuple = Player(name, skill, tuple(positions)).to_tuple()
        confirmation_message = (
            f"Are you sure you want to submit the following data?\n\n"
            f"Practice Date: {practice_date}\n"
            f"Player Name: {player_tuple[0]}\n"
            f"Skill Level: {player_tuple[1]}\n"
            f"Positions: {player_tuple[2]}"
        )
        return confirmation_message, True
    return "", False


@add_guests_app.callback(  # type: ignore[misc]
    [
        Output("player-data-table", "data"),
        Output("player-name-input", "value"),
        Output("player-skill-dropdown", "value"),
        Output("player-positions-dropdown", "value"),
    ],
    [
        Input("redirect-flag", "data"),
        Input("practice-date-picker", "date"),
        Input("player-data-table", "data"),
        Input("submit-confirm", "submit_n_clicks"),
    ],
    [
        State("url", "pathname"),
        State("player-name-input", "value"),
        State("player-skill-dropdown", "value"),
        State("player-positions-dropdown", "value"),
    ],
)
def update_player_data_table(  # noqa: PLR0913
    redirect_flag: bool,  # noqa: FBT001
    practice_date: datetime.date,
    data_table: list[dict[str, str]],
    confirm_n_clicks: int,
    url_pathname: str,
    name: str,
    skill: int | None,
    positions: list[str],
) -> tuple[list[dict[str, str]], str, int | None, list[str]]:
    """Update the player data table and corresponding JSON file.

    Args:
        redirect_flag (bool): Flag indicating if the URL path is invalid
        practice_date (datetime.date): Selected date of the practice.
        data_table (list[dict[str, str]]): Data table containing the player data.
        confirm_n_clicks (int): Number of clicks on the confirmation button.
        url_pathname (str): URL path containing the team name.
        name (str): Name of the player.
        skill (int): Skill level of the player.
        positions (list[str]): Positions played by the player.

    Returns:
        tuple[list[dict[str, str]], str, list[str], int]: Updated data table and reset input values.
    """
    if redirect_flag or not practice_date:
        raise PreventUpdate

    team_name = url_pathname.split("/")[-1]
    extras_data_path = f"data/extras/{team_name.upper()}_{practice_date}.json"
    if not Path(extras_data_path).exists():
        save_team_data(extras_data_path, [])

    if ctx.triggered_id != "player-data-table":
        extra_players = load_team_data(extras_data_path)
    else:
        extra_players = [Player.from_tuple(tuple(row.values())) for row in data_table]  # type: ignore[arg-type]

    if confirm_n_clicks and ctx.triggered_id == "submit-confirm":
        extra_players.append(Player(name, skill, tuple(positions)))  # type: ignore[arg-type]
        name = ""
        positions = []
        skill = None

    save_team_data(extras_data_path, extra_players)
    data_table_values = [player.to_tuple() for player in extra_players]
    data_table = [
        {"name": name, "skill": skill, "positions": positions} for name, skill, positions in data_table_values
    ]
    return data_table, name, skill, positions
