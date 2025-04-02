"""
Short description and source of base code.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import pytest

from falcon_formation.data_models import Guest, Member, Player, TeamDistributionMetrics
from falcon_formation.main import (
    _assign_me_to_team_one,
    _calculate_team_combination_metrics,
    _generate_every_team_combination,
)


@pytest.fixture
def team_combination() -> tuple[tuple[Player, ...], tuple[Player, ...]]:
    return (
        (
            Member(_id=1234, name="Member Name 1", skill=300, position="Forward"),
            Member(_id=1235, name="Member Name 2", skill=250, position="Defense"),
            Guest(name="Guest Name 1", skill=400, position="Goalie"),
        ),
        (
            Member(_id=1236, name="Member Name 3", skill=350, position="Goalie"),
            Member(_id=1237, name="Member Name 4", skill=200, position="Forward"),
            Guest(name="Guest Name 2", skill=450, position="Defense"),
        ),
    )


def test_generate_every_team_combination() -> None:
    players = [
        Member(_id=1234, name="Member Name 1"),
        Member(_id=1235, name="Member Name 2"),
        Member(_id=1236, name="Member Name 3"),
        Member(_id=1237, name="Member Name 4"),
        Guest(name="Guest Name 1"),
        Guest(name="Guest Name 2"),
    ]

    team_combination_number = 0
    for _ in _generate_every_team_combination(players):
        team_combination_number += 1

    assert team_combination_number == 20


def test_calculate_team_combination_metrics(team_combination: tuple[tuple[Player, ...], tuple[Player, ...]]) -> None:
    assert _calculate_team_combination_metrics(team_combination) == TeamDistributionMetrics(
        goalie_number_difference=0,
        defense_number_difference=0,
        skill_difference=50,
        defense_skill_difference=200,
    )


def test_assign_me_to_team_one(team_combination: tuple[tuple[Player, ...], tuple[Player, ...]]) -> None:
    assert _assign_me_to_team_one(team_combination, "Member Name 3") == (
        sorted(team_combination[1], key=lambda player: player.name),
        sorted(team_combination[0], key=lambda player: player.name),
    )
