"""
Tests for the falcon_formation.holdsport_api module.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import requests_mock
from falcon_formation.holdsport_api import _get_activity_id, get_registered_players


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
            text='[{"name": "Motion A practice", "starttime": "2024-01-01T00:00:00+00:00", "id": 1}]',
        )
        registered_players = get_registered_players(1, "2024-01-01", ("username", "password"))
        assert registered_players == ["Alice Smith", "John Doe"]


def test_get_registered_players_with_non_existing_activity_id() -> None:
    with requests_mock.Mocker() as m:
        m.get(
            "https://api.holdsport.dk/v1/teams/1/activities?date=2024-01-01",
            text="[]",
        )
        activity_id = _get_activity_id(1, "2024-01-01", ("username", "password"))
        assert activity_id is None
        registered_players = get_registered_players(1, "2024-01-01", ("username", "password"))
        assert registered_players == []


def test_get_registered_players_with_not_ok_status_code() -> None:
    with requests_mock.Mocker() as m:
        m.get(
            "https://api.holdsport.dk/v1/activities/1/activities_users",
            status_code=500,
        )
        m.get(
            "https://api.holdsport.dk/v1/teams/1/activities?date=2024-01-01",
            text='[{"name": "Motion A practice", "starttime": "2024-01-01T00:00:00+00:00", "id": 1}]',
        )
        registered_players = get_registered_players(1, "2024-01-01", ("username", "password"))
        assert registered_players == []


def test_get_activity_id_with_not_ok_status_code() -> None:
    with requests_mock.Mocker() as m:
        m.get(
            "https://api.holdsport.dk/v1/teams/1/activities?date=2024-01-01",
            status_code=500,
        )
        activity_id = _get_activity_id(1, "2024-01-01", ("username", "password"))
        assert activity_id is None
