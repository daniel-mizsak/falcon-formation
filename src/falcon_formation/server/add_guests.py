"""
Dash app interface for adding guests to a specific practice.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import asyncio
import datetime

from dash import Dash, Input, Output, State, ctx, dash_table, dcc, html
from dash.exceptions import PreventUpdate

from falcon_formation.data_models import Guest, Position, Skill
from falcon_formation.main import database, holdsport_api, load_registered_guests, load_registered_members
from falcon_formation.server import parse_search_parameters, server

# TODO: Add a limit of how many guests will be used for team generation.
add_guests_app = Dash(__name__, server=server, url_base_pathname="/add_guests/")
add_guests_app.layout = html.Div(
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
        html.H2(id="registered-player-number-label", children="Currently registered player number:"),
        html.H2("Practice date:"),
        dcc.DatePickerSingle(
            id="practice-date-picker",
            first_day_of_week=1,
        ),
        html.Br(),
        html.H2("Player name:"),
        dcc.Input(
            id="player-name-input",
            className="dropdown-input",
            placeholder="Enter player name...",
            type="text",
        ),
        html.Br(),
        html.Br(),
        html.H2("Skill Level:"),
        dcc.Dropdown(
            id="player-skill-dropdown",
            className="dropdown-input",
            options=Skill.to_dropdown_options(),
            value=Skill.AVERAGE.score,
        ),
        html.Br(),
        html.H2("Position:"),
        dcc.Dropdown(
            id="player-position-dropdown",
            className="dropdown-input",
            options=Position.to_dropdown_options(),
            value=Position.FORWARD.value,
            multi=False,
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
        html.Br(),
        html.Br(),
        html.H2("Guests:"),
        dash_table.DataTable(
            id="guests-data-table",
            columns=[
                {"name": "Player Name", "id": "_id"},
                {"name": "Skill Level", "id": "skill"},
                {"name": "Primary position", "id": "position"},
            ],
            data=[],
            row_deletable=True,
        ),
    ],
)


@add_guests_app.callback(  # type:ignore[misc]
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
    team_id_value = parse_search_parameters(search).get("team_id")
    if team_id_value is None:
        return ("/", None)
    team_id = int(team_id_value)

    if not database.team_metadata_exists(team_id):
        return ("/", None)

    return (pathname, team_id)


@add_guests_app.callback(  # type: ignore[misc]
    [
        Output("registered-player-number-label", "children"),
        Output("loading-output", "children", allow_duplicate=True),
    ],
    [
        Input("team-id", "data"),
        Input("practice-date-picker", "date"),
    ],
    prevent_initial_call="initial_duplicate",
)
def update_registered_player_number_label(team_id: int, practice_date: datetime.date) -> tuple[str, None]:
    """Load and display the registered members and guests."""
    if not team_id or not practice_date:
        raise PreventUpdate

    guests = load_registered_guests(team_id, str(practice_date))
    members = load_registered_members(team_id, str(practice_date))
    registered_player_number_label = (
        "Currently registered player number: "
        f"{len(members) + len(guests)} (Members: {len(members)}, Guests: {len(guests)})"
    )
    return (registered_player_number_label, None)


@add_guests_app.callback(  # type: ignore[misc]
    [
        Output("practice-date-picker", "min_date_allowed"),
        Output("practice-date-picker", "max_date_allowed"),
        Output("practice-date-picker", "date"),
        Output("practice-date-picker", "disabled_days"),
        Output("loading-output", "children"),
    ],
    [
        Input("team-id", "data"),
    ],
)
def display_date_picker(
    team_id: int,
) -> tuple[
    datetime.date,
    datetime.date,
    datetime.date,
    list[datetime.date],
    None,
]:
    """Load and display upcoming practice dates."""
    if not team_id:
        raise PreventUpdate

    team_metadata = database.load_team_metadata(team_id)
    if team_metadata is None:
        raise PreventUpdate

    upcoming_practice_dates = asyncio.run(
        holdsport_api.get_upcoming_activity_dates(
            team_id=team_id,
            activity_name=team_metadata.activity_name,
            number_of_dates=2,
        ),
    )

    min_allowed_date = upcoming_practice_dates[0]
    max_allowed_date = upcoming_practice_dates[-1]
    initial_date = min_allowed_date

    disabled_days = []
    for i in range((max_allowed_date - min_allowed_date).days):
        date = min_allowed_date + datetime.timedelta(days=i)
        if date not in upcoming_practice_dates:
            disabled_days.append(date)

    return (min_allowed_date, max_allowed_date, initial_date, disabled_days, None)


@add_guests_app.callback(  # type: ignore[misc]
    [
        Output("submit-button", "disabled"),
    ],
    [
        Input("player-name-input", "value"),
        Input("player-skill-dropdown", "value"),
        Input("player-position-dropdown", "value"),
    ],
    [
        State("guests-data-table", "data"),
    ],
)
def update_submit_button_disabled_status(
    name: str,
    skill: int,
    position: str,
    data_table: list[dict[str, str]],
) -> tuple[bool]:
    """Make submit button disable if not all guest attributes are filled out or if there is a duplicate name."""
    if not all([name, skill, position]):
        return (True,)
    if name in [data["_id"] for data in data_table]:
        return (True,)
    return (False,)


@add_guests_app.callback(  # type: ignore[misc]
    [
        Output("submit-confirm", "displayed"),
        Output("submit-confirm", "message"),
    ],
    [
        Input("submit-button", "n_clicks"),
    ],
    [
        State("practice-date-picker", "date"),
        State("player-name-input", "value"),
        State("player-skill-dropdown", "value"),
        State("player-position-dropdown", "value"),
    ],
)
def update_submit_confirm_message(
    n_clicks: int,
    practice_date: datetime.date,
    name: str,
    skill: int,
    position: str,
) -> tuple[bool, str]:
    """Display a confirmation dialog before submitting new guest."""
    if n_clicks:
        confirmation_message = (
            f"Are you sure you want to submit the following data?\n\n"
            f"Practice Date: {practice_date}\n"
            f"Player Name: {name}\n"
            f"Skill Level: {Skill.get_description_from_value(skill)}\n"
            f"Position: {position}"
        )
        return (True, confirmation_message)
    return (False, "")


@add_guests_app.callback(  # type: ignore[misc]
    [
        Output("guests-data-table", "data"),
        Output("player-name-input", "value"),
        Output("player-skill-dropdown", "value"),
        Output("player-position-dropdown", "value"),
    ],
    [
        Input("practice-date-picker", "date"),
        Input("guests-data-table", "data"),
        Input("submit-confirm", "submit_n_clicks"),
    ],
    [
        State("team-id", "data"),
        State("player-name-input", "value"),
        State("player-skill-dropdown", "value"),
        State("player-position-dropdown", "value"),
    ],
)
def update_guests_data_table(  # noqa: PLR0913
    practice_date: datetime.date,
    data_table: list[dict[str, str]],
    confirm_n_clicks: int,
    team_id: int,
    name: str,
    skill: int,
    position: str,
) -> tuple[list[dict[str, str]], str, int, str]:
    """Update the guests data table and the database with new guest data."""
    if not team_id or not practice_date:
        raise PreventUpdate

    guests = database.load_guest_collection(team_id, str(practice_date))

    # Remove guest
    if ctx.triggered_id == "guests-data-table":
        for guest in guests:
            if guest.name not in {data["_id"] for data in data_table}:
                database.delete_guest(team_id, str(practice_date), guest)
                guests.remove(guest)
                break

    # Add guest
    if confirm_n_clicks and ctx.triggered_id == "submit-confirm":
        new_guest = Guest(name, skill, position)
        database.insert_guest(team_id, str(practice_date), new_guest)
        guests.append(new_guest)

        name = ""
        skill = Skill.AVERAGE.score
        position = Position.FORWARD.value

    data_table = [
        {
            "_id": guest.name,
            "skill": str(Skill.get_description_from_value(guest.skill)),
            "position": guest.position,
        }
        for guest in guests
    ]
    return data_table, name, skill, position
