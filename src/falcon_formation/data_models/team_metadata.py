"""
Team metadata data model.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass()
class TeamMetadata:
    """Data class for storing data of team metadata."""

    _id: int
    name: str
    activity_name: str = ""
    # TODO: Add how much time before the practice the notification should be sent
    jersey_color_1: str = ""
    jersey_color_2: str = ""
    telegram_chat_id: int = 0

    def to_dict(self: TeamMetadata) -> dict[str, str]:
        """Return the team metadata as a dictionary for serialization.

        Args:
            self (TeamMetadata): The team metadata object.

        Returns:
            dict[str, str]: The team metadata as a dictionary.
        """
        return {
            "_id": str(self._id),
            "name": self.name,
            "activity_name": self.activity_name,
            "jersey_color_1": self.jersey_color_1,
            "jersey_color_2": self.jersey_color_2,
            "telegram_chat_id": str(self.telegram_chat_id),
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> TeamMetadata:
        """Return the team metadata from a dictionary.

        Args:
            data (dict[str, str]): The team metadata as a dictionary.

        Returns:
            TeamMetadata: The team metadata object.
        """
        return cls(
            _id=int(data["_id"]),
            name=data["name"],
            activity_name=data.get("activity_name", ""),
            jersey_color_1=data.get("jersey_color_1", ""),
            jersey_color_2=data.get("jersey_color_2", ""),
            telegram_chat_id=int(data.get("telegram_chat_id", 0)),
        )
