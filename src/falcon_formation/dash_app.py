"""
Short description and source of base code.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import datetime
from pathlib import Path

from dash import Dash, Input, Output, State, ctx, dash_table, dcc, html

from falcon_formation.create_teams import Player
from falcon_formation.main import load_team_data, save_team_data


def convert_player_object_table_row(player: Player) -> dict[str, str]:
    position_options = [
        {"label": "Goalie", "value": "G"},
        {"label": "Left Defender", "value": "LD"},
        {"label": "Right Defender", "value": "RD"},
        {"label": "Left Wing", "value": "LW"},
        {"label": "Right Wing", "value": "RW"},
        {"label": "Center", "value": "C"},
    ]
    positions_text = ", ".join(
        [position["label"] for position in position_options if position["value"] in player.positions]
    )
    return {"name": player.name, "skill": player.skill, "positions": positions_text}


def convert_table_row_to_player_object(row: dict[str, str]) -> Player:
    position_options = [
        {"label": "Goalie", "value": "G"},
        {"label": "Left Defender", "value": "LD"},
        {"label": "Right Defender", "value": "RD"},
        {"label": "Left Wing", "value": "LW"},
        {"label": "Right Wing", "value": "RW"},
        {"label": "Center", "value": "C"},
    ]
    positions = [position["value"] for position in position_options if position["label"] in row["positions"]]
    return Player(row["name"], row["skill"], tuple(positions))


team_name = "Motion A"

starting_date = datetime.date(2024, 6, 1)
ending_date = datetime.date(2024, 6, 30)
enabled_day_numbers = [0, 2]

disabled_days = [
    starting_date + datetime.timedelta(days=day)
    for day in range((ending_date - starting_date).days + 1)
    if (starting_date + datetime.timedelta(days=day)).weekday() not in enabled_day_numbers
]
initial_date = (datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(hours=2)).date()
while initial_date in disabled_days:
    initial_date += datetime.timedelta(days=1)


app = Dash(__name__)
app.layout = html.Div(
    [
        dcc.DatePickerSingle(
            id="practice-date-picker",
            min_date_allowed=starting_date,
            max_date_allowed=ending_date,
            first_day_of_week=1,
            date=initial_date,
            disabled_days=disabled_days,
        ),
        html.Br(),
        dash_table.DataTable(
            id="table",
            columns=[
                {"name": "Player Name", "id": "name"},
                {"name": "Skill Level", "id": "skill"},
                {"name": "Positions", "id": "positions"},
            ],
            data=[],
            row_deletable=True,
        ),
        html.Label("Player name:"),
        html.Br(),
        dcc.Input(
            id="player-name-input",
            placeholder="Player Name",
            type="text",
        ),
        html.Br(),
        html.Label("Position:"),
        dcc.Dropdown(
            options=[
                {"label": "Goalie", "value": "G"},
                {"label": "Left Defender", "value": "LD"},
                {"label": "Right Defender", "value": "RD"},
                {"label": "Left Wing", "value": "LW"},
                {"label": "Right Wing", "value": "RW"},
                {"label": "Center", "value": "C"},
            ],
            multi=True,
            id="position-dropdown",
        ),
        html.Div(id="output-container-dropdown-1"),
        html.Br(),
        html.Label("Skill Level:"),
        dcc.Dropdown(
            options=[
                {"label": "Fairly Below Average", "value": 1},
                {"label": "Below Average", "value": 2},
                {"label": "Average", "value": 3},
                {"label": "Above Average", "value": 4},
                {"label": "Fairly Above Average", "value": 5},
            ],
            value="Medium",
            id="skill-level-dropdown",
        ),
        html.Br(),
        html.Button("Submit", id="submit-button", n_clicks=0),
        dcc.ConfirmDialog(
            id="confirm-submit",
        ),
    ],
)


@app.callback(
    Output("submit-button", "disabled"),
    Input("player-name-input", "value"),
    Input("position-dropdown", "value"),
    Input("skill-level-dropdown", "value"),
    State("table", "data"),
)
def update_button_disabled_status(
    player_name: str,
    positions: list[str],
    skill_level: int,
    data_table: list[dict[str, str]],
) -> bool:
    if player_name and positions and skill_level:
        if player_name in [row["name"] for row in data_table]:
            return True
        return False
    return True


@app.callback(
    Output("confirm-submit", "message"),
    Output("confirm-submit", "displayed"),
    Input("submit-button", "n_clicks"),
    State("table", "data"),
    State("player-name-input", "value"),
    State("position-dropdown", "value"),
    State("skill-level-dropdown", "value"),
    State("practice-date-picker", "date"),
)
def update_confirm_message(
    n_clicks: int,
    data_table: list[dict[str, str]],
    player_name: str,
    positions: list[str],
    skill_level: int,
    practice_date: datetime.date,
) -> tuple[str, bool]:
    if n_clicks:
        fields = [player_name, positions, skill_level, practice_date]
        if all(fields):
            if player_name in [row["name"] for row in data_table]:
                confirmation_message = f"Player name {player_name} is already in the list."
                return confirmation_message, True
            confirmation_message = (
                f"Are you sure you want to submit the following data?\nPlayer Name: {player_name}\n"
                f"Position: {positions}\nSkill Level: {skill_level}\nPractice Date: {practice_date}"
            )
            return confirmation_message, True
        for field in fields:
            if not field:
                confirmation_message = f"Please fill out field: {field}"
        return confirmation_message, True
    return "", False


@app.callback(
    Output("table", "data"),
    Input("table", "data"),
    Input("practice-date-picker", "date"),
    Input("confirm-submit", "submit_n_clicks"),
    State("player-name-input", "value"),
    State("position-dropdown", "value"),
    State("skill-level-dropdown", "value"),
)
def display_confirm_and_update_text(  # noqa: PLR0913
    data_table: list[dict[str, str]],
    practice_date: datetime.date,
    confirm_n_clicks: int,
    player_name: str,
    position: str,
    skill_level: int,
) -> str:
    extras_data_path = Path(f"data/extras/{practice_date}.json")
    if not extras_data_path.exists():
        save_team_data(extras_data_path, team_name, [])

    if ctx.triggered_id != "table":
        extra_players = load_team_data(extras_data_path, team_name)
    else:
        extra_players = [convert_table_row_to_player_object(row) for row in data_table]

    if confirm_n_clicks and ctx.triggered_id == "confirm-submit":
        extra_players.append(Player(player_name, skill_level, tuple(position)))

    for extra_player in extra_players:
        data_table.append(convert_player_object_table_row(player))
    save_team_data(extras_data_path, team_name, extra_players)
    return data_table


if __name__ == "__main__":
    app.run(debug=True)
