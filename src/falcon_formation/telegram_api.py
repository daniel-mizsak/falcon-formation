"""
Class implementation for interacting with the Telegram API.

https://core.telegram.org/bots/api#setwebhook

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from __future__ import annotations

import aiohttp

from falcon_formation import STATUS_CODE_OK


class TelegramAPI:
    """Class for interacting with the Telegram API."""

    def __init__(self: TelegramAPI, token: str) -> None:
        """Initialization of the TelegramAPI object."""
        self.timeout = aiohttp.ClientTimeout(total=10)
        self.token = token
        self.headers = {"Accept": "application/json"}

    async def get_chat_id(self: TelegramAPI, group_name: str) -> int | None:
        """Return the chat id of the group with the given name.

        The API only works if the FalconFormation bot is a member of the group and there was a message sent in the
        group within the last 24 hours.

        Args:
            self (TelegramAPI): The TelegramAPI object.
            group_name (str): The name of the group.

        Returns:
            int | None: The chat id of the group or None if the group was not found.
        """
        url = f"https://api.telegram.org/bot{self.token}/getUpdates"
        async with (
            aiohttp.ClientSession(timeout=self.timeout) as session,
            session.get(url, headers=self.headers) as response,
        ):
            if response.status != STATUS_CODE_OK:
                return None
            response_dict = await response.json()

        for response_entry in response_dict["result"]:
            message = response_entry.get("message", {})
            chat = message.get("chat", {})
            if chat.get("title") == group_name and chat.get("type") in ["group", "supergroup"]:
                return int(chat["id"])
        return None
