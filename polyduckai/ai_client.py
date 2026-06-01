import logging
import os
from enum import Enum

import aiohttp

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Sent so OpenRouter can attribute traffic — optional but recommended.
_APP_REFERER = "https://github.com/SeloTapeTM/polyduckai"
_APP_TITLE = "Poly Telegram Bot"


class Model(str, Enum):
    """Free models available on OpenRouter.

    Model IDs occasionally change. If one stops working, check the current
    free catalogue at https://openrouter.ai/models?max_price=0 and update here.
    """

    GEMINI_FLASH = "google/gemini-2.0-flash-exp:free"
    DEEPSEEK = "deepseek/deepseek-chat-v3-0324:free"
    LLAMA = "meta-llama/llama-3.3-70b-instruct:free"
    QWEN = "qwen/qwen-2.5-72b-instruct:free"
    MISTRAL = "mistralai/mistral-small-3.1-24b-instruct:free"


class ChatSession:
    """One conversation session backed by OpenRouter. Keeps message history."""

    def __init__(self, api_key: str | None = None, model: Model = Model.GEMINI_FLASH):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not set")
        self.model = model
        self._messages: list[dict] = []
        self._session: aiohttp.ClientSession | None = None

    async def start(self) -> None:
        self._session = aiohttp.ClientSession()

    async def close(self) -> None:
        if self._session:
            await self._session.close()
            self._session = None

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, *_):
        await self.close()

    async def chat(self, message: str) -> str:
        if not self._session:
            raise RuntimeError("Session not started — call start() or use async with")

        self._messages.append({"role": "user", "content": message})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": _APP_REFERER,
            "X-Title": _APP_TITLE,
        }
        payload = {"model": self.model.value, "messages": self._messages}

        async with self._session.post(
            OPENROUTER_URL, headers=headers, json=payload
        ) as resp:
            data = await resp.json()
            if resp.status != 200:
                # Roll back the unanswered user turn so history stays consistent.
                self._messages.pop()
                err = data.get("error", {}).get("message", str(data))
                raise RuntimeError(f"OpenRouter error ({resp.status}): {err}")
            reply = data["choices"][0]["message"]["content"]

        self._messages.append({"role": "assistant", "content": reply})
        return reply

    def reset(self) -> None:
        self._messages.clear()
