"""
Short description and source of base code.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from pathlib import Path

from falcon_formation.create_teams import Player
from falcon_formation.main import load_team_data, save_team_data


def test_load_team_data() -> None:
    team_data_path = Path("data/team_example.json")
    team_name = "Dream Team"

    team_data = load_team_data(team_data_path, team_name)

    assert isinstance(team_data, list)
    assert len(team_data) == 15
    assert team_data[0] == Player(name="George Goalie", skill=3, positions=tuple("G"))
    assert team_data[1] == Player(name="Gustavo Goalie", skill=5, positions=tuple("G"))
    assert team_data[-1] == Player(name="Cody Center", skill=4, positions=("C", "RW"))


def test_save_team_data() -> None:
    team_data_path = Path("data/team_test.json")
    team_name = "Dream Team"

    team_data = [
        Player(name="George Goalie", skill=3, positions=tuple("G")),
        Player(name="Gustavo Goalie", skill=5, positions=tuple("G")),
        Player(name="Cody Center", skill=4, positions=("C", "RW")),
    ]

    save_team_data(team_data_path, team_name, team_data)

    team_data = load_team_data(team_data_path, team_name)

    assert isinstance(team_data, list)
    assert len(team_data) == 3
    assert team_data[0] == Player(name="George Goalie", skill=3, positions=tuple("G"))
    assert team_data[1] == Player(name="Gustavo Goalie", skill=5, positions=tuple("G"))
    assert team_data[-1] == Player(name="Cody Center", skill=4, positions=("C", "RW"))

    team_data_path.unlink()
