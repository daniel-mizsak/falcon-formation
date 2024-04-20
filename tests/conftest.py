"""
Short description and source of base code.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from pathlib import Path

import pytest
from falcon_formation.create_teams import Player, load_team_data


@pytest.fixture()  # type: ignore[misc]
def team_data() -> list[Player]:
    team_data_path = Path("data/team_example.json")
    team_name = "Dream Team"

    return load_team_data(team_data_path, team_name)
