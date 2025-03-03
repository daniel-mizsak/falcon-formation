"""
Team distribution data model.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from __future__ import annotations

from dataclasses import dataclass

from falcon_formation.data_models import Guest, Member, Player


@dataclass(eq=True, order=True, frozen=True)
class TeamDistributionMetrics:
    """Data class for storing data of team distribution metrics."""

    goalie_number_difference: int
    defense_number_difference: int
    skill_difference: int
    defense_skill_difference: int


@dataclass()
class TeamDistribution:
    """Data class for storing data of team distribution."""

    date: str
    team_1: list[Player]
    team_2: list[Player]
    metrics: TeamDistributionMetrics

    def to_dict(self: TeamDistribution) -> dict[str, str | dict[str, list[dict[str, str]]]]:
        """Return the team distribution data as a dictionary.

        Args:
            self (TeamDistribution): The team distribution object.

        Returns:
            dict[str, str | dict[str, list[dict[str, str]]]]: The team distribution data as a dictionary.
        """
        return {
            "_id": self.date,
            "team_1": {
                "members": [player.to_dict() for player in self.team_1 if isinstance(player, Member)],
                "guests": [player.to_dict() for player in self.team_1 if isinstance(player, Guest)],
            },
            "team_2": {
                "members": [player.to_dict() for player in self.team_2 if isinstance(player, Member)],
                "guests": [player.to_dict() for player in self.team_2 if isinstance(player, Guest)],
            },
            "goalie_number_difference": str(self.metrics.goalie_number_difference),
            "defense_number_difference": str(self.metrics.defense_number_difference),
            "skill_difference": str(self.metrics.skill_difference),
            "defense_skill_difference": str(self.metrics.defense_skill_difference),
        }

    @classmethod
    def from_dict(cls, data: dict[str, str | dict[str, list[dict[str, str]]]]) -> TeamDistribution:
        """Return the team distribution data from a dictionary.

        Args:
            data (dict[str, str | dict[str, list[dict[str, str]]]): The team distribution data as a dictionary.

        Returns:
            TeamDistribution: The team distribution object.
        """
        if isinstance(data["team_1"], dict):
            team_1_members: list[Player] = [
                Member.from_dict(p) for p in data["team_1"]["members"] if isinstance(p, dict)
            ]
            team_1_guests: list[Player] = [Guest.from_dict(p) for p in data["team_1"]["guests"]]
        if isinstance(data["team_2"], dict):
            team_2_members: list[Player] = [Member.from_dict(p) for p in data["team_2"]["members"]]
            team_2_guests: list[Player] = [Guest.from_dict(p) for p in data["team_2"]["guests"]]
        if (
            isinstance(data["goalie_number_difference"], str)
            and isinstance(data["defense_number_difference"], str)
            and isinstance(data["skill_difference"], str)
            and isinstance(data["defense_skill_difference"], str)
        ):
            team_distribution_metrics = TeamDistributionMetrics(
                goalie_number_difference=int(data["goalie_number_difference"]),
                defense_number_difference=int(data["defense_number_difference"]),
                skill_difference=int(data["skill_difference"]),
                defense_skill_difference=int(data["defense_skill_difference"]),
            )
        return cls(
            date=str(data["_id"]),
            team_1=team_1_members + team_1_guests,
            team_2=team_2_members + team_2_guests,
            metrics=team_distribution_metrics,
        )
