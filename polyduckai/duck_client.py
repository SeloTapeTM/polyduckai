import json
import logging
from enum import Enum

import aiohttp

logger = logging.getLogger(__name__)

STATUS_URL = "https://duckduckgo.com/duckchat/v1/status"
CHAT_URL = "https://duckduckgo.com/duckchat/v1/chat"

_BASE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Referer": "https://duckduckgo.com/",
    "Origin": "https://duckduckgo.com",
}


class Model(str, Enum):
    GPT4O_MINI = "gpt-4o-mini"
    CLAUDE_HAIKU = "claude-3-haiku-20240307"
    LLAMA = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
    MISTRAL = "mistralai/Mistral-Small-24B-Instruct-2501"
    O3_MINI = "o3-mini"


class DuckAISession:
    """One conversation session with duck.ai. Maintains message history and VQD token."""

    def __init__(self, model: Model = Model.GPT4O_MINI):
        self.model = model
        self._vqd_token: str | None = None
        self._messages: list[dict] = []
        self._session: aiohttp.ClientSession | None = None

    async def start(self) -> None:
        self._session = aiohttp.ClientSession(headers=_BASE_HEADERS)
        await self._refresh_vqd()

    async def close(self) -> None:
        if self._session:
            await self._session.close()
            self._session = None

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, *_):
        await self.close()

    async def _refresh_vqd(self) -> None:
        async with self._session.get(STATUS_URL, headers={"X-Vqd-Accept": "1"}) as resp:
            resp.raise_for_status()
            token = resp.headers.get("x-vqd-4")
            if not token:
                raise RuntimeError("duck.ai did not return a VQD token")
            self._vqd_token = token
            logger.debug("VQD token acquired")

    async def chat(self, message: str) -> str:
        if not self._session:
            raise RuntimeError("Session not started — call start() or use async with")

        self._messages.append({"role": "user", "content": message})

        async with self._session.post(
            CHAT_URL,
            headers={
                "Accept": "text/event-stream",
                "Content-Type": "application/json",
                "x-vqd-4": self._vqd_token,
            },
            json={"model": self.model, "messages": self._messages},
        ) as resp:
            resp.raise_for_status()
            new_vqd = resp.headers.get("x-vqd-4")
            if new_vqd:
                self._vqd_token = new_vqd
            reply = await _parse_sse(resp)

        self._messages.append({"role": "assistant", "content": reply})
        return reply

    def reset(self) -> None:
        self._messages.clear()


async def _parse_sse(resp: aiohttp.ClientResponse) -> str:
    parts: list[str] = []
    async for raw in resp.content:
        line = raw.decode("utf-8").strip()
        if not line.startswith("data: "):
            continue
        payload = line[6:]
        if payload == "[DONE]":
            break
        try:
            chunk = json.loads(payload)
            if "message" in chunk:
                parts.append(chunk["message"])
        except json.JSONDecodeError:
            pass
    return "".join(parts)
