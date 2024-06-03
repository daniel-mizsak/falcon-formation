"""
Helper functions for interacting with the Holdsport API.

https://github.com/Holdsport/holdsport-api

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import json
import unicodedata
from datetime import datetime

import requests

from falcon_formation import STATUS_CODE_OK


def get_registered_players(team_id: int, date: str, auth: tuple[str, str]) -> list[str]:
    """Return the list of players who registered for "Motion A" practice on the given date.

    Args:
        team_id (int): The ID of the team in the Holdsport system. Get it through the Holdsport API.
        date (str): The date of the practice in the format "YYYY-MM-DD".
        auth (tuple[str, str]): A tuple containing the username and password for the Holdsport API authentication.

    Returns:
        list[str]: The list of the names of the players who registered for the practice.
    """
    activity_id = _get_activity_id(team_id, date, auth)
    if activity_id is None:
        return []

    url = f"https://api.holdsport.dk/v1/activities/{activity_id}/activities_users"
    headers = {"Accept": "application/json"}

    response = requests.get(url, headers=headers, auth=auth, timeout=5)
    if response.status_code != STATUS_CODE_OK:
        return []
    response_dict = json.loads(response.text)

    registered_players = []
    for user in response_dict:
        if user["status"] == "Attending":
            user_name = unicodedata.normalize("NFKD", user["name"])
            registered_players.append(user_name)

    return sorted(registered_players)


def _get_activity_id(team_id: int, date: str, auth: tuple[str, str]) -> int | None:
    """Return the activity ID of the "Motion A" practice on the given date.

    Args:
        team_id (int): The ID of the team in the Holdsport system. Get it through the Holdsport API.
        date (str): The date of the practice in the format "YYYY-MM-DD".
        auth (tuple[str, str]): A tuple containing the username and password for the Holdsport API authentication.

    Returns:
        int | None: The activity ID of the "Motion A" practice on the given date, or None if no such practice exists.
    """
    url = f"https://api.holdsport.dk/v1/teams/{team_id}/activities?date={date}"
    headers = {"Accept": "application/json"}

    response = requests.get(url, headers=headers, auth=auth, timeout=5)
    if response.status_code != STATUS_CODE_OK:
        return None
    response_dict = json.loads(response.text)

    for response_entry in response_dict:
        activity_name = "Motion A practice"
        start_time = str(datetime.strptime(response_entry["starttime"], "%Y-%m-%dT%H:%M:%S%z").date())

        if (response_entry["name"] == activity_name) and (date == start_time) and (response_entry["id"]):
            return int(response_entry["id"])
    return None
