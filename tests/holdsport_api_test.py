"""
Tests for the falcon_formation.holdsport_api module.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import requests_mock
from falcon_formation.holdsport_api import (
    _get_activity_id,
    _get_list_of_team_members,
    _get_list_of_teams,
    get_registered_players,
)


def test_get_registered_players_with_existing_activity_id() -> None:
    with requests_mock.Mocker() as m:
        m.get(
            "https://api.holdsport.dk/v1/activities/1/activities_users",
            text="""
            [
                {
                    "id": 1,
                    "user_id": 1,
                    "name": "John Doe",
                    "status": "Attending",
                    "status_code": 1,
                    "updated_at": "2024-01-01T00:00:00+00:00"
                },
                {
                    "id": 2,
                    "user_id": 2,
                    "name": "Jane Doe",
                    "status": "Not attending",
                    "status_code": 2,
                    "updated_at": "2024-01-01T00:00:00+00:00"
                },
                {
                    "id": 3,
                    "user_id": 3,
                    "name": "Alice Smith",
                    "status": "Attending",
                    "status_code": 1,
                    "updated_at": "2024-01-01T00:00:00+00:00"
                },
                {
                    "id": 4,
                    "user_id": 4,
                    "name": "Bob Smith",
                    "status": "Not attending",
                    "status_code": 1,
                    "updated_at": "2024-01-01T00:00:00+00:00"
                }
            ]
            """,
        )
        m.get(
            "https://api.holdsport.dk/v1/teams/1/activities?date=2024-01-01",
            text='[{"name": "Falcon practice", "starttime": "2024-01-01T00:00:00+00:00", "id": 1}]',
        )
        registered_players = get_registered_players(1, "2024-01-01", ("username", "password"), "Falcon practice")
        assert registered_players == ["Alice Smith", "John Doe"]


def test_get_registered_players_with_non_existing_activity_id() -> None:
    with requests_mock.Mocker() as m:
        m.get(
            "https://api.holdsport.dk/v1/teams/1/activities?date=2024-01-01",
            text="[]",
        )
        activity_id = _get_activity_id(1, "2024-01-01", ("username", "password"), "Falcon practice")
        assert activity_id is None
        registered_players = get_registered_players(1, "2024-01-01", ("username", "password"), "Falcon practice")
        assert registered_players == []


def test_get_registered_players_with_not_ok_status_code() -> None:
    with requests_mock.Mocker() as m:
        m.get(
            "https://api.holdsport.dk/v1/activities/1/activities_users",
            status_code=500,
        )
        m.get(
            "https://api.holdsport.dk/v1/teams/1/activities?date=2024-01-01",
            text='[{"name": "Falcon practice", "starttime": "2024-01-01T00:00:00+00:00", "id": 1}]',
        )
        registered_players = get_registered_players(1, "2024-01-01", ("username", "password"), "Falcon practice")
        assert registered_players == []


def test_get_activity_id_with_not_ok_status_code() -> None:
    with requests_mock.Mocker() as m:
        m.get(
            "https://api.holdsport.dk/v1/teams/1/activities?date=2024-01-01",
            status_code=500,
        )
        activity_id = _get_activity_id(1, "2024-01-01", ("username", "password"), "Falcon practice")
        assert activity_id is None


def test_get_list_of_teams_with_ok_status_code() -> None:
    with requests_mock.Mocker() as m:
        m.get(
            "https://api.holdsport.dk/v1/teams",
            text='[{"id": 123456, "name": "Falcon 1"}, {"id": 234567, "name": "Falcon 2"}]',
        )
        teams = _get_list_of_teams(("username", "password"))
        expected_teams: list[dict[str, str]] = [
            {"id": "123456", "name": "Falcon 1"},
            {"id": "234567", "name": "Falcon 2"},
        ]
        assert sorted(teams, key=lambda x: int(x["id"])) == sorted(expected_teams, key=lambda x: int(x["id"]))


def test_get_list_of_teams_with_not_ok_status_code() -> None:
    with requests_mock.Mocker() as m:
        m.get(
            "https://api.holdsport.dk/v1/teams",
            status_code=500,
        )
        teams = _get_list_of_teams(("username", "password"))
        assert teams == []


def test_get_list_of_team_members_with_ok_status_code() -> None:
    with requests_mock.Mocker() as m:
        m.get(
            "https://api.holdsport.dk/v1/teams/1/members",
            text='[{"id": 1, "firstname": "John", "lastname": "Doe"}, \
                   {"id": 2, "firstname": "Jane", "lastname": "Doe"}, \
                   {"id": 3, "firstname": "Alice", "lastname": "Smith"}, \
                   {"id": 4, "firstname": "Bob", "lastname": "Smith"}]',
        )
        team_members = _get_list_of_team_members(1, ("username", "password"))
        assert team_members == ["Alice Smith", "Bob Smith", "Jane Doe", "John Doe"]


def test_get_list_of_team_members_with_not_ok_status_code() -> None:
    with requests_mock.Mocker() as m:
        m.get(
            "https://api.holdsport.dk/v1/teams/1/members",
            status_code=500,
        )
        team_members = _get_list_of_team_members(1, ("username", "password"))
        assert team_members == []
