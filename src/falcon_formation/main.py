"""
Main module of the Falcon Formation application.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from datetime import UTC, datetime, timedelta

from falcon_formation import JERSEY_COLORS
from falcon_formation.create_teams import choose_best_team, generate_output, generate_output_goalie, get_players
from falcon_formation.data_operations import load_config, load_team_data
from falcon_formation.holdsport_api import get_registered_players


def falcon_formation(team_name: str, goalie: bool = False) -> tuple[str, str]:  # noqa: FBT001, FBT002
    """Run Falcon Formation.

    Args:
        team_name (str): Name of the team.
        goalie (bool): Whether to only check for goalies. Defaults to False.

    Returns:
        str: The output text containing all the relevant information about the generated teams and their metadata.
    """
    # Load configuration values
    config_path = ".env"
    team_id, activity_name, auth, _ = load_config(config_path, team_name)
    date = str((datetime.now(tz=UTC) + timedelta(hours=2)).date())

    # Load team data and query registered players
    team_data_path = f"data/{team_name.upper()}.json"
    team_data = load_team_data(team_data_path)
    registered_players = get_registered_players(team_id, date, auth, activity_name)

    # Get players
    players, unknown_players, players_with_missing_data = get_players(team_data, registered_players)

    # Extra players
    extras_data_path = f"https://falcon-formation.pythonvilag.hu/extras/{team_name}/{date}"
    extra_players = load_team_data(extras_data_path)
    players.extend(extra_players)

    # Generate goalie output if specified
    if goalie:
        return generate_output_goalie(players), ""

    # Randomly choose one of the best team combinations
    best_team = choose_best_team(players)

    jersey_colors = JERSEY_COLORS[team_name.upper()]

    # Create output
    return generate_output(date, best_team, jersey_colors, players_with_missing_data, unknown_players)
