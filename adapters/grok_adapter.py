from openai import OpenAI

from config import CALL_TIMEOUT_SEC, GROK_MODEL, MAX_TOKENS
from .base import BaseAdapter


class GrokAdapter(BaseAdapter):
    name = "Grok"

    def __init__(self, api_key: str) -> None:
        self._client = OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1",
            timeout=float(CALL_TIMEOUT_SEC),
        )

    def ask(self, prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=GROK_MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""
