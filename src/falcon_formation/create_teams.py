"""
Helper functions for creating equal hockey teams.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from __future__ import annotations

import random
from itertools import combinations
from typing import TYPE_CHECKING

from falcon_formation.data_models import Player, TeamData, TeamDistribution, TeamMetrics

if TYPE_CHECKING:
    from collections.abc import Generator


def get_players(team_data: list[Player], registered_players: list[str]) -> tuple[list[Player], list[str], list[str]]:
    """Return the players to generate teams from.

    Also returns players who are not part of the team data and players with missing data.

    Args:
        team_data (list[Player]): List of Player objects, where each element represents a player in the team.
        registered_players (list[str]): The list of the names of the players who registered for the practice.

    Returns:
        tuple[list[Player], list[str], list[str]]: A tuple containing the players to generate teams from.
        Also return players who are registered, but not present in team_data as unknown players,
        and players whose team_data is incomplete.
    """
    players: list[Player] = []
    unknown_players: list[str] = []
    players_with_missing_data: list[str] = []
    for player_name in registered_players:
        player = next((player for player in team_data if player.name == player_name), None)
        if player:
            players.append(player)
            if not player.skill or not player.positions:
                players_with_missing_data.append(player_name)
        else:
            players.append(Player(name=player_name, skill=3, positions=()))
            unknown_players.append(player_name)

    return players, unknown_players, players_with_missing_data


def choose_best_team(players: list[Player]) -> TeamData:
    """Return one team and its corresponding metrics from the teams with the best metrics.

    Args:
        players (list[Player]): Players to generate teams from.

    Returns:
        TeamData: A team and its corresponding metrics.
    """
    maximum_number_of_teams = 50000
    best_teams: list[TeamData] = []
    best_team_metrics = None
    random.shuffle(players)

    for teams in _generate_every_team_combination(players):
        team_metrics = _calculate_team_metrics(teams)

        if best_team_metrics is None:
            best_team_metrics = team_metrics

        if team_metrics == best_team_metrics:
            best_teams.append(TeamData(teams, team_metrics))
        elif team_metrics < best_team_metrics:
            best_team_metrics = team_metrics
            best_teams = [TeamData(teams, team_metrics)]

        if len(best_teams) >= maximum_number_of_teams:
            break  # pragma: no cover

    return random.choice(best_teams)  # noqa: S311


def _generate_every_team_combination(players: list[Player]) -> Generator[TeamDistribution, None, None]:
    for team_1_tuple in combinations(players, len(players) // 2):
        team_1 = set(team_1_tuple)
        team_2 = {player for player in players if player not in team_1}

        yield (team_1, team_2)


def _calculate_team_metrics(teams: TeamDistribution) -> TeamMetrics:
    goalie_number_difference = _calculate_goalie_number_difference(teams)
    defense_number_difference = _calculate_defense_number_difference(teams)
    skill_difference = _calculate_skill_level_difference(teams, goalie_number_difference)

    return TeamMetrics(goalie_number_difference, defense_number_difference, skill_difference)


def _calculate_goalie_number_difference(teams: TeamDistribution) -> int:
    total_goalie_numbers = []
    for team in teams:
        total_goalie_number = 0
        for player in team:
            if "G" in player.positions:
                total_goalie_number += 1
        total_goalie_numbers.append(total_goalie_number)

    return abs(total_goalie_numbers[0] - total_goalie_numbers[1])


def _calculate_defense_number_difference(teams: TeamDistribution) -> int:
    total_defense_numbers = []
    for team in teams:
        total_defense_number = 0
        for player in team:
            if set(player.positions).intersection({"RD", "LD"}):
                total_defense_number += 1
        total_defense_numbers.append(total_defense_number)

    return abs(total_defense_numbers[0] - total_defense_numbers[1])


def _calculate_skill_level_difference(teams: TeamDistribution, goalie_number_difference: int) -> int:
    total_team_skills = []
    for team in teams:
        total_team_skill = 0
        for player in team:
            if "G" in player.positions and goalie_number_difference != 0:
                continue
            total_team_skill += player.skill
        total_team_skills.append(total_team_skill)

    return abs(total_team_skills[0] - total_team_skills[1])


def generate_output(
    date: str,
    best_team: TeamData,
    players_with_missing_data: list[str],
    unknown_players: list[str],
) -> str:
    """Generate the output string containing all the necessary information about the teams.

    Args:
        date (str): The date of the practice.
        best_team (Team): The best team distribution and its corresponding metrics.
        players_with_missing_data (list[str]): Players missing from team_data.
        unknown_players (list[str]): Players with incomplete information in team_data.

    Returns:
        str: All the necessary information about the teams.
    """
    team_red, team_green = _assign_me_to_team_red(best_team.teams, "Daniel Mizsak")
    output = f"Date: {date}\n\n"
    output += f"Team Red: ({len(team_red)})\n" + "\n".join([player.name for player in team_red]) + "\n\n"
    output += f"Team Green: ({len(team_green)})\n" + "\n".join([player.name for player in team_green]) + "\n\n"
    output += f"Players with missing data: {', '.join(players_with_missing_data)}\n"
    output += f"Unknown players: {', '.join(unknown_players)}\n\n"
    output += f"Skill difference: {best_team.metrics.skill_difference}\n"
    output += f"Goalie number difference: {best_team.metrics.goalie_number_difference}\n"
    output += f"Defense number difference: {best_team.metrics.defense_number_difference}\n\n"

    return output


def _assign_me_to_team_red(teams: TeamDistribution, my_name: str) -> tuple[list[Player], list[Player]]:
    i_am_in_team_zero = any(player.name == my_name for player in teams[0])
    team_red = sorted(teams[0] if i_am_in_team_zero else teams[1], key=lambda player: player.name)
    team_green = sorted(teams[1] if i_am_in_team_zero else teams[0], key=lambda player: player.name)
    return team_red, team_green
