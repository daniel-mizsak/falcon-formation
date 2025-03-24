"""
Tests for the data model modules.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import re

import pytest

from falcon_formation.data_models import (
    Guest,
    Member,
    Position,
    Skill,
    TeamDistributionMetrics,
    TeamMetadata,
)


# TeamMetadata
def test_team_metadata(team_metadata: TeamMetadata) -> None:
    assert isinstance(team_metadata._id, int)  # noqa: SLF001
    assert team_metadata._id == 12345  # noqa: SLF001

    assert isinstance(team_metadata.name, str)
    assert team_metadata.name == "Team Name"

    assert isinstance(team_metadata.activity_name, str)
    assert team_metadata.activity_name == "Activity Name"

    assert isinstance(team_metadata.jersey_color_1, str)
    assert team_metadata.jersey_color_1 == "Red"

    assert isinstance(team_metadata.jersey_color_2, str)
    assert team_metadata.jersey_color_2 == "Black"

    assert isinstance(team_metadata.telegram_chat_id, int)
    assert team_metadata.telegram_chat_id == -123456


def test_team_metadata_to_dict(team_metadata: TeamMetadata) -> None:
    team_metadata_dict = team_metadata.to_dict()
    assert isinstance(team_metadata_dict, dict)

    assert team_metadata_dict == {
        "_id": "12345",
        "name": "Team Name",
        "activity_name": "Activity Name",
        "jersey_color_1": "Red",
        "jersey_color_2": "Black",
        "telegram_chat_id": "-123456",
    }


def test_team_metadata_from_dict(team_metadata: TeamMetadata) -> None:
    team_metadata_dict = {
        "_id": "12345",
        "name": "Team Name",
        "activity_name": "Activity Name",
        "jersey_color_1": "Red",
        "jersey_color_2": "Black",
        "telegram_chat_id": "-123456",
    }
    assert TeamMetadata.from_dict(team_metadata_dict) == team_metadata


# Skill
def test_skill() -> None:
    assert Skill.MINIMUM.score == -500
    assert Skill.MINIMUM.description == "Minimum"

    assert Skill.WELL_BELOW_AVERAGE.score == 100
    assert Skill.WELL_BELOW_AVERAGE.description == "Well below average"

    assert Skill.BELOW_AVERAGE.score == 200
    assert Skill.BELOW_AVERAGE.description == "Below average"

    assert Skill.AVERAGE.score == 300
    assert Skill.AVERAGE.description == "Average"

    assert Skill.ABOVE_AVERAGE.score == 400
    assert Skill.ABOVE_AVERAGE.description == "Above average"

    assert Skill.WELL_ABOVE_AVERAGE.score == 500
    assert Skill.WELL_ABOVE_AVERAGE.description == "Well above average"

    assert Skill.MAXIMUM.score == 1000
    assert Skill.MAXIMUM.description == "Maximum"

    assert {"label": "Average", "value": 300} in Skill.to_dropdown_options()
    assert {"label": "Minimum", "value": -500} not in Skill.to_dropdown_options()

    assert Skill.get_description_from_value(300) == "Average"
    assert Skill.get_description_from_value(420) is None


# Position
def test_position() -> None:
    assert Position.DEFENSE.value == "Defense"
    assert Position.DEFENSE.emoji == "⏮️"

    assert Position.FORWARD.value == "Forward"
    assert Position.FORWARD.emoji == "⏩"

    assert Position.GOALIE.value == "Goalie"
    assert Position.GOALIE.emoji == "⏹️"

    assert Position.to_dropdown_options() == [
        {"label": "Defense", "value": "Defense"},
        {"label": "Forward", "value": "Forward"},
        {"label": "Goalie", "value": "Goalie"},
    ]


# Member
def test_member_default_values(member: Member) -> None:
    assert isinstance(member._id, int)  # noqa: SLF001
    assert member._id == 1234  # noqa: SLF001

    assert isinstance(member.name, str)
    assert member.name == "Member Name"

    assert isinstance(member.skill, int)
    assert member.skill == Skill.AVERAGE.score

    assert isinstance(member.position, str)
    assert member.position == Position.FORWARD.value


def test_member_custom_values(member: Member) -> None:
    member = Member(_id=1234, name="Member Name", skill=420, position="Defense")

    assert member._id == 1234  # noqa: SLF001
    assert member.name == "Member Name"
    assert member.skill == 420
    assert member.position == "Defense"


def test_member_post_init() -> None:
    with pytest.raises(TypeError, match=re.escape("Invalid member id")):
        Member(_id=12.34, name="Member Name")  # type: ignore[arg-type]

    with pytest.raises(ValueError, match=re.escape("Invalid player name")):
        Member(_id=1234, name="")

    member = Member(_id=1234, name="Member Name", skill=Skill.MAXIMUM.score + 1)
    assert member.skill == Skill.MAXIMUM.score

    member = Member(_id=1234, name="Member Name", skill=Skill.MINIMUM.score - 1)
    assert member.skill == Skill.MINIMUM.score

    with pytest.raises(ValueError, match=re.escape("Invalid position")):
        Member(_id=1234, name="Member Name", position="Midfield")


def test_member_to_dict(member: Member) -> None:
    member_dict = member.to_dict()
    assert isinstance(member_dict, dict)

    assert member_dict == {
        "_id": "1234",
        "name": "Member Name",
        "skill": str(Skill.AVERAGE.score),
        "position": Position.FORWARD.value,
    }


def test_member_from_dict(member: Member) -> None:
    member_dict = {
        "_id": "1234",
        "name": "Member Name",
        "skill": str(Skill.AVERAGE.score),
        "position": Position.FORWARD.value,
    }
    assert Member.from_dict(member_dict) == member


def test_member_to_string(member: Member) -> None:
    assert member.to_string(show_skill=True, show_position=True, show_guest=True) == "Member Name  💪300  ⏩"
    assert member.to_string(show_skill=False, show_position=True, show_guest=True) == "Member Name  ⏩"
    assert member.to_string(show_skill=True, show_position=False, show_guest=True) == "Member Name  💪300"
    assert member.to_string(show_skill=False, show_position=False, show_guest=False) == "Member Name"


# Guest
def test_guest_default_values(guest: Guest) -> None:
    assert isinstance(guest.name, str)
    assert guest.name == "Guest Name"

    assert isinstance(guest.skill, int)
    assert guest.skill == Skill.AVERAGE.score

    assert isinstance(guest.position, str)
    assert guest.position == Position.FORWARD.value


def test_guest_custom_values(guest: Guest) -> None:
    guest = Guest(name="Guest Name", skill=420, position="Defense")

    assert guest.name == "Guest Name"
    assert guest.skill == 420
    assert guest.position == "Defense"


def test_guest_to_dict(guest: Guest) -> None:
    guest_dict = guest.to_dict()
    assert isinstance(guest_dict, dict)

    assert guest_dict == {
        "_id": "Guest Name",
        "skill": str(Skill.AVERAGE.score),
        "position": Position.FORWARD.value,
    }


def test_guest_from_dict(guest: Guest) -> None:
    guest_dict = {
        "_id": "Guest Name",
        "skill": str(Skill.AVERAGE.score),
        "position": Position.FORWARD.value,
    }
    assert Guest.from_dict(guest_dict) == guest


def test_guest_to_string(guest: Guest) -> None:
    assert guest.to_string(show_skill=True, show_position=True, show_guest=True) == "Guest Name  💪300  ⏩  👤"
    assert guest.to_string(show_skill=True, show_position=True, show_guest=False) == "Guest Name  💪300  ⏩"


# TeamDistributionMetrics
def test_team_distribution_metrics(team_distribution_metrics: TeamDistributionMetrics) -> None:
    assert isinstance(team_distribution_metrics.goalie_number_difference, int)
    assert team_distribution_metrics.goalie_number_difference == 1

    assert isinstance(team_distribution_metrics.defense_number_difference, int)
    assert team_distribution_metrics.defense_number_difference == 1

    assert isinstance(team_distribution_metrics.skill_difference, int)
    assert team_distribution_metrics.skill_difference == 100

    assert isinstance(team_distribution_metrics.defense_skill_difference, int)
    assert team_distribution_metrics.defense_skill_difference == 50


def test_team_metrics_operators() -> None:
    team_metrics_1 = TeamDistributionMetrics(
        goalie_number_difference=0,
        defense_number_difference=0,
        skill_difference=0,
        defense_skill_difference=0,
    )
    team_metrics_2 = TeamDistributionMetrics(
        goalie_number_difference=0,
        defense_number_difference=0,
        skill_difference=0,
        defense_skill_difference=1,
    )
    team_metrics_3 = TeamDistributionMetrics(
        goalie_number_difference=0,
        defense_number_difference=0,
        skill_difference=1,
        defense_skill_difference=0,
    )
    team_metrics_4 = TeamDistributionMetrics(
        goalie_number_difference=0,
        defense_number_difference=1,
        skill_difference=0,
        defense_skill_difference=0,
    )
    team_metrics_5 = TeamDistributionMetrics(
        goalie_number_difference=1,
        defense_number_difference=0,
        skill_difference=0,
        defense_skill_difference=0,
    )

    assert team_metrics_1 < team_metrics_2
    assert team_metrics_2 < team_metrics_3
    assert team_metrics_3 < team_metrics_4
    assert team_metrics_4 < team_metrics_5


# TeamDistribution
# TODO: Add tests for TeamDistribution
