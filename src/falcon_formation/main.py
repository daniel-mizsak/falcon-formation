"""
Main module of the Falcon Formation application.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

import requests
from dotenv import dotenv_values

from falcon_formation import STATUS_CODE_OK
from falcon_formation.create_teams import choose_best_team, generate_output
from falcon_formation.data_models import Player

# from falcon_formation.create_teams import get_players # noqa: ERA001
# from falcon_formation.holdsport_api import get_registered_players # noqa: ERA001


def falcon_formation(team_name: str) -> str:
    """Run Falcon Formation.

    Args:
        team_name (str): Name of the team.

    Returns:
        str: The output text containing all the relevant information about the generated teams.
    """
    # Load configuration values
    config_path = ".env"
    team_id, activity_name, auth = load_config(config_path, team_name)
    date = str((datetime.now(tz=UTC) + timedelta(hours=2)).date())

    # Load team data and query registered players
    # team_data_path = f"data/{team_name.upper()}.json"  # noqa: ERA001
    # team_data = load_team_data(team_data_path)  # noqa: ERA001
    # registered_players = get_registered_players(team_id, date, auth, activity_name)  # noqa: ERA001

    # Get players
    # players, unknown_players, players_with_missing_data = get_players(team_data, registered_players)  # noqa: ERA001
    players: list[Player] = []
    unknown_players: list[str] = []
    players_with_missing_data: list[str] = []

    # Extra players
    extras_data_path = f"https://falcon-formation.pythonvilag.hu/extras/{team_name}/{date}"
    extra_players = load_team_data(extras_data_path)
    players.extend(extra_players)

    # Randomly choose one of the best team combinations
    best_team = choose_best_team(players)

    # Create output
    return generate_output(date, best_team, players_with_missing_data, unknown_players)


def load_config(config_path: str, team_name: str) -> tuple[int, str, tuple[str, str]]:
    """Load configuration values from a .env file or environment variables.

    Args:
        config_path (str): Path to the .env file.
        team_name (str): Prefix of the team-specific configuration values.

    Returns:
        tuple[int, str, tuple[str, str]]: Team ID, activity name, and authentication data.
    """
    config = dotenv_values(config_path)
    if not config:
        config = dict(os.environ)

    team_prefix = team_name.upper() + "_"

    team_id = int(str(config[team_prefix + "TEAM_ID"]))
    activity_name = str(config[team_prefix + "ACTIVITY_NAME"])
    auth = (str(config["HOLDSPORT_USERNAME"]), str(config["HOLDSPORT_PASSWORD"]))

    return team_id, activity_name, auth


def load_team_data(team_data_path: str) -> list[Player]:
    """Load team data from a JSON file.

    Args:
        team_data_path (str): Path or URL to the JSON file.

    Returns:
        list[Player]: List of Player objects, where each element represents a player in the team.
    """
    if team_data_path.startswith("http"):
        try:
            response = requests.get(url=team_data_path, timeout=10)
            if response.status_code != STATUS_CODE_OK:
                return []
            json_data = json.loads(response.text)
        except requests.exceptions.ConnectionError:
            return []
    else:
        with Path(team_data_path).open("r", encoding="utf-8") as file_handle:
            json_data = json.load(file_handle)

    team_data = []
    for player_name in json_data:
        player = Player(
            name=str(player_name),
            skill=int(json_data[player_name]["skill"]),
            positions=tuple(json_data[player_name]["positions"]),
        )
        team_data.append(player)
    return team_data


def save_team_data(team_data_path: str, players: list[Player]) -> None:
    """Save team data to a JSON file.

    Args:
        team_data_path (str): Path to the JSON file.
        players (List[Player]): List of Player objects, where each element represents a player in the team.
    """
    team_data = {}
    for player in players:
        team_data[player.name] = {"skill": player.skill, "positions": list(player.positions)}

    with Path(team_data_path).open("w", encoding="utf-8") as file_handle:
        json.dump(team_data, file_handle, ensure_ascii=False, indent=2)
