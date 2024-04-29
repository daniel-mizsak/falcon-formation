"""
Update skill level of individual players based on the outcome of the game.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from falcon_formation.create_teams import Player


def update_players_skill(team_data: list[Player], update_values: dict[str, int]) -> list[Player]:
    """Update the skill level of individual players based on the outcome of the game.

    Args:
        team_data (list[Player]): List of Player objects, where each element represents a player in the team.
        update_values (dict[str, int]): Dictionary where the key is the player name and the value is the
        skill level change.

    Returns:
        list[Player]: Updated list of Player objects.
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
