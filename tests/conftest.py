"""
Conftest module for pytest fixtures.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import pytest

from falcon_formation.data_models import Player
from falcon_formation.main import load_team_data


@pytest.fixture()  # type: ignore[misc]
def team_data() -> list[Player]:
    team_data_path = "data/team_example.json"

    return load_team_data(team_data_path)
