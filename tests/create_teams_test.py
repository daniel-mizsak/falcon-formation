"""
Tests for the falcon_formation.create_teams module.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import textwrap
from math import factorial
from pathlib import Path

import pytest
from falcon_formation.create_teams import (
    Player,
    TeamData,
    TeamMetrics,
    _assign_me_to_team_red,
    _calculate_defense_number_difference,
    _calculate_goalie_number_difference,
    _calculate_skill_level_difference,
    _calculate_team_metrics,
    _generate_every_team_combination,
    choose_best_team,
    generate_output,
    get_players,
    load_team_data,
)


def test_player() -> None:
    player = Player(name="George Goalie", skill=3, positions=frozenset(["G"]))
    assert isinstance(player, Player)

    assert isinstance(player.name, str)
    assert player.name == "George Goalie"

    assert isinstance(player.skill, int)
    assert player.skill == 3

    assert isinstance(player.positions, frozenset)
    assert player.positions == frozenset(["G"])


def test_team_metrics() -> None:
    team_metrics = TeamMetrics(skill_difference=3, goalie_number_difference=2, defense_number_difference=1)
    assert isinstance(team_metrics, TeamMetrics)

    assert isinstance(team_metrics.skill_difference, int)
    assert team_metrics.skill_difference == 3

    assert isinstance(team_metrics.goalie_number_difference, int)
    assert team_metrics.goalie_number_difference == 2

    assert isinstance(team_metrics.defense_number_difference, int)
    assert team_metrics.defense_number_difference == 1


@pytest.mark.skip(reason="Have not updated tests to reflect changes in the code.")  # type: ignore[misc]
def test_team_metrics_operators() -> None:
    team_metrics_1 = TeamMetrics(skill_difference=2, goalie_number_difference=2, defense_number_difference=2)
    team_metrics_2 = TeamMetrics(skill_difference=2, goalie_number_difference=2, defense_number_difference=2)
    team_metrics_3 = TeamMetrics(skill_difference=2, goalie_number_difference=2, defense_number_difference=3)
    team_metrics_4 = TeamMetrics(skill_difference=2, goalie_number_difference=4, defense_number_difference=1)
    team_metrics_5 = TeamMetrics(skill_difference=3, goalie_number_difference=1, defense_number_difference=2)
    team_metrics_6 = TeamMetrics(skill_difference=1, goalie_number_difference=3, defense_number_difference=2)

    assert team_metrics_1 == team_metrics_2
    assert team_metrics_1 != team_metrics_3
    assert team_metrics_1 < team_metrics_3
    assert team_metrics_1 < team_metrics_4
    assert team_metrics_1 < team_metrics_5
    assert team_metrics_1 > team_metrics_6


def test_team_data() -> None:
    team_data = TeamData(
        teams=(
            {
                Player(name="George Goalie", skill=3, positions=frozenset(["G"])),
                Player(name="Daniel Defender", skill=4, positions=frozenset(["LD", "C"])),
            },
            {
                Player(name="Gustavo Goalie", skill=5, positions=frozenset(["G"])),
                Player(name="David Defender", skill=3, positions=frozenset(["LD", "RD"])),
            },
        ),
        metrics=TeamMetrics(skill_difference=1, goalie_number_difference=0, defense_number_difference=0),
    )

    assert isinstance(team_data, TeamData)

    # assert isinstance(team_data.teams, TeamDistribution)  # noqa: ERA001
    assert len(team_data.teams) == 2
    assert isinstance(team_data.teams[0], set)
    assert isinstance(team_data.teams[1], set)

    assert isinstance(team_data.metrics, TeamMetrics)


def test_load_team_data() -> None:
    team_data_path = Path("data/team_example.json")
    team_name = "Dream Team"

    team_data = load_team_data(team_data_path, team_name)

    assert isinstance(team_data, list)
    assert len(team_data) == 15
    assert team_data[0] == Player(name="George Goalie", skill=3, positions=frozenset("G"))
    assert team_data[1] == Player(name="Gustavo Goalie", skill=5, positions=frozenset("G"))
    assert team_data[-1] == Player(name="Cody Center", skill=4, positions=frozenset({"C", "RW"}))


def test_get_players(team_data: list[Player]) -> None:
    registered_players = [
        "George Goalie",
        "Gustavo Goalie",
        "Daniel Defender",
        "David Defender",
        "Wally Wing",
        "Willy Wing",
        "Cody Center",
        "Adam Anonymus",
    ]

    players, unknown_players, players_with_missing_data = get_players(team_data, registered_players)

    assert isinstance(players, list)
    assert len(players) == 8
    assert isinstance(players[0], Player)

    assert isinstance(unknown_players, list)
    assert len(unknown_players) == 1
    assert unknown_players[0] == "Adam Anonymus"

    assert isinstance(players_with_missing_data, list)
    assert len(players_with_missing_data) == 1
    assert players_with_missing_data[0] == "Willy Wing"


def test_best_team() -> None:
    players = [
        Player(name="George Goalie", skill=3, positions=frozenset("G")),
        Player(name="Gustavo Goalie", skill=5, positions=frozenset("G")),
        Player(name="Daniel Defender", skill=4, positions=frozenset({"LD", "C"})),
    ]

    best_team = choose_best_team(players)

    assert isinstance(best_team, TeamData)
    assert len(best_team.teams) == 2
    assert isinstance(best_team.teams[0], set)
    assert isinstance(best_team.teams[1], set)

    assert isinstance(best_team.metrics, TeamMetrics)
    # TODO: Assert concrete values


def test_generate_every_team_combination(team_data: list[Player]) -> None:
    number_of_team_combinations = 0

    for team_1, team_2 in _generate_every_team_combination(team_data):
        assert isinstance(team_1, set)
        assert len(team_1) == len(team_data) // 2

        assert isinstance(team_2, set)
        assert len(team_1) + len(team_2) == len(team_data)

        for player in team_1:
            assert player not in team_2
        number_of_team_combinations += 1

    assert number_of_team_combinations == factorial(len(team_data)) / (
        factorial(len(team_data) // 2) * factorial(len(team_data) - len(team_data) // 2)
    )


def test_calculate_team_metrics(team_data: list[Player]) -> None:
    for teams in _generate_every_team_combination(team_data):
        team_metrics = _calculate_team_metrics(teams)

        goalie_number_difference = _calculate_goalie_number_difference(teams)
        defense_number_difference = _calculate_defense_number_difference(teams)
        skill_level_difference = _calculate_skill_level_difference(teams)

        assert isinstance(team_metrics, TeamMetrics)
        assert team_metrics.goalie_number_difference == goalie_number_difference
        assert team_metrics.defense_number_difference == defense_number_difference
        assert team_metrics.skill_difference == skill_level_difference


def test_calculate_goalie_number_difference(team_data: list[Player]) -> None:
    for teams in _generate_every_team_combination(team_data):
        goalie_number_difference = _calculate_goalie_number_difference(teams)

        team_1, team_2 = teams
        goalie_number_team_1 = len([player for player in team_1 if "G" in player.positions])
        goalie_number_team_2 = len([player for player in team_2 if "G" in player.positions])

        assert goalie_number_difference == abs(goalie_number_team_1 - goalie_number_team_2)


def test_calculate_defense_number_difference(team_data: list[Player]) -> None:
    for teams in _generate_every_team_combination(team_data):
        defense_number_difference = _calculate_defense_number_difference(teams)

        team_1, team_2 = teams
        defense_number_team_1 = len([player for player in team_1 if player.positions.intersection({"RD", "LD"})])
        defense_number_team_2 = len([player for player in team_2 if player.positions.intersection({"RD", "LD"})])

        assert defense_number_difference == abs(defense_number_team_1 - defense_number_team_2)


def test_calculate_skill_level_difference(team_data: list[Player]) -> None:
    for teams in _generate_every_team_combination(team_data):
        skill_level_difference = _calculate_skill_level_difference(teams)

        team_1, team_2 = teams
        skill_level_team_1 = sum([player.skill for player in team_1])
        skill_level_team_2 = sum([player.skill for player in team_2])

        assert skill_level_difference == abs(skill_level_team_1 - skill_level_team_2)


def test_generate_output() -> None:
    date = "2024-01-01"
    best_team = TeamData(
        teams=(
            {
                Player(name="George Goalie", skill=3, positions=frozenset("G")),
                Player(name="Daniel Mizsak", skill=4, positions=frozenset({"LD", "C"})),
            },
            {
                Player(name="Gustavo Goalie", skill=5, positions=frozenset("G")),
                Player(name="David Defender", skill=3, positions=frozenset({"LD", "RD"})),
            },
        ),
        metrics=TeamMetrics(skill_difference=1, goalie_number_difference=0, defense_number_difference=0),
    )
    players_with_missing_data = ["Willy Wing"]
    unknown_players = ["Adam Anonymus"]

    output = generate_output(date, best_team, players_with_missing_data, unknown_players)

    assert isinstance(output, str)
    assert output == textwrap.dedent("""\
                                     Date: 2024-01-01

                                     Team Red: (2)
                                     Daniel Mizsak
                                     George Goalie

                                     Team Green: (2)
                                     David Defender
                                     Gustavo Goalie

                                     Players with missing data: Willy Wing
                                     Unknown players: Adam Anonymus

                                     Skill difference: 1
                                     Goalie number difference: 0
                                     Defense number difference: 0

                                     """)


def test_assign_me_to_team_red(team_data: list[Player]) -> None:
    for teams in _generate_every_team_combination(team_data):
        my_name = "Daniel Defender"
        team_red, team_green = _assign_me_to_team_red(teams, my_name)

        assert isinstance(team_red, list)
        assert isinstance(team_green, list)

        assert len(team_red) + len(team_green) == len(team_data)
        assert any(player.name == my_name for player in team_red)
        assert not any(player.name == my_name for player in team_green)
