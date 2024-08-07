"""
Dash app interface for adding extra players to the team.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import datetime
from pathlib import Path

from dash import Dash, Input, Output, State, ctx, dash_table, dcc, html
from flask import Flask, Response, send_file

from falcon_formation.data_models import Player
from falcon_formation.main import load_team_data, save_team_data

team_name = "Motion A"  # TODO: Use team name from the main app.

starting_date = datetime.date(2024, 7, 1)
ending_date = datetime.date(2024, 7, 31)
enabled_day_numbers = [0, 1, 2, 3]  # TODO: Change to the days of the week when the practice is held.

disabled_days = [
    starting_date + datetime.timedelta(days=day)
    for day in range((ending_date - starting_date).days + 1)
    if (starting_date + datetime.timedelta(days=day)).weekday() not in enabled_day_numbers
]
initial_date = (datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(hours=2)).date()
while initial_date in disabled_days:
    initial_date += datetime.timedelta(days=1)


server = Flask(__name__)
app = Dash(__name__, server=server, url_base_pathname="/dash/")
app.layout = html.Div(
    [
        html.Label("Practice date:"),
        html.Br(),
        dcc.DatePickerSingle(
            id="practice-date-picker",
            min_date_allowed=starting_date,
            max_date_allowed=ending_date,
            first_day_of_week=1,
            date=initial_date,
            disabled_days=disabled_days,
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


@app.callback(  # type: ignore[misc]
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


@app.callback(  # type: ignore[misc]
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


@app.callback(  # type: ignore[misc]
    [
        Output("player-data-table", "data"),
        Output("player-name-input", "value"),
        Output("player-skill-dropdown", "value"),
        Output("player-positions-dropdown", "value"),
    ],
    [
        Input("practice-date-picker", "date"),
        Input("player-data-table", "data"),
        Input("submit-confirm", "submit_n_clicks"),
    ],
    [
        State("player-name-input", "value"),
        State("player-skill-dropdown", "value"),
        State("player-positions-dropdown", "value"),
    ],
)
def update_player_data_table(  # noqa: PLR0913
    practice_date: datetime.date,
    data_table: list[dict[str, str]],
    confirm_n_clicks: int,
    name: str,
    skill: int | None,
    positions: list[str],
) -> tuple[list[dict[str, str]], str, int | None, list[str]]:
    """Update the player data table and corresponding JSON file.

    Args:
        practice_date (datetime.date): Selected date of the practice.
        data_table (list[dict[str, str]]): Data table containing the player data.
        confirm_n_clicks (int): Number of clicks on the confirmation button.
        name (str): Name of the player.
        skill (int): Skill level of the player.
        positions (list[str]): Positions played by the player.

    Returns:
        tuple[list[dict[str, str]], str, list[str], int]: Updated data table and reset input values.
    """
    extras_data_path = f"data/extras/{practice_date}.json"
    if not Path(extras_data_path).exists():
        save_team_data(extras_data_path, team_name, [])

    if ctx.triggered_id != "player-data-table":
        extra_players = load_team_data(extras_data_path, team_name)
    else:
        extra_players = [Player.from_tuple(tuple(row.values())) for row in data_table]  # type: ignore[arg-type]

    if confirm_n_clicks and ctx.triggered_id == "submit-confirm":
        extra_players.append(Player(name, skill, tuple(positions)))  # type: ignore[arg-type]
        name = ""
        positions = []
        skill = None

    save_team_data(extras_data_path, team_name, extra_players)
    data_table_values = [player.to_tuple() for player in extra_players]
    data_table = [
        {"name": name, "skill": skill, "positions": positions} for name, skill, positions in data_table_values
    ]
    return data_table, name, skill, positions


@server.route("/extras/<date>")
def serve_json(date: str) -> Response:
    """Serve the JSON file containing the extra players for the given date.

    Args:
        date (str): Date of the practice.

    Returns:
        Response: JSON file containing the extra players for the given date.
    """
    file_path = Path(f"data/extras/{date}.json").resolve()
    return send_file(file_path, mimetype="application/json")


if __name__ == "__main__":
    server.run(host="0.0.0.0")
