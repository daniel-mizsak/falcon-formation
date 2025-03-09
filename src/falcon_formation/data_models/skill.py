"""
Skill data model.

Available pre-defined player skill values and helper methods.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from __future__ import annotations

from enum import Enum


class Skill(Enum):
    """Enum class for player skills."""

    MINIMUM = (-500, "Minimum")
    WELL_BELOW_AVERAGE = (100, "Well below average")
    BELOW_AVERAGE = (200, "Below average")
    AVERAGE = (300, "Average")
    ABOVE_AVERAGE = (400, "Above average")
    WELL_ABOVE_AVERAGE = (500, "Well above average")
    MAXIMUM = (1000, "Maximum")

    @property
    def score(self: Skill) -> int:
        """Return the skill score."""
        return self.value[0]

    @property
    def description(self: Skill) -> str:
        """Return the skill description."""
        return self.value[1]

    @staticmethod
    def to_dropdown_options() -> list[dict[str, int | str]]:
        """Return the skill levels as dropdown options for Dash."""
        return [{"label": v.description, "value": v.score} for v in Skill if v not in (Skill.MINIMUM, Skill.MAXIMUM)]

    @staticmethod
    def get_description_from_value(score: int) -> str | None:
        """Return the skill description from the skill score."""
        for skill in Skill:
            if skill.score == score:
                return skill.description
        return None
