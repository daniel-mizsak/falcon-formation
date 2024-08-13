"""
Data classes for storing player data and team metrics.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, TypeAlias


@dataclass(frozen=True)
class Player:
    """Data class for storing player data."""

    name: str
    skill: int
    positions: tuple[str, ...]

    SKILL_OPTIONS: ClassVar[dict[int, str]] = {
        1: "Fairly Below Average",
        2: "Below Average",
        3: "Average",
        4: "Above Average",
        5: "Fairly Above Average",
    }

    POSITION_OPTIONS: ClassVar[dict[str, str]] = {
        "G": "Goalie",
        "LD": "Left Defender",
        "RD": "Right Defender",
        "LW": "Left Wing",
        "RW": "Right Wing",
        "C": "Center",
    }

    def __post_init__(self: Player) -> None:
        """Validate the player data.

        Args:
            self (Player): The Player object.

        Raises:
            ValueError: If the skill level or position is invalid.
        """
        if self.skill not in self.SKILL_OPTIONS:
            msg = f"Invalid skill level: {self.skill}"
            raise ValueError(msg)
        if any(position not in self.POSITION_OPTIONS for position in self.positions):
            msg = f"Invalid position: {self.positions}"
            raise ValueError(msg)

    def to_tuple(self: Player) -> tuple[str, str, str]:
        """Return the player data as a tuple.

        Returns:
            tuple[str, str, str]: The player data as a tuple.
        """
        return (
            self.name,
            self.SKILL_OPTIONS[self.skill],
            ", ".join(self.POSITION_OPTIONS[position] for position in self.positions),
        )

    @classmethod
    def from_tuple(cls, data: tuple[str, str, str]) -> Player:  # noqa: ANN102, RUF100
        """Create a Player object from a tuple.

        Args:
            data (tuple[str, str, str]): The player data as a tuple.

        Returns:
            Player: The Player object.
        """
        name_input, skill_input, positions_input = data
        name: str = name_input
        skill: int = {v: k for k, v in cls.SKILL_OPTIONS.items()}[skill_input]
        positions: tuple[str, ...] = tuple(
            {v: k for k, v in cls.POSITION_OPTIONS.items()}[position] for position in positions_input.split(", ")
        )
        return cls(name, skill, positions)


@dataclass(eq=True, order=True, frozen=True)
class TeamMetrics:
    """Data class for storing team metrics."""

    goalie_number_difference: int
    defense_number_difference: int
    skill_difference: int


# TODO: Use `type` keyword solution when dropping Python 3.11.
TeamDistribution: TypeAlias = tuple[set[Player], set[Player]]  # noqa: UP040


@dataclass(frozen=True)
class TeamData:
    """Data class for storing a team's members and metrics."""

    teams: TeamDistribution
    metrics: TeamMetrics
