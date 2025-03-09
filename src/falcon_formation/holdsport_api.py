"""
Class implementation for interacting with the Holdsport API.

https://github.com/Holdsport/holdsport-api

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from __future__ import annotations

import datetime
import re
from collections import Counter

import aiohttp

from falcon_formation import STATUS_CODE_OK


class HoldsportAPI:
    """Class for interacting with the Holdsport API."""

    def __init__(self: HoldsportAPI, login: str, password: str) -> None:
        """Initialization of the HoldsportAPI object."""
        self.timeout = aiohttp.ClientTimeout(total=10)
        self.auth = aiohttp.BasicAuth(login, password)
        self.headers = {"Accept": "application/json"}

    async def get_users_attending_activity(self: HoldsportAPI, activity_id: int) -> list[dict[str, str]]:
        """Return a list of dictionaries containing the ids and names of users attending the activity.

        Args:
            self (HoldsportAPI): The HoldsportAPI object.
            activity_id (int): The id of the activity in the Holdsport system.

        Returns:
            list[dict[str, str]]: List of dictionaries containing the ids and names of users attending the activity.
        """
        url = f"https://api.holdsport.dk/v1/activities/{activity_id}/activities_users"
        async with (
            aiohttp.ClientSession(timeout=self.timeout) as session,
            session.get(url, headers=self.headers, auth=self.auth) as response,
        ):
            if response.status != STATUS_CODE_OK:
                return []
            response_dict = await response.json()

        users = []
        for response_entry in response_dict:
            if response_entry["status"] == "Attending":
                # Replace multiple spaces with a single space and remove leading/trailing spaces
                name = re.sub(r"\s+", " ", response_entry["name"]).strip().upper()
                users.append({"_id": response_entry["user_id"], "name": name})
        return sorted(users, key=lambda x: x["name"])

    async def get_activity_id(self: HoldsportAPI, team_id: int, date: str, activity_name: str) -> int | None:
        """Return the id of the activity on the given date for a team or None if there is no such activity.

        Args:
            self (HoldsportAPI): The HoldsportAPI object.
            team_id (int): The id of the team in the Holdsport system.
            date (str): The date of the activity in format "YYYY-MM-DD".
            activity_name (str): The name of the activity in the Holdsport system.

        Returns:
            int | None: The id of the activity or None if there is no such activity.
        """
        url = f"https://api.holdsport.dk/v1/teams/{team_id}/activities?date={date}"
        async with (
            aiohttp.ClientSession(timeout=self.timeout) as session,
            session.get(url, headers=self.headers, auth=self.auth) as response,
        ):
            if response.status != STATUS_CODE_OK:
                return None
            response_dict = await response.json()

        for response_entry in response_dict:
            start_time = str(datetime.datetime.strptime(response_entry["starttime"], "%Y-%m-%dT%H:%M:%S%z").date())
            if (response_entry["name"] == activity_name) and (date == start_time) and (response_entry["id"]):
                return int(response_entry["id"])
        return None

    async def get_upcoming_activity_dates(
        self: HoldsportAPI,
        team_id: int,
        activity_name: str,
        number_of_dates: int = 4,
    ) -> list[datetime.date]:
        """Return the list of upcoming dates for a given activity for a team.

        Args:
            self (HoldsportAPI): The HoldsportAPI object.
            team_id (int): The id of the team in the Holdsport system.
            activity_name (str): The name of the activity in the Holdsport system.
            number_of_dates (int, optional): The number of upcoming dates to return. Defaults to 4. Maximum is 10.

        Returns:
            list[datetime.date]: The list of upcoming dates for the activity for the team.
        """
        number_of_dates = min(number_of_dates, 10)
        activities_to_query = number_of_dates**2
        activity_dates = []
        while True:
            url = f"https://api.holdsport.dk/v1/teams/{team_id}/activities?per_page={activities_to_query}"
            async with (
                aiohttp.ClientSession(timeout=self.timeout) as session,
                session.get(url, headers=self.headers, auth=self.auth) as response,
            ):
                if response.status != STATUS_CODE_OK:
                    return []
                response_dict = await response.json()

            for response_entry in response_dict:
                if response_entry["name"] == activity_name:
                    start_time = datetime.datetime.strptime(response_entry["starttime"], "%Y-%m-%dT%H:%M:%S%z")
                    activity_dates.append(start_time.date())
                if len(activity_dates) == number_of_dates:
                    break

            if len(activity_dates) < number_of_dates:
                activities_to_query += number_of_dates
                activity_dates = []
            else:
                break

        return sorted(activity_dates)

    async def get_users_in_team(self: HoldsportAPI, team_id: int) -> list[dict[str, str]]:
        """Return a list of dictionaries containing the ids and names of users who are members of a team.

        Args:
            self (HoldsportAPI): The HoldsportAPI object.
            team_id (int): The id of the team in the Holdsport system.

        Returns:
            list[dict[str, str]]: List of dictionaries containing the ids and names of users of a team.
        """
        url = f"https://api.holdsport.dk/v1/teams/{team_id}/members"
        async with (
            aiohttp.ClientSession(timeout=self.timeout) as session,
            session.get(url, headers=self.headers, auth=self.auth) as response,
        ):
            if response.status != STATUS_CODE_OK:
                return []
            response_dict = await response.json()

        users = []
        for response_entry in response_dict:
            # Replace multiple spaces with a single space and remove leading/trailing spaces
            first_name = re.sub(r"\s+", " ", response_entry["firstname"]).strip().upper()
            last_name = re.sub(r"\s+", " ", response_entry["lastname"]).strip().upper()

            users.append({"_id": response_entry["id"], "name": f"{first_name} {last_name}"})
        return sorted(users, key=lambda x: x["name"])

    async def get_teams(self: HoldsportAPI) -> list[dict[str, str]]:
        """Return a list of dictionaries containing the ids and names of teams.

        Returns:
            list[dict[str, str]]: List of dictionaries containing the ids and names of teams.
        """
        url = "https://api.holdsport.dk/v1/teams"
        async with (
            aiohttp.ClientSession(timeout=self.timeout) as session,
            session.get(url, headers=self.headers, auth=self.auth) as response,
        ):
            if response.status != STATUS_CODE_OK:
                return []
            response_dict = await response.json()

        return [
            {"_id": str(response_entry["id"]), "name": str(response_entry["name"])} for response_entry in response_dict
        ]

    async def get_activity_names_with_minimum_occurrences(
        self: HoldsportAPI,
        team_id: int,
        activities_to_query: int = 8,
        minimum_occurrences: int = 2,
    ) -> list[str]:
        """Return the list of activity names that occur more times than specified.

        Args:
            self (HoldsportAPI): The HoldsportAPI object.
            team_id (int): The id of the team in the Holdsport system.
            activities_to_query (int, optional): The number of activities to query. Defaults to 8.
            minimum_occurrences (int, optional): The minimum number of occurrences. Defaults to 2.

        Returns:
            list[str]: The list of activity names that occur more times than specified.
        """
        url = f"https://api.holdsport.dk/v1/teams/{team_id}/activities?per_page={activities_to_query}"
        async with (
            aiohttp.ClientSession(timeout=self.timeout) as session,
            session.get(url, headers=self.headers, auth=self.auth) as response,
        ):
            if response.status != STATUS_CODE_OK:
                return []
            response_dict = await response.json()

        activity_occurrences = Counter(response_entry["name"] for response_entry in response_dict)
        return sorted(
            [
                activity_name
                for activity_name, occurrence in activity_occurrences.items()
                if occurrence >= minimum_occurrences
            ],
        )
