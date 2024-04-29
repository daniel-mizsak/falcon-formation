"""
Update skill level of individual players based on the outcome of the game.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import json
from pathlib import Path

from falcon_formation.create_teams import Player


def update_players_skill(team_data: list[Player], update_values: dict[str, int]) -> list[Player]:
    """_summary_.

    Args:
        team_data (list[Player]): _description_
        update_values (dict[str, int]): _description_

    Returns:
        list[Player]: _description_
    """
    updated_team_data = []
    for player in team_data:
        if player.name in update_values:
            updated_player = Player(
                name=player.name,
                skill=player.skill + update_values[player.name],
                positions=player.positions,
            )
            updated_team_data.append(updated_player)
        else:
            updated_team_data.append(player)

    return updated_team_data


def save_team_data(team_data_path: Path, team_name: str, players: list[Player]) -> None:
    """Save team data to a JSON file.

    Args:
        team_data_path (Path): Path to the JSON file.
        team_name (str): Name of the team within the JSON file. One JSON file may contain multiple teams.
        players (List[Player]): List of Player objects, where each element represents a player in the team.
    """
    team_data = {}
    for player in players:
        team_data[player.name] = {"skill": player.skill, "positions": list(player.positions)}

    with team_data_path.open("w", encoding="utf-8") as file_handle:
        json.dump({team_name: team_data}, file_handle, ensure_ascii=False, indent=2)
