"""Prompt templates for all pipeline stages."""


def build_agent_prompt(context: str, request: str, detail: bool = False) -> str:
    """Build the shared prompt sent to all 4 models."""
    parts: list[str] = []
    if context.strip():
        parts.append(f"Context:\n{context.strip()}\n")
    parts.append(f"Request:\n{request.strip()}")
    if detail:
        parts.append(
            "\nPlease give a thorough, detailed response with:\n"
            "- Specific examples and concrete recommendations\n"
            "- Step-by-step guidance where applicable\n"
            "- Pros/cons or comparisons where relevant\n"
            "- Practical tips and things to watch out for\n"
            "Respond in the same language as the request."
        )
    return "\n".join(parts)


AGGREGATION_SYSTEM = (
    "You are a meticulous synthesizer of AI-generated ideas. "
    "You receive several independent responses to the same question.\n\n"
    "Your synthesis rules:\n"
    "1. Merge genuinely duplicate points (same idea stated identically or near-identically).\n"
    "2. Preserve diverse and contrasting viewpoints - do NOT force a single conclusion.\n"
    "3. Highlight unique insights raised by only one model.\n"
    "4. Retain all relevant nuances and caveats.\n"
    "5. Use clear headings or sections when the content benefits from structure.\n"
    "6. Be comprehensive but not repetitive.\n"
    "7. IMPORTANT: Always respond in the same language as the user's original request."
)

AGGREGATION_USER_TEMPLATE = """\
Original context:
{context}

User's request:
{request}

=== AI Model Responses ===
{responses}

Synthesize the above into a unified response. Merge duplicates, preserve diversity, highlight unique insights."""


PRESENTATION_SYSTEM = (
    "You are a professional editor. Your sole task is to reformat text for maximum readability.\n\n"
    "Strict constraints:\n"
    "- Do NOT change, add, or remove any content, ideas, or conclusions.\n"
    "- Do NOT take sides or introduce opinions not already present.\n"
    "- Improve formatting: headings, bullet points, paragraph breaks, smooth transitions.\n"
    "- Write in a warm, clear, natural tone.\n"
    "- The reader should find the result pleasant and easy to follow.\n"
    "- IMPORTANT: Always write in the same language as the input text. Do NOT translate."
)

PRESENTATION_USER_TEMPLATE = """\
Please reformat the following synthesis for readability. Do not alter the content.

{synthesis}"""
