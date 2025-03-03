"""
Member data model.

Members are players who can register through Holdsport and are regular attendees.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from __future__ import annotations

from dataclasses import dataclass

from falcon_formation.data_models.player import Player
from falcon_formation.data_models.position import Position
from falcon_formation.data_models.skill import Skill


@dataclass()
class Member(Player):
    """Data class for storing data of members."""

    _id: int
    name: str
    skill: int = Skill.AVERAGE.score
    position: str = Position.FORWARD.value

    def __post_init__(self: Member) -> None:
        # TODO: This function should not be necessary if every member class is created properly.
        """Further validate the member data."""
        super().__post_init__()
        if not isinstance(self._id, int):
            msg = f"Invalid member id: {self._id}\nMember id must be an integer."  # type: ignore[unreachable]
            raise TypeError(msg)

    def to_dict(self: Member) -> dict[str, str]:
        """Return the member data as a dictionary.

        Args:
            self (Member): The member object.

        Returns:
            dict[str, str]: The member data as a dictionary.
        """
        return {
            "_id": str(self._id),
            "name": self.name,
            "skill": str(self.skill),
            "position": self.position,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> Member:
        """Return the member data from a dictionary.

        Args:
            data (dict[str, int | str]): The member data as a dictionary.

        Returns:
            Member: The member object.
        """
        return cls(
            _id=int(data["_id"]),
            name=data["name"],
            skill=int(data.get("skill", Skill.AVERAGE.score)),
            position=data.get("position", Position.FORWARD.value),
        )
