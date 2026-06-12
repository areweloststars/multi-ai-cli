"""Synthesis step: Claude reads all model responses and integrates them."""
import logging

import anthropic

from config import AGGREGATION_MAX_TOKENS, CLAUDE_AGGREGATION_MODEL
from prompts import AGGREGATION_SYSTEM, AGGREGATION_USER_TEMPLATE

logger = logging.getLogger(__name__)


def _format_responses(responses: dict, failures: dict) -> str:
    parts: list[str] = []
    for name, text in responses.items():
        parts.append(f"### {name}\n{text}")
    if failures:
        fail_lines = "\n".join(f"- {k}: {v}" for k, v in failures.items())
        parts.append(f"### Failed models (excluded from synthesis)\n{fail_lines}")
    return "\n\n".join(parts)


def aggregate(
    api_key: str,
    context: str,
    request: str,
    responses: dict,
    failures: dict,
) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    user_msg = AGGREGATION_USER_TEMPLATE.format(
        context=context or "(none)",
        request=request,
        responses=_format_responses(responses, failures),
    )
    message = client.messages.create(
        model=CLAUDE_AGGREGATION_MODEL,
        max_tokens=AGGREGATION_MAX_TOKENS,
        system=AGGREGATION_SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    )
    return message.content[0].text
