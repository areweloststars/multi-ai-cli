from google import genai

from config import GEMINI_MODEL
from .base import BaseAdapter


class GeminiAdapter(BaseAdapter):
    name = "Gemini"

    def __init__(self, api_key: str) -> None:
        self._client = genai.Client(api_key=api_key)

    def ask(self, prompt: str) -> str:
        response = self._client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        return response.text or ""
