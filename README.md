# Multi-AI Idea Integrator

A CLI tool that queries **Claude, ChatGPT, Gemini, and Grok in parallel**, then uses Claude to synthesize the responses and ChatGPT to polish the final output — all in one pipeline.

## Pipeline

```
User input (context + request)
        |
        v
  ┌─────────────────────────────────────────┐
  │  Parallel Query  (Step 2)               │
  │  Claude · ChatGPT · Gemini · Grok       │
  └──────────┬──────────────────────────────┘
             │  independent responses
             v
  ┌──────────────────────────────────────┐
  │  Synthesis  (Step 3)                 │
  │  Claude merges, preserves diversity  │
  └──────────┬───────────────────────────┘
             │
             v
  ┌──────────────────────────────────────┐
  │  Polish  (Step 4)                    │
  │  ChatGPT reformats for readability   │
  └──────────┬───────────────────────────┘
             │
             v
        Final output  +  raw JSON log
```

## Features

- **Parallel execution** — all 4 models called simultaneously via `ThreadPoolExecutor`
- **Graceful degradation** — one model failing does not stop the pipeline; failures are clearly reported
- **Single retry** — each failed call is retried once (cost-controlled)
- **Per-model HTTP timeout** — configurable in `config.py` (default 90s)
- **Raw response logging** — every model's original answer saved to `logs/raw_*.json`
- **Diversity-preserving synthesis** — Claude merges duplicates but keeps conflicting viewpoints intact
- **No hardcoded secrets** — all API keys loaded from `.env`

## Project Structure

```
multi-ai-cli/
├── adapters/
│   ├── base.py             # Abstract adapter interface
│   ├── claude_adapter.py   # Anthropic SDK
│   ├── chatgpt_adapter.py  # OpenAI SDK
│   ├── gemini_adapter.py   # Google GenAI SDK
│   └── grok_adapter.py     # OpenAI SDK + xAI base URL
├── orchestrator.py         # Parallel dispatch with timeout & retry
├── aggregator.py           # Claude synthesis call
├── presenter.py            # ChatGPT polish call
├── prompts.py              # All prompt templates
├── config.py               # Model names, timeouts, token limits
├── main.py                 # CLI entry point
└── logs/                   # Auto-created: session logs + raw JSON
```

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure API keys
cp .env.example .env
# Edit .env and fill in your keys

# 3. Run
python main.py
```

## Configuration

Edit `config.py` to change models or limits:

```python
CLAUDE_QUERY_MODEL       = "claude-sonnet-4-6"
CLAUDE_AGGREGATION_MODEL = "claude-opus-4-7"
CHATGPT_MODEL            = "gpt-4o"
GEMINI_MODEL             = "gemini-2.0-flash"
GROK_MODEL               = "grok-3"

CALL_TIMEOUT_SEC = 90   # per-model HTTP timeout
MAX_TOKENS       = 2048
```

## Required API Keys

| Key | Provider | Purpose |
|-----|----------|---------|
| `ANTHROPIC_API_KEY` | [Anthropic](https://console.anthropic.com) | Claude (query + synthesis) |
| `OPENAI_API_KEY` | [OpenAI](https://platform.openai.com) | ChatGPT (query + polish) |
| `GOOGLE_API_KEY` | [Google AI Studio](https://aistudio.google.com) | Gemini |
| `XAI_API_KEY` | [xAI](https://console.x.ai) | Grok |

All 4 keys are optional — missing models are skipped and clearly flagged.

## Tech Stack

- **Python 3.10+**
- `anthropic` — Claude API
- `openai` — ChatGPT & Grok API
- `google-genai` — Gemini API
- `python-dotenv` — environment config
- `concurrent.futures` — parallel model calls
