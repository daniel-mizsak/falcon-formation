"""
Init file for the package.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

STATUS_CODE_OK = 200

GOALIE_RETURN_DICTIONARY: dict[int, str] = {
    0: "Oh-oh! No goalie registered for today's practice yet. Please reach out to other goalies.",
    1: "Attention! Only 1 goalie registered for today's practice! Please reach out to other goalies.",
    2: "Good news! There are exactly 2 goalies registered for today's practice.",
}

JERSEY_COLORS: dict[str, tuple[str, str]] = {
    "FALCONS_1": ("RED", "BLACK"),
}
