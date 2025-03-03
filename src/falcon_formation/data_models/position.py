"""
Position data model.

Available player positions and helper methods.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from __future__ import annotations

from enum import StrEnum


class Position(StrEnum):
    """Enum class for player positions."""

    DEFENSE = "Defense"
    FORWARD = "Forward"
    GOALIE = "Goalie"

    @property
    def emoji(self) -> str:
        """Return the emoji representation of the position."""
        emojis = {
            "Defense": "⏮️",
            "Forward": "⏩",
            "Goalie": "⏹️",
        }
        return emojis[self.value]

    @staticmethod
    def to_dropdown_options() -> list[dict[str, str]]:
        """Return the player positions as dropdown options for Dash."""
        return [{"label": v.value, "value": v.value} for v in Position]
