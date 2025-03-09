"""
Tests for the Holdsport API.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from datetime import datetime

import pytest
from aioresponses import aioresponses

from falcon_formation.holdsport_api import HoldsportAPI


@pytest.mark.asyncio
async def test_get_users_attending_activity(holdsport_api: HoldsportAPI) -> None:
    with aioresponses() as m:
        m.get(
            "https://api.holdsport.dk/v1/activities/1/activities_users",
            payload=[
                {
                    "id": 1,
                    "user_id": 1,
                    "name": " Rihouse   Peace",
                    "status": "Attending",
                    "status_code": 1,
                    "updated_at": "2024-01-01T00:00:00+00:00",
                },
                {
                    "id": 2,
                    "user_id": 2,
                    "name": " Roberto  Orszagos",
                    "status": "Not attending",
                    "status_code": 2,
                    "updated_at": "2024-01-01T00:00:00+00:00",
                },
                {
                    "id": 3,
                    "user_id": 3,
                    "name": "Sø Ø Possum   ",
                    "status": "Attending",
                    "status_code": 1,
                    "updated_at": "2024-01-01T00:00:00+00:00",
                },
                {
                    "id": 4,
                    "user_id": 4,
                    "name": " Tobias Elias",
                    "status": "Not attending",
                    "status_code": 1,
                    "updated_at": "2024-01-01T00:00:00+00:00",
                },
            ],
        )
        registered_players = await holdsport_api.get_users_attending_activity(activity_id=1)
        assert registered_players == [
            {"_id": 1, "name": "RIHOUSE PEACE"},
            {"_id": 3, "name": "SØ Ø POSSUM"},
        ]


@pytest.mark.asyncio
async def test_get_users_attending_activity_with_non_existing_activity_id(holdsport_api: HoldsportAPI) -> None:
    with aioresponses() as m:
        m.get(
            "https://api.holdsport.dk/v1/activities/1/activities_users",
            payload=[],
        )
        registered_players = await holdsport_api.get_users_attending_activity(activity_id=1)
        assert registered_players == []


@pytest.mark.asyncio
async def test_get_users_attending_activity_with_not_ok_status_code(holdsport_api: HoldsportAPI) -> None:
    with aioresponses() as m:
        m.get(
            "https://api.holdsport.dk/v1/activities/1/activities_users",
            status=500,
        )
        registered_players = await holdsport_api.get_users_attending_activity(activity_id=1)
        assert registered_players == []


@pytest.mark.asyncio
async def test_get_activity_id(holdsport_api: HoldsportAPI) -> None:
    with aioresponses() as m:
        m.get(
            "https://api.holdsport.dk/v1/teams/123456/activities?date=2024-01-01",
            payload=[
                {
                    "name": "Team Example - Training",
                    "starttime": "2024-01-01T00:00:00+00:00",
                    "id": 1,
                },
            ],
        )
        activity_id = await holdsport_api.get_activity_id(
            team_id=123456,
            date="2024-01-01",
            activity_name="Team Example - Training",
        )
        assert activity_id == 1


@pytest.mark.asyncio
async def test_get_activity_id_with_non_existing_activity(holdsport_api: HoldsportAPI) -> None:
    with aioresponses() as m:
        m.get(
            "https://api.holdsport.dk/v1/teams/123456/activities?date=2024-01-01",
            payload=[],
        )
        activity_id = await holdsport_api.get_activity_id(
            team_id=123456,
            date="2024-01-01",
            activity_name="Team Example - Training",
        )
        assert activity_id is None


@pytest.mark.asyncio
async def test_get_activity_id_with_not_ok_status_code(holdsport_api: HoldsportAPI) -> None:
    with aioresponses() as m:
        m.get(
            "https://api.holdsport.dk/v1/teams/123456/activities?date=2024-01-01",
            status=500,
        )
        activity_id = await holdsport_api.get_activity_id(
            team_id=123456,
            date="2024-01-01",
            activity_name="Team Example - Training",
        )
        assert activity_id is None


@pytest.mark.asyncio
async def test_get_upcoming_activity_dates(holdsport_api: HoldsportAPI) -> None:
    with aioresponses() as m:
        m.get(
            "https://api.holdsport.dk/v1/teams/123456/activities?per_page=9",
            payload=[
                {
                    "name": "Team Example - Training",
                    "starttime": "2024-01-01T00:00:00+00:00",
                    "id": 1,
                },
                {
                    "name": "Team Example - Other",
                    "starttime": "2024-01-02T00:00:00+00:00",
                    "id": 2,
                },
                {
                    "name": "Team Example - Training",
                    "starttime": "2024-01-03T00:00:00+00:00",
                    "id": 3,
                },
                {
                    "name": "Team Example - Other",
                    "starttime": "2024-01-04T00:00:00+00:00",
                    "id": 4,
                },
                {
                    "name": "Team Example - Training",
                    "starttime": "2024-01-05T00:00:00+00:00",
                    "id": 5,
                },
                {
                    "name": "Team Example - Other",
                    "starttime": "2024-01-06T00:00:00+00:00",
                    "id": 6,
                },
                {
                    "name": "Team Example - Training",
                    "starttime": "2024-01-07T00:00:00+00:00",
                    "id": 7,
                },
                {
                    "name": "Team Example - Other",
                    "starttime": "2024-01-08T00:00:00+00:00",
                    "id": 8,
                },
                {
                    "name": "Team Example - Training",
                    "starttime": "2024-01-09T00:00:00+00:00",
                    "id": 9,
                },
            ],
        )
        practice_dates = await holdsport_api.get_upcoming_activity_dates(
            team_id=123456,
            activity_name="Team Example - Training",
            number_of_dates=3,
        )
        expected_dates = [
            datetime.strptime("2024-01-01T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z").date(),
            datetime.strptime("2024-01-03T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z").date(),
            datetime.strptime("2024-01-05T00:00:00+00:00", "%Y-%m-%dT%H:%M:%S%z").date(),
        ]
        assert practice_dates == expected_dates


@pytest.mark.asyncio
async def test_get_upcoming_activity_dates_with_not_ok_status_code(holdsport_api: HoldsportAPI) -> None:
    with aioresponses() as m:
        m.get(
            "https://api.holdsport.dk/v1/teams/123456/activities?per_page=9",
            status=500,
        )
        practice_dates = await holdsport_api.get_upcoming_activity_dates(
            team_id=123456,
            activity_name="Team Example - Training",
            number_of_dates=3,
        )
        assert practice_dates == []


@pytest.mark.asyncio
async def test_get_users_in_teams(holdsport_api: HoldsportAPI) -> None:
    with aioresponses() as m:
        m.get(
            "https://api.holdsport.dk/v1/teams/123456/members",
            payload=[
                {"id": 1, "firstname": "Rihouse", "lastname": "Peace"},
                {"id": 2, "firstname": "Roberto ", "lastname": " Orszagos"},
                {"id": 3, "firstname": "Sø Ø", "lastname": "Possum  "},
                {"id": 4, "firstname": " Tobias", "lastname": "Elias "},
            ],
        )
        team_members = await holdsport_api.get_users_in_team(team_id=123456)
        assert team_members == [
            {"_id": 1, "name": "RIHOUSE PEACE"},
            {"_id": 2, "name": "ROBERTO ORSZAGOS"},
            {"_id": 3, "name": "SØ Ø POSSUM"},
            {"_id": 4, "name": "TOBIAS ELIAS"},
        ]


@pytest.mark.asyncio
async def test_get_users_in_team_with_not_ok_status_code(holdsport_api: HoldsportAPI) -> None:
    with aioresponses() as m:
        m.get(
            "https://api.holdsport.dk/v1/teams/123456/members",
            status=500,
        )
        team_members = await holdsport_api.get_users_in_team(team_id=123456)
        assert team_members == []


@pytest.mark.asyncio
async def test_get_teams(holdsport_api: HoldsportAPI) -> None:
    with aioresponses() as m:
        m.get(
            "https://api.holdsport.dk/v1/teams",
            payload=[
                {"id": 123456, "name": "TEAM_EXAMPLE"},
                {"id": 234567, "name": "TEAM_OTHER_EXAMPLE"},
            ],
        )
        teams = await holdsport_api.get_teams()
        expected_teams: list[dict[str, str]] = [
            {"_id": "123456", "name": "TEAM_EXAMPLE"},
            {"_id": "234567", "name": "TEAM_OTHER_EXAMPLE"},
        ]
        assert sorted(teams, key=lambda x: x["_id"]) == sorted(expected_teams, key=lambda x: x["_id"])


@pytest.mark.asyncio
async def test_get_teams_with_not_ok_status_code(holdsport_api: HoldsportAPI) -> None:
    with aioresponses() as m:
        m.get(
            "https://api.holdsport.dk/v1/teams",
            status=500,
        )
        teams = await holdsport_api.get_teams()
        assert teams == []


@pytest.mark.asyncio
async def test_get_activity_names_with_minimum_occurrences(holdsport_api: HoldsportAPI) -> None:
    with aioresponses() as m:
        m.get(
            "https://api.holdsport.dk/v1/teams/123456/activities?per_page=8",
            payload=[
                {"name": "Team Example - Training"},
                {"name": "Team Example - Christmas 1"},
                {"name": "Team Example - Christmas 2"},
                {"name": "Team Example - Other"},
                {"name": "Team Example - Training"},
                {"name": "Team Example - Other"},
                {"name": "Team Example - New Year 1"},
                {"name": "Team Example - Training"},
            ],
        )
        activity_names = await holdsport_api.get_activity_names_with_minimum_occurrences(team_id=123456)
        assert activity_names == sorted(["Team Example - Training", "Team Example - Other"])


@pytest.mark.asyncio
async def test_get_activity_names_with_minimum_occurrences_with_not_ok_status_code(
    holdsport_api: HoldsportAPI,
) -> None:
    with aioresponses() as m:
        m.get(
            "https://api.holdsport.dk/v1/teams/123456/activities?per_page=8",
            status=500,
        )
        activity_names = await holdsport_api.get_activity_names_with_minimum_occurrences(team_id=123456)
        assert activity_names == []
