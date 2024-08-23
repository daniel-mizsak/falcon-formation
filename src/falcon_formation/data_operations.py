"""
Functions for interacting with the saved data files.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import json
import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import dotenv_values

from falcon_formation import STATUS_CODE_OK
from falcon_formation.data_models import Player


def load_config(config_path: str, team_name: str) -> tuple[int, str, tuple[str, str]]:
    """Load configuration values from a .env file or environment variables.

    Args:
        config_path (str): Path to the .env file.
        team_name (str): Prefix of the team-specific configuration values.

    Returns:
        tuple[int, str, tuple[str, str], str]:
        TEAM_ID, ACTIVITY_NAME, (HOLDSPORT_USERNAME, HOLDSPORT_PASSWORD), ENCRYPTION_KEY
    """
    config = dotenv_values(config_path)
    team_prefix = team_name.upper() + "_"
    if not config:
        config = dict(os.environ)
        team_prefix = ""

    team_id = int(str(config[team_prefix + "TEAM_ID"]))
    activity_name = str(config[team_prefix + "ACTIVITY_NAME"])
    auth = (str(config["HOLDSPORT_USERNAME"]), str(config["HOLDSPORT_PASSWORD"]))
    encryption_key = str(config[team_prefix + "ENCRYPTION_KEY"])

    return team_id, activity_name, auth, encryption_key


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


def save_team_data_from_csv(team_data_path: str) -> None:  # TODO: Maybe rename to convert?
    """Save team data to a JSON file from a CSV file.

    Args:
        team_data_path (str): Path to the JSON file.
    """
    dataframe = pd.read_csv(team_data_path)
    print("Players with missing skill level:")  # noqa: T201
    print(dataframe["name"][dataframe["skill"] == 0])  # noqa: T201

    print("Players with missing positions:")  # noqa: T201
    print(dataframe["name"][dataframe["positions"].isna()])  # noqa: T201

    dataframe = dataframe[(dataframe["skill"] != 0) & (dataframe["positions"].notna())]
    team_data = {}
    for _, row in dataframe.iterrows():
        positions = row["positions"].replace(" ", "").split(",")
        team_data[row["name"]] = {"skill": row["skill"], "positions": positions}

    with Path(team_data_path.replace(".csv", ".json")).open("w", encoding="utf-8") as file_handle:
        json.dump(team_data, file_handle, ensure_ascii=False, indent=2)
