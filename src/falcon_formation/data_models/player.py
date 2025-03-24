"""
Player data model.

Players are the base class for team members and guests.
Players objects are used to generate teams as it only requires the name, skill, and position of the player.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from falcon_formation.data_models.position import Position
from falcon_formation.data_models.skill import Skill


class Player(ABC):
    """Abstract base class for storing data of players."""

    name: str
    skill: int
    position: str

    def __post_init__(self: Player) -> None:
        """Validate the player data.

        Args:
            self (Player): The Player object.

        Raises:
            ValueError: If the player data has an invalid value.
        """
        if not len(self.name):
            msg = f"Invalid player name: {self.name}\nPlayer name must not be empty."
            raise ValueError(msg)

        if Skill.MINIMUM.score > self.skill:
            self.skill = max(self.skill, Skill.MINIMUM.score)

        if Skill.MAXIMUM.score < self.skill:
            self.skill = min(self.skill, Skill.MAXIMUM.score)

        if self.position not in list(map(str, Position)):
            msg = (
                f"Invalid position: {self.position} for player: {self.name}\n"
                f"Valid positions: {list(map(str, Position))}"
            )
            raise ValueError(msg)

    @abstractmethod
    def to_dict(self) -> dict[str, str]:
        """Return the player data as a dictionary."""

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict[str, str]) -> Player:
        """Return the player data from a dictionary."""

    def to_string(self: Player, show_skill: bool, show_position: bool, show_guest: bool) -> str:  # noqa: FBT001
        """Return the player data as a string.

        Args:
            self (Player): The Player object.
            show_skill (bool): Whether to show the skill.
            show_position (bool): Whether to show the position.
            show_guest (bool): Whether to show the guest emoji.

        Returns:
            str: The player data as a string.
        """
        from falcon_formation.data_models import Guest

        guest_emoji = "  👤" if isinstance(self, Guest) else ""
        position_emoji = Position(self.position).emoji

        player_string = f"{self.name}"
        if show_skill:
            player_string += f"  💪{self.skill}"
        if show_position:
            player_string += f"  {position_emoji}"
        if show_guest:
            player_string += guest_emoji

        return player_string
