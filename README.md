# Multi-AI Idea Integrator

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Models](https://img.shields.io/badge/Models-Claude%20%7C%20ChatGPT%20%7C%20Gemini%20%7C%20Grok-purple)
![Lint](https://github.com/areweloststars/multi-ai-cli/actions/workflows/lint.yml/badge.svg)

ChatGPT, Gemini, Grok, Claude 4개의 AI 모델에 같은 질문을 **동시에** 보내고, 각 모델의 답변을 나란히 비교한 뒤 ChatGPT가 최종 정리해주는 CLI 파이프라인입니다.

---

## Demo

```
============================================================
   Multi-AI Idea Integrator
============================================================

질문: 30대 남자 여름 데이트 패션 추천해줘

------------------------------------------------------------
Step 1/4  Initialising adapters ...
  Active: Claude, ChatGPT, Gemini, Grok

------------------------------------------------------------
Step 2/4  Querying 4 model(s) in parallel + Claude Code (local) ...
  [OK] Claude Code (local)
  [OK] ChatGPT
  [OK] Gemini

------------------------------------------------------------
Step 3/4  Synthesising responses ...
  [OK] Synthesised with ChatGPT

------------------------------------------------------------
Step 4/4  ChatGPT is polishing the output ...

============================================================
### Claude Code 추천

1. 네이비/화이트 린넨 셔츠 + 베이지 치노 팬츠
2. 신발: 흰 스니커즈 또는 로퍼
3. 색상 최대 2가지로 제한 — 과하지 않게

### ChatGPT 추천

1. 폴로 셔츠 / 린넨 셔츠 (네이비, 화이트, 라이트 블루)
2. 치노 팬츠 또는 쇼츠 (슬림 핏, 베이지/카키)
3. 로퍼 또는 스니커즈
4. 클래식 시계 + 선글라스

### Gemini 추천

1. 린넨·면·레이온 혼방 소재 (통기성 우선)
2. 장소별 분리: 낮엔 리넨 셔츠, 저녁엔 오픈 카라
3. 슬림 스트레이트 슬랙스 또는 세미 와이드 치노
4. 향수 + 통기성 이너웨어로 땀 관리
============================================================
```

---

## Pipeline

```
질문 입력 (context + request)
        |
        v
+--------------------------------------------------+
|  Step 2: Parallel Query                          |
|  Claude Code (local)  /  ChatGPT  /  Gemini      |
|  Claude API  /  Grok  (크레딧 있을 때 추가)      |
+--------------------+-----------------------------+
                     |  각 모델 독립 답변
                     v
+--------------------------------------------------+
|  Step 3: Synthesis                               |
|  Claude API 우선, 없으면 ChatGPT 자동 폴백       |
|  각 모델 답변을 번호 목록으로 나란히 정리         |
+--------------------+-----------------------------+
                     |
                     v
+--------------------------------------------------+
|  Step 4: Polish (ChatGPT)                        |
|  가독성 포맷 정리 — 내용 변경 없이               |
+--------------------+-----------------------------+
                     |
                     v
          최종 출력  +  raw JSON 로그 저장
```

---

## Features

- **병렬 실행** — `ThreadPoolExecutor`로 모든 모델 동시 호출
- **Graceful Degradation** — 일부 모델 실패해도 파이프라인 계속 진행
- **ChatGPT 자동 폴백** — Claude API 크레딧 없을 때 ChatGPT가 합성 대행
- **Claude Code 로컬 주입** — `--local-response`로 AI 에이전트 답변을 3번째 의견으로 추가
- **1회 자동 재시도** — 실패한 모델 호출 자동 재시도 (비용 제어)
- **모델별 HTTP 타임아웃** — `config.py`에서 조정 가능 (기본 90초)
- **Raw 응답 로깅** — 모든 모델의 원본 답변을 `logs/raw_*.json`에 저장
- **한글 완벽 지원** — Windows UTF-8 콘솔 자동 설정, 한글 출력 깨짐 없음
- **API 키 없어도 동작** — 보유한 키만으로 자동 구성, 없는 모델은 스킵
- **시크릿 미노출** — 모든 API 키는 `.env`에서만 로드

---

## Usage

```bash
# 대화형 실행
python main.py

# 질문만 바로 입력
python main.py -r "오늘 점심 뭐 먹을까?"

# 맥락 + 질문
python main.py -c "스타트업 초기, 팀 3명" -r "MVP 기술 스택 추천해줘"

# Claude Code 의견 포함한 3안 비교
python main.py -r "질문" --local-response "여기에 Claude Code 직접 답변"

# 상세 답변 끄기
python main.py -r "질문" --no-detail
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
# .env 파일을 열어 키 입력

# 4. Run
python main.py
```

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
├── orchestrator.py         # 병렬 dispatch, timeout & 1회 retry
├── aggregator.py           # Claude 우선 합성, ChatGPT 자동 폴백
├── presenter.py            # ChatGPT 가독성 polish
├── prompts.py              # 모든 프롬프트 템플릿
├── config.py               # 모델명, 타임아웃, 토큰 한도
├── main.py                 # CLI 진입점 (argparse)
└── logs/                   # 자동 생성: 세션 로그 + raw JSON
```

---

## Configuration

`config.py`에서 모델과 한도 변경:

```python
CLAUDE_QUERY_MODEL       = "claude-sonnet-4-6"
CLAUDE_AGGREGATION_MODEL = "claude-opus-4-7"
CHATGPT_MODEL            = "gpt-4o"
GEMINI_MODEL             = "gemini-2.5-flash"
GROK_MODEL               = "grok-3"

CALL_TIMEOUT_SEC = 90    # 모델별 HTTP 타임아웃
MAX_TOKENS       = 2048  # 모델별 응답 최대 토큰
```

---

## Required API Keys

| 환경 변수 | 발급처 | 용도 |
|-----------|--------|------|
| `ANTHROPIC_API_KEY` | [Anthropic Console](https://console.anthropic.com) | Claude (질의 + 합성) |
| `OPENAI_API_KEY` | [OpenAI Platform](https://platform.openai.com) | ChatGPT (질의 + 폴백 합성 + polish) |
| `GOOGLE_API_KEY` | [Google AI Studio](https://aistudio.google.com) | Gemini |
| `XAI_API_KEY` | [xAI Console](https://console.x.ai) | Grok |

4개 모두 선택 사항 — 보유한 키만으로 자동 구성됩니다.

---

## Tech Stack

| 분류 | 라이브러리 |
|------|-----------|
| Claude API | `anthropic` |
| ChatGPT / Grok API | `openai` |
| Gemini API | `google-genai` |
| 병렬 실행 | `concurrent.futures` |
| 환경 변수 | `python-dotenv` |
| CI (lint) | `ruff` + GitHub Actions |

---

## License

MIT
