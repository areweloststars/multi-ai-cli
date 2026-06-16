# Multi-AI Idea Integrator

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Models](https://img.shields.io/badge/Models-Claude%20%7C%20ChatGPT%20%7C%20Gemini%20%7C%20Grok-purple)

A CLI tool that queries **Claude, ChatGPT, Gemini, and Grok in parallel**, then uses Claude to synthesize the responses and ChatGPT to polish the final output — all in one pipeline.

---

## Demo

```
============================================================
   Multi-AI Idea Integrator
============================================================

Context (background / constraints) - Enter to skip:
> 스타트업 초기 단계, 팀 3명, 예산 부족

Request:
> MVP 기술 스택 선택 기준을 알려줘

------------------------------------------------------------
Step 1/4  Initialising adapters ...
  Active: Claude, ChatGPT, Gemini, Grok

------------------------------------------------------------
Step 2/4  Querying 4 model(s) in parallel ...
  [OK] Claude
  [OK] ChatGPT
  [OK] Gemini
  [OK] Grok

------------------------------------------------------------
Step 3/4  Claude is synthesising ...

------------------------------------------------------------
Step 4/4  ChatGPT is polishing the output ...

============================================================
## MVP 기술 스택 선택 기준

### 핵심 원칙
- **검증 속도 우선**: 익숙한 기술로 빠르게 시장 반응 확인
- **팀 역량 중심**: 학습 비용보다 실행 속도가 중요한 초기 단계
- **확장성은 나중에**: 지금은 작동하는 것이 완벽한 것보다 낫다

### 모델별 주요 인사이트
- **Claude**: 기술 선택보다 문제 정의가 먼저. 스택은 나중에 바꿀 수 있다
- **ChatGPT**: Next.js + Supabase 조합이 풀스택 소팀에게 가장 빠른 선택
- **Gemini**: Firebase/GCP 무료 티어를 적극 활용해 초기 비용 최소화
- **Grok**: 오픈소스 생태계가 풍부한 스택 선택으로 채용 난이도 낮추기

### 공통 권장사항
1. 팀이 이미 잘 아는 언어/프레임워크 선택
2. 관리형 서비스(DB, 인증, 스토리지) 활용으로 운영 부담 최소화
3. 3개월 후 리팩토링을 전제로 지금 당장 동작하는 것에 집중
============================================================

Session log    : logs/session_20260616_142301.log
Raw responses  : logs/raw_20260616_142301.json
```

---

## Pipeline

```
User input (context + request)
        |
        v
+------------------------------------------+
|  Step 2: Parallel Query                  |
|  Claude  /  ChatGPT  /  Gemini  /  Grok  |
+------------------+-----------------------+
                   |  4 independent answers
                   v
+------------------------------------------+
|  Step 3: Synthesis (Claude)              |
|  Merges duplicates, preserves diversity  |
+------------------+-----------------------+
                   |
                   v
+------------------------------------------+
|  Step 4: Polish (ChatGPT)                |
|  Reformats for readability               |
+------------------+-----------------------+
                   |
                   v
          Final output  +  raw JSON log
```

---

## Features

- **Parallel execution** — all 4 models called simultaneously via `ThreadPoolExecutor`
- **Graceful degradation** — one model failing does not stop the pipeline; failures are clearly reported
- **Single retry** — each failed call is retried once (cost-controlled)
- **Per-model HTTP timeout** — configurable in `config.py` (default 90s)
- **Raw response logging** — every model's original answer saved to `logs/raw_*.json`
- **Diversity-preserving synthesis** — Claude merges duplicates but keeps conflicting viewpoints intact
- **No hardcoded secrets** — all API keys loaded from `.env`

---

## Project Structure

```
multi-ai-cli/
├── adapters/
│   ├── base.py             # Abstract adapter interface (ask -> str)
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

---

## Setup

```bash
# 1. Clone
git clone https://github.com/areweloststars/multi-ai-cli.git
cd multi-ai-cli

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API keys
cp .env.example .env
# Edit .env and fill in your keys

# 4. Run
python main.py
```

---

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

---

## Required API Keys

| Key | Provider | Purpose |
|-----|----------|---------|
| `ANTHROPIC_API_KEY` | [Anthropic Console](https://console.anthropic.com) | Claude (query + synthesis) |
| `OPENAI_API_KEY` | [OpenAI Platform](https://platform.openai.com) | ChatGPT (query + polish) |
| `GOOGLE_API_KEY` | [Google AI Studio](https://aistudio.google.com) | Gemini |
| `XAI_API_KEY` | [xAI Console](https://console.x.ai) | Grok |

All 4 keys are optional — missing models are skipped and clearly flagged.

---

## Tech Stack

| Category | Library |
|----------|---------|
| Claude API | `anthropic` |
| ChatGPT / Grok API | `openai` |
| Gemini API | `google-genai` |
| Parallel execution | `concurrent.futures` |
| Environment config | `python-dotenv` |

---

## License

MIT
