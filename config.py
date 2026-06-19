# Model identifiers - update to current available versions as needed
CLAUDE_QUERY_MODEL = "claude-sonnet-4-6"
CLAUDE_AGGREGATION_MODEL = "claude-opus-4-7"
CHATGPT_MODEL = "gpt-4o"
GEMINI_MODEL = "gemini-2.5-flash"
GROK_MODEL = "grok-3"           # verify against https://docs.x.ai/docs/models

# Timing
CALL_TIMEOUT_SEC: int = 90      # per-model HTTP timeout
RETRY_DELAY_SEC: int = 2        # pause before single retry

# Token limits
MAX_TOKENS: int = 2048
AGGREGATION_MAX_TOKENS: int = 4096
