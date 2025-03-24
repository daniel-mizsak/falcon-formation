"""
Short description and source of base code.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import pytest

from falcon_formation.data_models import Guest, Member, TeamDistribution, TeamDistributionMetrics, TeamMetadata


@pytest.fixture
def team_metadata(team_id: int) -> TeamMetadata:
    return TeamMetadata(
        _id=team_id,
        name="Team Name",
        activity_name="Activity Name",
        jersey_color_1="Red",
        jersey_color_2="Black",
        telegram_chat_id=-123456,
    )


@pytest.fixture
def member() -> Member:
    return Member(_id=1234, name="Member Name")


@pytest.fixture
def guest() -> Guest:
    return Guest(name="Guest Name")


@pytest.fixture
def team_distribution_metrics() -> TeamDistributionMetrics:
    return TeamDistributionMetrics(
        goalie_number_difference=1,
        defense_number_difference=1,
        skill_difference=100,
        defense_skill_difference=50,
    )


@pytest.fixture
def team_distribution(date: str, team_distribution_metrics: TeamDistributionMetrics) -> TeamDistribution:
    team_1 = [
        Member(_id=1234, name="Member Name 1"),
        Member(_id=1235, name="Member Name 2"),
        Guest(name="Guest Name 1"),
    ]
    team_2 = [
        Member(_id=1236, name="Member Name 3"),
        Member(_id=1237, name="Member Name 4"),
        Guest(name="Guest Name 2"),
    ]
    return TeamDistribution(
        date=date,
        team_1=team_1,
        team_2=team_2,
        metrics=team_distribution_metrics,
    )


@pytest.fixture
def team_id() -> int:
    return 12345


@pytest.fixture
def date() -> str:
    return "2025-01-01"
