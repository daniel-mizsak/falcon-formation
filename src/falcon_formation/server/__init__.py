"""
Init file for the server.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from urllib.parse import parse_qs

from flask import Flask

server: Flask = Flask(__name__)
server.url_map.strict_slashes = False


def parse_search_parameters(search: str) -> dict[str, str]:
    """Parse the search parameters from the URL.

    Args:
        search (str): The URL search parameters.

    Returns:
        dict[str, str]: The parsed search parameters.
    """
    try:
        parsed_qs = parse_qs(search.lstrip("?"))
        parsed_query: dict[str, str] = {}
        for key in parsed_qs:
            parsed_query[key] = parsed_qs[key][0]
    except (KeyError, ValueError, TypeError):
        return {}
    return parsed_query


import falcon_formation.server.routes  # noqa: E402, F401
from falcon_formation.server.add_guests import add_guests_app  # noqa: E402, F401
from falcon_formation.server.edit_team import edit_team_app  # noqa: E402, F401
from falcon_formation.server.manage_team import manage_team_app  # noqa: E402, F401

__all__ = ["server"]
