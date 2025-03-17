"""
Init file for the server.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import os
from urllib.parse import parse_qs

from flask import Flask

from falcon_formation import (
    HOLDSPORT_PASSWORD_KEY,
    HOLDSPORT_USERNAME_KEY,
    MONGO_PASSWORD_KEY,
    MONGO_USERNAME_KEY,
    # TELEGRAM_TOKEN_KEY,
)
from falcon_formation.database import FalconFormationDatabase
from falcon_formation.holdsport_api import HoldsportAPI

# from falcon_formation.telegram_api import TelegramAPI  # noqa: ERA001

server: Flask = Flask(__name__)
server.url_map.strict_slashes = False

database = FalconFormationDatabase(
    # host="mongo",
    host="localhost",
    port=27017,
    username=str(os.getenv(MONGO_USERNAME_KEY)),
    password=str(os.getenv(MONGO_PASSWORD_KEY)),
)
holdsport_api = HoldsportAPI(
    login=str(os.getenv(HOLDSPORT_USERNAME_KEY)),
    password=str(os.getenv(HOLDSPORT_PASSWORD_KEY)),
)
# telegram_api = TelegramAPI(token=str(os.getenv(TELEGRAM_TOKEN_KEY)))  # noqa: ERA001


def parse_search_parameters(search: str) -> int | None:
    """Parse the search parameters from the URL.

    Args:
        search (str): The URL search parameters.

    Returns:
        int | None: The team id if it can be parsed, otherwise None.
    """
    try:
        parsed_query = parse_qs(search.lstrip("?"))
        team_id = int(parsed_query["team_id"][0])
    except (KeyError, ValueError, TypeError):
        return None
    return team_id


import falcon_formation.server.routes  # noqa: E402, F401
from falcon_formation.server.add_guests import add_guests_app  # noqa: E402, F401
from falcon_formation.server.edit_team import edit_team_app  # noqa: E402, F401
from falcon_formation.server.manage_team import manage_team_app  # noqa: E402, F401

add_guests_app.logger.disabled = False

__all__ = ["server"]
