#!/usr/bin/env python3
"""Multi-AI Idea Integrator - CLI entry point.

Usage:
  python main.py                          # interactive prompts
  python main.py -r "질문"               # request only
  python main.py -c "맥락" -r "질문"    # context + request
"""
import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Force UTF-8 on Windows console (fixes Korean garbling)
if sys.platform == "win32":
    import ctypes
    ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    ctypes.windll.kernel32.SetConsoleCP(65001)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
sys.stdin.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv

from adapters import ClaudeAdapter, ChatGPTAdapter, GeminiAdapter, GrokAdapter
from aggregator import aggregate
from orchestrator import gather_responses
from presenter import present
from prompts import build_agent_prompt

load_dotenv()

_SEP   = "-" * 60
_THICK = "=" * 60


# -- Setup ------------------------------------------------------------

def _setup_logging(logs_dir: Path) -> Path:
    logs_dir.mkdir(exist_ok=True)
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = logs_dir / f"session_{ts}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.FileHandler(path, encoding="utf-8")],
    )
    return path


def _build_adapters() -> dict:
    specs = [
        ("Claude",  "ANTHROPIC_API_KEY", ClaudeAdapter),
        ("ChatGPT", "OPENAI_API_KEY",    ChatGPTAdapter),
        ("Gemini",  "GOOGLE_API_KEY",    GeminiAdapter),
        ("Grok",    "XAI_API_KEY",       GrokAdapter),
    ]
    adapters: dict = {}
    skipped: list[str] = []

    for name, env_var, cls in specs:
        key = os.getenv(env_var)
        if not key:
            skipped.append(f"{name} (no {env_var})")
            continue
        try:
            adapters[name] = cls(key)
        except Exception as exc:
            skipped.append(f"{name} (init error: {exc})")

    if skipped:
        print(f"  Skipping: {', '.join(skipped)}")
    return adapters


def _safe_str(obj):
    if isinstance(obj, str):
        return obj.encode("utf-8", errors="replace").decode("utf-8")
    if isinstance(obj, dict):
        return {k: _safe_str(v) for k, v in obj.items()}
    return obj


def _save_raw(logs_dir: Path, context: str, request: str,
              responses: dict, failures: dict) -> Path:
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = logs_dir / f"raw_{ts}.json"
    payload = _safe_str({
        "timestamp": ts,
        "context":   context,
        "request":   request,
        "responses": responses,
        "failures":  failures,
    })
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


# -- Output helpers ---------------------------------------------------

def _print_footer(log_path: Path, raw_path: Path) -> None:
    print(f"\n{_THICK}")
    print(f"Session log    : {log_path}")
    print(f"Raw responses  : {raw_path}")


def _print_result(text: str, log_path: Path, raw_path: Path) -> None:
    print(f"\n{_THICK}")
    print(text)
    _print_footer(log_path, raw_path)


# -- Main pipeline ----------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-AI Idea Integrator")
    parser.add_argument("-c", "--context", default=None, help="Background / constraints")
    parser.add_argument("-r", "--request", default=None, help="What to ask all models")
    parser.add_argument("-d", "--detail", action="store_true", default=True, help="Request detailed responses (default: on)")
    args = parser.parse_args()

    logs_dir = Path("logs")
    log_path = _setup_logging(logs_dir)
    logger   = logging.getLogger("main")

    print(f"\n{_THICK}")
    print("   Multi-AI Idea Integrator")
    print(_THICK)

    # Get context and request — from args or interactive input
    context = (args.context or "").strip()

    if args.request is not None:
        request = args.request.strip()
        print(f"\n질문: {request}\n")
    else:
        request = input("\n질문을 입력하세요:\n> ").strip()
        print()

    if not request:
        print("No request entered. Exiting.")
        return

    prompt = build_agent_prompt(context, request, detail=args.detail)
    logger.info("Prompt built (%d chars)", len(prompt))

    # Step 1: initialise adapters
    print(_SEP)
    print("Step 1/4  Initialising adapters ...")
    adapters = _build_adapters()
    if not adapters:
        print("No adapters available. Check .env and retry.")
        return
    print(f"  Active: {', '.join(adapters)}")

    # Step 2: parallel query
    print(f"\n{_SEP}")
    print(f"Step 2/4  Querying {len(adapters)} model(s) in parallel ...")
    responses, failures = gather_responses(adapters, prompt)

    for name in adapters:
        if name in responses:
            print(f"  [OK] {name}")
        else:
            short_err = failures.get(name, "unknown error")[:80]
            print(f"  [!!] {name} - {short_err}")

    raw_path = _save_raw(logs_dir, context, request, responses, failures)
    logger.info("Raw responses saved -> %s", raw_path)

    if not responses:
        print("\nAll models failed. Cannot continue.")
        _print_footer(log_path, raw_path)
        return

    # Step 3: aggregate (Claude preferred, ChatGPT fallback)
    print(f"\n{_SEP}")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openai_key    = os.getenv("OPENAI_API_KEY")
    if not anthropic_key and not openai_key:
        print("Step 3/4  [SKIP] No aggregation key - showing raw responses.\n")
        for name, text in responses.items():
            print(f"-- {name} --\n{text}\n")
        _print_footer(log_path, raw_path)
        return

    print("Step 3/4  Synthesising responses ...")
    try:
        synthesis, agg_model = aggregate(
            context, request, responses, failures,
            anthropic_key=anthropic_key or "",
            openai_key=openai_key or "",
        )
        logger.info("Synthesis complete via %s (%d chars)", agg_model, len(synthesis))
        print(f"  [OK] Synthesised with {agg_model}")
    except Exception as exc:
        logger.error("Aggregation error: %s", exc, exc_info=True)
        print(f"  [!] Aggregation failed ({exc}) - showing raw responses.\n")
        for name, text in responses.items():
            print(f"-- {name} --\n{text}\n")
        _print_footer(log_path, raw_path)
        return

    # Step 4: present (ChatGPT)
    print(f"\n{_SEP}")
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("Step 4/4  [SKIP] No OPENAI_API_KEY - showing synthesis directly.\n")
        _print_result(synthesis, log_path, raw_path)
        return

    print("Step 4/4  ChatGPT is polishing the output ...")
    try:
        final = present(openai_key, synthesis)
        logger.info("Final output ready (%d chars)", len(final))
    except Exception as exc:
        logger.error("Presentation error: %s", exc, exc_info=True)
        print(f"  [!] Presentation failed ({exc}) - showing synthesis.\n")
        final = synthesis

    _print_result(final, log_path, raw_path)


if __name__ == "__main__":
    main()
