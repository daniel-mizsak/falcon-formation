"""
Tests for the Telegram API.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import pytest
from aioresponses import aioresponses

from falcon_formation.telegram_api import TelegramAPI


@pytest.fixture
def telegram_api() -> TelegramAPI:
    return TelegramAPI("token")


@pytest.mark.asyncio
async def test_get_chat_id(telegram_api: TelegramAPI) -> None:
    with aioresponses() as m:
        m.get(
            "https://api.telegram.org/bottoken/getUpdates",
            payload={
                "ok": True,
                "result": [
                    {
                        "update_id": 123456789,
                        "message": {
                            "message_id": 1,
                            "from": {
                                "id": 1111111111,
                                "is_bot": False,
                                "first_name": "Rihouse",
                                "last_name": "Peace",
                                "username": "housy",
                                "language_code": "en",
                            },
                            "chat": {
                                "id": -1122334455,
                                "title": "Team Name",
                                "type": "group",
                                "all_members_are_administrators": True,
                            },
                            "date": 1800000000,
                            "text": "Test",
                        },
                    },
                ],
            },
        )
        chat_id = await telegram_api.get_chat_id(group_name="Team Name")
        assert chat_id == -1122334455


@pytest.mark.asyncio
async def test_get_chat_id_with_non_existing_group_name(telegram_api: TelegramAPI) -> None:
    with aioresponses() as m:
        m.get(
            "https://api.telegram.org/bottoken/getUpdates",
            payload={
                "ok": True,
                "result": [
                    {
                        "update_id": 123456789,
                        "message": {
                            "message_id": 1,
                            "from": {
                                "id": 1111111111,
                                "is_bot": False,
                                "first_name": "Rihouse",
                                "last_name": "Peace",
                                "username": "housy",
                                "language_code": "en",
                            },
                            "chat": {
                                "id": -1122334455,
                                "title": "Team Name",
                                "type": "group",
                                "all_members_are_administrators": True,
                            },
                            "date": 1800000000,
                            "text": "Test",
                        },
                    },
                ],
            },
        )
        chat_id = await telegram_api.get_chat_id(group_name="No Team Name")
        assert chat_id is None


@pytest.mark.asyncio
async def test_get_chat_id_with_not_ok_status_code(telegram_api: TelegramAPI) -> None:
    with aioresponses() as m:
        m.get(
            "https://api.telegram.org/bottoken/getUpdates",
            status=500,
        )
        chat_id = await telegram_api.get_chat_id(group_name="")
        assert chat_id is None
