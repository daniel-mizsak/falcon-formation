"""
Short description and source of base code.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import datetime

from dash import Dash, Input, Output, State, dcc, html


def get_initial_date_and_disabled_days(
    starting_date: datetime.date,
    ending_date: datetime.date,
    enabled_day_numbers: list[int],
) -> tuple[datetime.date, list[datetime.date]]:
    """_summary_.

    Args:
        starting_date (datetime.date): _description_
        ending_date (datetime.date): _description_
        enabled_day_numbers (list[int]): _description_

    Returns:
        tuple[datetime.date, list[datetime.date]]: _description_
    """
    disabled_days = [
        starting_date + datetime.timedelta(days=day)
        for day in range((ending_date - starting_date).days + 1)
        if (starting_date + datetime.timedelta(days=day)).weekday() not in enabled_day_numbers
    ]
    initial_date = (datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(hours=2)).date()
    while initial_date in disabled_days:
        initial_date += datetime.timedelta(days=1)
    return initial_date, disabled_days


starting_date = datetime.date(2024, 6, 1)
ending_date = datetime.date(2024, 6, 30)
enabled_day_numbers = [0, 2]
initial_date, disabled_days = get_initial_date_and_disabled_days(starting_date, ending_date, enabled_day_numbers)


app = Dash(__name__)
app.layout = html.Div(
    [
        dcc.Input(
            id="player-name-input",
            placeholder="Player Name",
            type="text",
        ),
        html.Br(),
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
        dcc.DatePickerSingle(
            id="practice-date-picker",
            min_date_allowed=starting_date,
            max_date_allowed=ending_date,
            first_day_of_week=1,
            date=initial_date,
            disabled_days=disabled_days,
        ),
        html.Div(id="output-data"),
        html.Br(),
        html.Button("Submit", id="submit-button", n_clicks=0),
        dcc.ConfirmDialog(
            id="confirm-submit",
        ),
    ],
)


@app.callback(
    Output("confirm-submit", "message"),
    Output("confirm-submit", "displayed"),
    Input("submit-button", "n_clicks"),
    State("position-dropdown", "value"),
    State("skill-level-dropdown", "value"),
    State("practice-date-picker", "date"),
    State("player-name-input", "value"),
    prevent_initial_call=True,
)
def update_confirm_message(
    n_clicks: int,
    player_name: str,
    positions: list[str],
    skill_level: int,
    practice_date: datetime.date,
) -> tuple[str, bool]:
    """_summary_.

    Args:
        n_clicks (int): _description_
        player_name (str): _description_
        positions (list[str]): _description_
        skill_level (int): _description_
        practice_date (datetime.date): _description_

    Returns:
        tuple[str, bool]: _description_
    """
    if n_clicks:
        if all([player_name, positions, skill_level, practice_date]):
            confirmation_message = (
                f"Are you sure you want to submit the following data?\nPlayer Name: {player_name}, "
                f"Position: {positions}, Skill Level: {skill_level}, Practice Date: {practice_date}"
            )
            return confirmation_message, True
        confirmation_message = "Please fill out all fields"
        return confirmation_message, True
    return "", False


@app.callback(
    Output("output-data", "children"),
    Input("confirm-submit", "submit_n_clicks"),
    State("player-name-input", "value"),
    State("position-dropdown", "value"),
    State("skill-level-dropdown", "value"),
    State("practice-date-picker", "date"),
    prevent_initial_call=True,
)
def display_confirm_and_update_text(
    confirm_n_clicks: int,
    player_name: str,
    position: str,
    skill_level: int,
    practice_date: datetime.date,
) -> str:
    """_summary_.

    Args:
        confirm_n_clicks (int): _description_
        player_name (str): _description_
        position (str): _description_
        skill_level (int): _description_
        practice_date (datetime.date): _description_

    Returns:
        str: _description_
    """
    if confirm_n_clicks:
        return (
            f"Player Name: {player_name}, Position: {position}, Skill Level: {skill_level}, "
            f"Practice Date: {practice_date}"
        )
    return "Aborted..."


if __name__ == "__main__":
    app.run(debug=True)
