"""
Helper functions for creating equal hockey teams.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from itertools import combinations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path


@dataclass(frozen=True)
class Player:
    """Data class for storing player data."""

    name: str
    skill: int
    positions: frozenset[str]


@dataclass(eq=True, order=True, frozen=True)
class TeamMetrics:
    """Data class for storing team metrics."""

    skill_difference: int
    goalie_number_difference: int
    defense_number_difference: int


def load_team_data(team_data_path: Path, team_name: str) -> list[Player]:
    """Load team data from a JSON file.

    Args:
        team_data_path (Path): Path to the JSON file.
        team_name (str): Name of the team within the JSON file. One JSON file may contain multiple teams.

    Returns:
        list[Player]: List of Player objects, where each element represents a player in the team.
    """
    with team_data_path.open("r", encoding="utf-8") as file_handle:
        json_data = json.load(file_handle)[team_name]

    team_data = []
    for player_name in json_data:
        player = Player(
            name=str(player_name),
            skill=int(json_data[player_name]["skill"]),
            positions=frozenset(json_data[player_name]["positions"]),
        )
        team_data.append(player)
    return team_data


def generate_every_team_combination(players: list[Player]) -> Generator[tuple[set[Player], set[Player]], None, None]:
    """Generate every possible team combination from a list of players.

    The teams always have the same number of players.
    Or the difference is at most 1 in case of an odd number of players.

    Args:
        players (list[Player]): List of Player objects to create teams from.

    Yields:
        Generator[tuple[set[Player], set[Player]], None, None]: The two teams containing sets of Player objects.
    """
    for team_1_tuple in combinations(players, len(players) // 2):
        team_1 = set(team_1_tuple)
        team_2 = {player for player in players if player not in team_1}

        yield (team_1, team_2)


def calculate_team_metrics(teams: tuple[set[Player], set[Player]]) -> TeamMetrics:
    """Calculate team metrics based on the given teams.

    Args:
        teams (tuple[set[Player], set[Player]]): The two teams containing sets of Player objects.

    Returns:
        TeamMetrics: TeamMetrics object containing the calculated metrics for the given teams.
    """
    return TeamMetrics(
        skill_difference=_calculate_skill_level_difference(teams),
        goalie_number_difference=_calculate_goalie_number_difference(teams),
        defense_number_difference=_calculate_defense_number_difference(teams),
    )


def _calculate_skill_level_difference(teams: tuple[set[Player], set[Player]]) -> int:
    total_team_skills = []
    for team in teams:
        total_team_skill = 0
        for player in team:
            total_team_skill += player.skill
        total_team_skills.append(total_team_skill)

    return abs(total_team_skills[0] - total_team_skills[1])


def _calculate_goalie_number_difference(teams: tuple[set[Player], set[Player]]) -> int:
    total_goalie_numbers = []
    for team in teams:
        total_goalie_number = 0
        for player in team:
            if "G" in player.positions:
                total_goalie_number += 1
        total_goalie_numbers.append(total_goalie_number)

    return abs(total_goalie_numbers[0] - total_goalie_numbers[1])


def _calculate_defense_number_difference(teams: tuple[set[Player], set[Player]]) -> int:
    total_defense_numbers = []
    for team in teams:
        total_defense_number = 0
        for player in team:
            if set(player.positions).intersection({"RD", "LD"}):
                total_defense_number += 1
        total_defense_numbers.append(total_defense_number)

    return abs(total_defense_numbers[0] - total_defense_numbers[1])


def assign_me_to_team_red(teams: tuple[set[Player], set[Player]], my_name: str) -> tuple[list[Player], list[Player]]:
    """Assign the player with the given name to the red team.

    Args:
        teams (tuple[set[Player], set[Player]]): The two teams containing sets of Player objects.
        my_name (str): The name of the player to assign to the red team.

    Returns:
        tuple[list[Player], list[Player]]: The two teams as sorted lists of Player objects.
    """
    i_am_in_team_zero = any(player.name == my_name for player in teams[0])
    team_red = sorted(teams[0] if i_am_in_team_zero else teams[1], key=lambda player: player.name)
    team_green = sorted(teams[1] if i_am_in_team_zero else teams[0], key=lambda player: player.name)
    return team_red, team_green
