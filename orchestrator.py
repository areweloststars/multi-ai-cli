"""Parallel model orchestration with timeout and single retry per model."""
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from concurrent.futures import TimeoutError as FutureTimeoutError
from typing import Dict, Optional, Tuple

from adapters.base import BaseAdapter
from config import CALL_TIMEOUT_SEC, RETRY_DELAY_SEC

logger = logging.getLogger(__name__)

# Outer wall-clock limit covers the HTTP timeout + one retry + buffer
_OUTER_TIMEOUT = CALL_TIMEOUT_SEC + RETRY_DELAY_SEC + 10


def _call_with_retry(adapter: BaseAdapter, prompt: str) -> str:
    last_exc: Optional[Exception] = None
    for attempt in range(2):           # original attempt + 1 retry
        try:
            return adapter.ask(prompt)
        except Exception as exc:
            last_exc = exc
            logger.warning("[%s] attempt %d failed: %s", adapter.name, attempt + 1, exc)
            if attempt == 0:
                time.sleep(RETRY_DELAY_SEC)
    raise last_exc  # type: ignore[misc]


def gather_responses(
    adapters: Dict[str, BaseAdapter],
    prompt: str,
) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Run all adapters in parallel. Returns (successes, failures)."""
    successes: Dict[str, str] = {}
    failures: Dict[str, str] = {}

    with ThreadPoolExecutor(max_workers=len(adapters)) as pool:
        future_to_name: Dict = {
            pool.submit(_call_with_retry, adapter, prompt): name
            for name, adapter in adapters.items()
        }

        try:
            for future in as_completed(future_to_name, timeout=_OUTER_TIMEOUT):
                name = future_to_name[future]
                try:
                    successes[name] = future.result()
                    logger.info("[%s] OK - %d chars", name, len(successes[name]))
                except Exception as exc:
                    failures[name] = str(exc)
                    logger.error("[%s] failed: %s", name, exc)
        except FutureTimeoutError:
            for future, name in future_to_name.items():
                if name not in successes and name not in failures:
                    future.cancel()
                    failures[name] = f"timed out after {_OUTER_TIMEOUT}s"
                    logger.error("[%s] timed out", name)

    return successes, failures
