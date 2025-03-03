"""
Dash app interface for editing players in a team.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import asyncio

from dash import Dash, Input, Output, State, dash_table, dcc, html
from dash.exceptions import PreventUpdate

from falcon_formation.data_models import Member, Position, Skill
from falcon_formation.server import database, holdsport_api, parse_search_parameters, server

edit_team_app = Dash(__name__, server=server, url_base_pathname="/edit_team/")
edit_team_app.layout = html.Div(
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
        html.H2("Members"),
        dash_table.DataTable(
            id="members-data-table",
            columns=[
                {"name": "Player ID", "id": "_id", "editable": False},
                {"name": "Player Name", "id": "name", "editable": False},
                {"name": f"Skill Level (Between {Skill.MINIMUM.score} and {Skill.MAXIMUM.score})", "id": "skill"},
                {"name": "Primary position", "id": "position", "presentation": "dropdown"},
            ],
            data=[],
            hidden_columns=["_id"],
            editable=True,
            style_cell_conditional=[{"if": {"column_id": c}, "textAlign": "left"} for c in ["position"]],
            dropdown={
                "position": {
                    "options": Position.to_dropdown_options(),
                    "clearable": False,
                },
            },
        ),
        html.Button(
            "Sync Members",
            id="sync-members-button",
            className="submit-button",
            n_clicks=0,
        ),
        # TODO: Create confirm dialog about the added/removed players
    ],
)


@edit_team_app.callback(  # type:ignore[misc]
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


@edit_team_app.callback(  # type:ignore[misc]
    [
        Output("members-data-table", "data"),
    ],
    [
        Input("team-id", "data"),
    ],
)
def display_members_data_table(team_id: int) -> tuple[list[dict[str, str]],]:
    """Load and display the members of the team."""
    if not team_id:
        raise PreventUpdate

    members = database.load_member_collection(team_id)
    data_table = [member.to_dict() for member in members]
    data_table.sort(key=lambda x: x["name"])
    return (data_table,)


@edit_team_app.callback(  # type: ignore[misc]
    [
        Output("members-data-table", "data", allow_duplicate=True),
    ],
    [
        Input("members-data-table", "data_timestamp"),
    ],
    [
        State("team-id", "data"),
        State("members-data-table", "data"),
        State("members-data-table", "data_previous"),
    ],
    prevent_initial_call=True,
)
def update_members_data_table(
    data_table_timestamp: str,
    team_id: int,
    data_table: list[dict[str, str]],
    data_table_previous: list[dict[str, str]],
) -> tuple[list[dict[str, str]],]:
    """Check if the proposed change is valid and if so update the database and the data table."""
    if not team_id or not data_table_timestamp:
        raise PreventUpdate

    updated_member = validate_members_data_table(data_table, data_table_previous)

    if updated_member:
        # At Player initialization skill is adjusted to the limits. If it changes it needs to be updated.
        for data in data_table:
            if int(data["_id"]) == updated_member._id:  # noqa: SLF001
                data["skill"] = str(updated_member.skill)
        database.update_member(team_id, updated_member)
        return (data_table,)
    return (data_table_previous,)


@edit_team_app.callback(  # type: ignore[misc]
    [
        Output("members-data-table", "data", allow_duplicate=True),
        Output("loading-output", "children"),
    ],
    [
        Input("sync-members-button", "n_clicks"),
    ],
    [
        State("team-id", "data"),
    ],
    prevent_initial_call=True,
)
def sync_members_with_team_data(n_clicks: int, team_id: int) -> tuple[list[dict[str, str]], None]:
    """Sync the members of the team with the Holdsport API."""
    if not n_clicks:
        raise PreventUpdate

    members = database.load_member_collection(team_id)
    holdsport_members = asyncio.run(holdsport_api.get_users_in_team(team_id))

    # Add new members to the team
    for holdsport_member in holdsport_members:
        if not database.member_exists(team_id, int(holdsport_member["_id"])):
            database.insert_member(team_id, Member.from_dict(holdsport_member))
            members.append(Member.from_dict(holdsport_member))

    data_table = [member.to_dict() for member in members]
    data_table.sort(key=lambda x: x["name"])
    return (data_table, None)


def validate_members_data_table(
    data_table: list[dict[str, str]],
    data_table_previous: list[dict[str, str]],
) -> Member | None:
    """Validate the members data table."""
    # TODO: I am not sure the change can be invalid anymore.
    for data, data_previous in zip(data_table, data_table_previous, strict=True):
        if data == data_previous:
            continue
        try:
            member = Member.from_dict(data)
        except (ValueError, TypeError):
            return None
        else:
            return member
    return None
