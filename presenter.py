"""Presentation step: ChatGPT reformats the synthesis for readability."""
import logging

from openai import OpenAI

from config import AGGREGATION_MAX_TOKENS, CHATGPT_MODEL
from prompts import PRESENTATION_SYSTEM, PRESENTATION_USER_TEMPLATE

logger = logging.getLogger(__name__)


def present(api_key: str, synthesis: str) -> str:
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=CHATGPT_MODEL,
        max_tokens=AGGREGATION_MAX_TOKENS,
        messages=[
            {"role": "system", "content": PRESENTATION_SYSTEM},
            {"role": "user", "content": PRESENTATION_USER_TEMPLATE.format(synthesis=synthesis)},
        ],
    )
    return response.choices[0].message.content or synthesis
