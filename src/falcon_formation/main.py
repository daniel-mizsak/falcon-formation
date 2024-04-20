"""
Main module of the Falcon Formation application.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import os
import random
import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

from dotenv import dotenv_values

from falcon_formation.create_teams import (
    Player,
    TeamMetrics,
    assign_me_to_team_red,
    calculate_team_metrics,
    generate_every_team_combination,
    load_team_data,
)
from falcon_formation.holdsport_api import get_registered_players


def main() -> int:
    """Main function of the Falcon Formation application."""
    start_time = time.time()

    print(falcon_formation())  # noqa: T201

    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.2f} seconds.")  # noqa: T201

    return 0


def falcon_formation() -> str:
    """_summary_.

    Returns:
        str: _description_
    """
    # Load configuration values
    config = dotenv_values(".env")
    if not config:
        config = dict(os.environ)

    date = str((datetime.now(tz=UTC) + timedelta(hours=2) + timedelta(days=2)).date())
    team_id = int(str(config["TEAM_ID"]))
    team_name = str(config["TEAM_NAME"])
    auth = (str(config["HOLDSPORT_USERNAME"]), str(config["HOLDSPORT_PASSWORD"]))

    # Load team data and query registered players
    team_data_path = Path("data/team.json")
    team_data = load_team_data(team_data_path, team_name)
    registered_players = get_registered_players(team_id, date, auth)

    # Get player list to create teams from
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
            players.append(Player(name=player_name, skill=3, positions=frozenset()))
            unknown_players.append(player_name)

    # Calculate teams with the best metrics
    best_teams: list[tuple[tuple[set[Player], set[Player]], TeamMetrics]] = []
    best_team_metrics = None
    random.shuffle(players)
    for teams in generate_every_team_combination(players):
        team_metrics = calculate_team_metrics(teams)

        if best_team_metrics is None:
            best_team_metrics = team_metrics

        if team_metrics == best_team_metrics:
            best_teams.append((teams, team_metrics))
        elif team_metrics < best_team_metrics:
            best_team_metrics = team_metrics
            best_teams = [(teams, team_metrics)]

    # Choose a random team from the best teams and create output
    choice = random.choice(best_teams)  # noqa: S311
    team_red, team_green = assign_me_to_team_red(choice[0], "Daniel Mizsak")

    output = f"Date: {date}\n\n"
    output += f"Team Red: ({len(team_red)})\n{'\n'.join([player.name for player in team_red])}\n\n"
    output += f"Team Green: ({len(team_green)})\n{'\n'.join([player.name for player in team_green])}\n\n"
    output += f"Players with missing data: {', '.join(players_with_missing_data)}\n"
    output += f"Unknown players: {', '.join(unknown_players)}\n\n"
    output += f"Skill difference: {choice[1].skill_difference}\n"
    output += f"Goalie number difference: {choice[1].goalie_number_difference}\n"
    output += f"Defense number difference: {choice[1].defense_number_difference}\n\n"

    return output


if __name__ == "__main__":
    sys.exit(main())
