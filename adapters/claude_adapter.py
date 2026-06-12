import anthropic

from config import CALL_TIMEOUT_SEC, CLAUDE_QUERY_MODEL, MAX_TOKENS
from .base import BaseAdapter


class ClaudeAdapter(BaseAdapter):
    name = "Claude"

    def __init__(self, api_key: str) -> None:
        self._client = anthropic.Anthropic(
            api_key=api_key,
            timeout=float(CALL_TIMEOUT_SEC),
        )

    def ask(self, prompt: str) -> str:
        message = self._client.messages.create(
            model=CLAUDE_QUERY_MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
