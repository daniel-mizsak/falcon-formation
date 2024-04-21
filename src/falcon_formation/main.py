"""
Main module of the Falcon Formation application.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import os
import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

from dotenv import dotenv_values

from falcon_formation.create_teams import (
    generate_output,
    get_best_team,
    get_players,
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

    # Get the best team
    best_team = get_best_team(players)

    # Create output
    return generate_output(date, best_team, players_with_missing_data, unknown_players)


if __name__ == "__main__":
    sys.exit(main())
