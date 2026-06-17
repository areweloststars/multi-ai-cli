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
    "You are an assistant that summarizes each AI model's response as a concise numbered list.\n\n"
    "Output format — repeat this block for every model that responded:\n\n"
    "[Model Name] 추천:\n"
    "  1. ...\n"
    "  2. ...\n"
    "  3. ...\n\n"
    "Rules:\n"
    "1. Extract the 3-6 most important recommendations or points per model.\n"
    "2. Keep each item to one short line — include a key detail or tip in parentheses if useful.\n"
    "3. Do NOT merge or cross-reference models — each block stands alone.\n"
    "4. Preserve unique insights that only one model raised.\n"
    "5. IMPORTANT: Always respond in the same language as the user's original request."
)

AGGREGATION_USER_TEMPLATE = """\
Context:
{context}

User's request:
{request}

=== AI Model Responses ===
{responses}

Summarize each model's response as a separate numbered list using the format above."""


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
