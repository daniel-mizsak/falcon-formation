"""
Main module of the Falcon Formation application.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

from dotenv import dotenv_values

from falcon_formation.create_teams import (
    Player,
    choose_best_team,
    generate_output,
    get_players,
    load_team_data,
)
from falcon_formation.holdsport_api import get_registered_players


def falcon_formation() -> str:
    """Run Falcon Formation.

    Returns:
        str: The output text containing all the relevant information about the generated teams.
    """
    # Load configuration values
    config = dotenv_values(".env")
    if not config:
        config = dict(os.environ)

    date = str((datetime.now(tz=UTC) + timedelta(hours=2)).date())
    team_id = int(str(config["TEAM_ID"]))
    team_name = str(config["TEAM_NAME"])
    auth = (str(config["HOLDSPORT_USERNAME"]), str(config["HOLDSPORT_PASSWORD"]))

    # Load team data and query registered players
    team_data_path = Path("data/team.json")
    team_data = load_team_data(team_data_path, team_name)
    registered_players = get_registered_players(team_id, date, auth)

    # Get players
    players, unknown_players, players_with_missing_data = get_players(team_data, registered_players)
    # TODO: Add easy option to add extra players

    # Extra players
    extra_players: list[Player] = [
        # Player(name="name", skill=3, positions=("G")),  # noqa: ERA001
        Player(name="Magnus's Guest", skill=3, positions=frozenset()),
        Player(name="Nikolaj", skill=3, positions=frozenset({"G"})),
    ]
    players.extend(extra_players)

    # Randomly choose one of the best team combinations
    best_team = choose_best_team(players)

    # Create output
    return generate_output(date, best_team, players_with_missing_data, unknown_players)
