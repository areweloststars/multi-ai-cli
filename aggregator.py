"""Synthesis step: uses Claude if available and funded, falls back to ChatGPT."""
import logging

from config import AGGREGATION_MAX_TOKENS, CLAUDE_AGGREGATION_MODEL, CHATGPT_MODEL
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
    context: str,
    request: str,
    responses: dict,
    failures: dict,
    anthropic_key: str = "",
    openai_key: str = "",
) -> tuple[str, str]:
    """Returns (synthesized_text, model_used). Prefers Claude, falls back to ChatGPT."""
    user_msg = AGGREGATION_USER_TEMPLATE.format(
        context=context or "(none)",
        request=request,
        responses=_format_responses(responses, failures),
    )

    if anthropic_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=anthropic_key)
            msg = client.messages.create(
                model=CLAUDE_AGGREGATION_MODEL,
                max_tokens=AGGREGATION_MAX_TOKENS,
                system=AGGREGATION_SYSTEM,
                messages=[{"role": "user", "content": user_msg}],
            )
            logger.info("Aggregated with Claude")
            return msg.content[0].text, "Claude"
        except Exception as exc:
            logger.warning("Claude aggregation failed (%s), falling back to ChatGPT", exc)

    if openai_key:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        resp = client.chat.completions.create(
            model=CHATGPT_MODEL,
            max_tokens=AGGREGATION_MAX_TOKENS,
            messages=[
                {"role": "system", "content": AGGREGATION_SYSTEM},
                {"role": "user", "content": user_msg},
            ],
        )
        logger.info("Aggregated with ChatGPT (fallback)")
        return resp.choices[0].message.content or "", "ChatGPT"

    raise RuntimeError("No API key available for aggregation.")
