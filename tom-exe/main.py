import json
import unicodedata
from datetime import datetime

import requests

STAUS_CODE_OK = 200


def _get_activity_id(team_id: int, date: str, activity_name: str, auth: tuple[str, str]) -> int | None:
    url = f"https://api.holdsport.dk/v1/teams/{team_id}/activities?date={date}"
    headers = {"Accept": "application/json"}

    response = requests.get(url, headers=headers, auth=auth, timeout=5)
    if response.status_code != STAUS_CODE_OK:
        return None
    response_dict = json.loads(response.text)

    for response_entry in response_dict:
        start_time = str(datetime.strptime(response_entry["starttime"], "%Y-%m-%dT%H:%M:%S%z").date())

        if (response_entry["name"] == activity_name) and (date == start_time) and (response_entry["id"]):
            return int(response_entry["id"])
    return None


def get_registered_players(
    team_id: int, date: str, activity_name: str, status: str, auth: tuple[str, str]
) -> list[str]:
    activity_id = _get_activity_id(team_id, date, activity_name, auth)
    if activity_id is None:
        return []

    url = f"https://api.holdsport.dk/v1/activities/{activity_id}/activities_users"
    headers = {"Accept": "application/json"}

    response = requests.get(url, headers=headers, auth=auth, timeout=5)
    if response.status_code != STAUS_CODE_OK:
        return []
    response_dict = json.loads(response.text)

    registered_players = []
    for user in response_dict:
        if user["status"] == status:
            user_name = unicodedata.normalize("NFKD", user["name"]).replace("\xa0", " ")
            registered_players.append(user_name)

    return sorted(registered_players)


if __name__ == "__main__":
    with open("data.txt") as file_handle:
        data = file_handle.read().split("\n")

    team_id = int(data[0].split("=")[1])
    date = data[1].split("=")[1]
    activity_name = data[2].split("=")[1]
    status = data[3].split("=")[1]
    auth = (data[4].split("=")[1], data[5].split("=")[1])

    registered_players = get_registered_players(team_id, date, activity_name, status, auth)

    print(f"Registered players for {activity_name} on {date}:\n")

    for registered_player in registered_players:
        print(registered_player)

    input("\n\nPress enter to exit.")
