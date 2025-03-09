"""
Helper functions for creating hockey teams.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from __future__ import annotations

import asyncio
import random
from datetime import UTC, datetime, timedelta
from itertools import combinations
from typing import TYPE_CHECKING

from falcon_formation.data_models import Guest, Member, TeamDistribution, TeamDistributionMetrics
from falcon_formation.server import database, holdsport_api

if TYPE_CHECKING:
    from collections.abc import Generator

    from falcon_formation.data_models import Player


def create_teams(team_id: int) -> None:
    """Create the teams for the given team id.

    Args:
        team_id (int): The id of the team in the Holdsport system.
    """
    date = str((datetime.now(tz=UTC) + timedelta(hours=2)).date())

    players: list[Player] = []
    players.extend(load_registered_members(team_id, date))
    players.extend(load_registered_guests(team_id, date))
    create_team_distribution(players, team_id, date)


def get_teams(team_id: int) -> str:
    """Get the previously created teams for the given team id.

    Args:
        team_id (int): The id of the team in the Holdsport system.

    Returns:
        str: The formatted string of the teams.
    """
    date = str((datetime.now(tz=UTC) + timedelta(hours=2)).date())

    team_metadata = database.load_team_metadata(team_id)
    if team_metadata is None:
        return "No team metadata found."
    team_distribution = database.load_team_distribution(team_id, date)
    if team_distribution is None:
        return "No team distribution found."

    output = ""
    output = f"Date: {team_distribution.date}\n\n"
    output += f"Team {team_metadata.jersey_color_1}: ({len(team_distribution.team_1)})\n"
    output += "\n".join([str(player) for player in team_distribution.team_1]) + "\n\n"

    output += f"Team {team_metadata.jersey_color_2}: ({len(team_distribution.team_2)})\n"
    output += "\n".join([str(player) for player in team_distribution.team_2]) + "\n\n"

    output += f"Goalie number difference: {team_distribution.metrics.goalie_number_difference}\n"
    output += f"Defense number difference: {team_distribution.metrics.defense_number_difference}\n"
    output += f"Skill difference: {team_distribution.metrics.skill_difference}\n"
    output += f"Defense skill difference: {team_distribution.metrics.defense_skill_difference}"

    return output


def get_goalie_number(team_id: int) -> str:
    """Get the formatted string of the goalie number for the given team id.

    Args:
        team_id (int): The id of the team in the Holdsport system.

    Returns:
        str: The formatted string of the goalie number.
    """
    date = str((datetime.now(tz=UTC) + timedelta(hours=2)).date())

    players: list[Player] = []
    players.extend(load_registered_members(team_id, date))
    players.extend(load_registered_guests(team_id, date))

    goalie_count = 0
    for player in players:
        if player.position == "Goalie":
            goalie_count += 1

    goalie_return_dictionary: dict[int, str] = {
        0: "Oh-oh! No goalie registered for today's practice yet. Please reach out to other goalies.",
        1: "Attention! Only 1 goalie registered for today's practice! Please reach out to other goalies.",
        2: "Good news! There are exactly 2 goalies registered for today's practice.",
    }

    return goalie_return_dictionary.get(
        goalie_count,
        "Ok, it looks like more than 2 goalies registered for today's practice. I guess we will make it work somehow.",
    )


def load_registered_members(team_id: int, date: str) -> list[Member]:
    """Query the registered members from Holdsport and load them from the database.

    Args:
        team_id (int): The id of the team in the Holdsport system.
        date (str): The date of the activity in format "YYYY-MM-DD".

    Returns:
        list[Member]: List of registered members.
    """
    team_metadata = database.load_team_metadata(team_id)
    if team_metadata is None:
        return []
    activity_id = asyncio.run(holdsport_api.get_activity_id(team_id, date, team_metadata.activity_name))
    if activity_id is None:
        return []
    registered_members = asyncio.run(holdsport_api.get_users_attending_activity(activity_id))

    members: list[Member] = []
    for registered_member in registered_members:
        member = database.load_member(team_id, int(registered_member["_id"]))
        if member:
            members.append(member)
        else:
            new_member = Member.from_dict(registered_member)
            database.insert_member(team_id, new_member)
            members.append(new_member)
    return members


def load_registered_guests(team_id: int, date: str) -> list[Guest]:
    """Load the registered guests from the database.

    Args:
        team_id (int): The id of the team in the Holdsport system.
        date (str): The date of the activity in format "YYYY-MM-DD".

    Returns:
        list[Guest]: List of registered guests.
    """
    return database.load_guest_collection(team_id, date)


def create_team_distribution(players: list[Player], team_id: int, date: str) -> None:
    """Create the team distribution based on the registered players.

    The team distribution is randomly selected from the best team combinations.
    The result is not returned as execution time can be substantial, but rather inserted into the database.

    Args:
        players (list[Player]): List of registered Members and Guests.
        team_id (int): The id of the team in the Holdsport system.
        date (str): The date of the activity in format "YYYY-MM-DD".
    """
    maximum_number_of_teams = 5000
    best_team_combinations: list[tuple[tuple[Player, ...], tuple[Player, ...]]] = []
    best_metrics: TeamDistributionMetrics | None = None

    shuffled_players = players.copy()
    random.shuffle(shuffled_players)

    for team_combination in _generate_every_team_combination(shuffled_players):
        metrics = _calculate_team_combination_metrics(team_combination)

        if best_metrics is None:
            best_metrics = metrics

        if metrics == best_metrics:
            best_team_combinations.append(team_combination)
        elif metrics < best_metrics:
            best_metrics = metrics
            best_team_combinations = [team_combination]
            continue

        if len(best_team_combinations) >= maximum_number_of_teams:
            break

    if best_metrics is None:
        return

    teams = _assign_me_to_team_one(random.choice(best_team_combinations))  # noqa: S311
    team_distribution = TeamDistribution(
        date=date,
        team_1=teams[0],
        team_2=teams[1],
        metrics=best_metrics,
    )
    database.insert_or_update_team_distribution(team_id, team_distribution)


def _generate_every_team_combination(
    players: list[Player],
) -> Generator[tuple[tuple[Player, ...], tuple[Player, ...]], None, None]:
    for team_1 in combinations(players, len(players) // 2):
        team_2 = tuple(player for player in players if player not in team_1)
        yield (team_1, team_2)


def _calculate_team_combination_metrics(
    team_combination: tuple[tuple[Player, ...], tuple[Player, ...]],
) -> TeamDistributionMetrics:
    goalie_number_difference = _calculate_goalie_number_difference(team_combination)
    defense_number_difference = _calculate_defense_number_difference(team_combination)
    skill_difference = _calculate_skill_difference(team_combination, goalie_number_difference)
    defense_skill_difference = _calculate_defense_skill_difference(team_combination)

    return TeamDistributionMetrics(
        goalie_number_difference=goalie_number_difference,
        defense_number_difference=defense_number_difference,
        skill_difference=skill_difference,
        defense_skill_difference=defense_skill_difference,
    )


def _calculate_goalie_number_difference(team_combination: tuple[tuple[Player, ...], tuple[Player, ...]]) -> int:
    total_goalie_numbers = []
    for team in team_combination:
        total_goalie_number = 0
        for player in team:
            if player.position == "Goalie":
                total_goalie_number += 1
        total_goalie_numbers.append(total_goalie_number)

    return abs(total_goalie_numbers[0] - total_goalie_numbers[1])


def _calculate_defense_number_difference(team_combination: tuple[tuple[Player, ...], tuple[Player, ...]]) -> int:
    total_defense_numbers = []
    for team in team_combination:
        total_defense_number = 0
        for player in team:
            if player.position == "Defense":
                total_defense_number += 1
        total_defense_numbers.append(total_defense_number)

    return abs(total_defense_numbers[0] - total_defense_numbers[1])


def _calculate_skill_difference(
    team_combination: tuple[tuple[Player, ...], tuple[Player, ...]],
    goalie_number_difference: int,
) -> int:
    total_team_skills: list[int] = []
    for team in team_combination:
        total_team_skill = 0
        for player in team:
            # Goalie skill is not considered if there is a goalie number difference.
            if goalie_number_difference != 0 and player.position == "Goalie":
                continue
            total_team_skill += player.skill
        total_team_skills.append(total_team_skill)

    return abs(total_team_skills[0] - total_team_skills[1])


def _calculate_defense_skill_difference(team_combination: tuple[tuple[Player, ...], tuple[Player, ...]]) -> int:
    total_defense_skills = []
    for team in team_combination:
        total_defense_skill = 0
        for player in team:
            if player.position == "Defense":
                total_defense_skill += player.skill
        total_defense_skills.append(total_defense_skill)

    return abs(total_defense_skills[0] - total_defense_skills[1])


def _assign_me_to_team_one(
    team_combination: tuple[tuple[Player, ...], tuple[Player, ...]],
    my_name: str = "DANIEL MIZSAK",
) -> tuple[list[Player], list[Player]]:
    i_am_in_team_one = any(player.name == my_name for player in team_combination[0])
    team_1 = sorted(team_combination[0] if i_am_in_team_one else team_combination[1], key=lambda player: player.name)
    team_2 = sorted(team_combination[1] if i_am_in_team_one else team_combination[0], key=lambda player: player.name)
    return team_1, team_2
