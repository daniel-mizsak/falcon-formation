"""
Guest data model.

Guests are players who cannot register through Holdsport and are not regular attendees.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from __future__ import annotations

from dataclasses import dataclass

from falcon_formation.data_models.player import Player
from falcon_formation.data_models.position import Position
from falcon_formation.data_models.skill import Skill


@dataclass()
class Guest(Player):
    """Data class for storing data of guests."""

    name: str
    skill: int = Skill.AVERAGE.score
    position: str = Position.FORWARD.value

    def to_dict(self: Guest) -> dict[str, str]:
        """Return the guest data as a dictionary.

        Args:
            self (Guest): The guest object.

        Returns:
            dict[str, int | str]: The guest data as a dictionary.
        """
        return {
            "_id": self.name,
            "skill": str(self.skill),
            "position": self.position,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> Guest:
        """Return the guest data from a dictionary.

        Args:
            data (dict[str, int | str]): The guest data as a dictionary.

        Returns:
            Guest: The guest object.
        """
        return cls(
            name=data["_id"],
            skill=int(data.get("skill", Skill.AVERAGE.score)),
            position=data.get("position", Position.FORWARD.value),
        )
