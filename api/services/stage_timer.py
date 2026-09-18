"""Per-request stage timer (v3 latency decomposition).

Accumulates wall-clock seconds per named stage inside the current process
(thread-safe; the guide pipeline runs the goal-query retrieval in a worker
thread). The bench evaluator resets it before every step and stores the
snapshot next to the measured step latency, so a step's latency can be
reported as vision / embed / clip / rerank / retrieval / generate instead of
one number. Inclusive stages (localize, goal_retrieval, routed_retrieval)
contain exclusive ones (embed, vector_search, clip, rerank, …); the report
shows both and states which are which.
"""
from __future__ import annotations

import threading
import time
from contextlib import contextmanager
from functools import wraps
from typing import Dict

_LOCK = threading.Lock()
_ACC: Dict[str, list] = {}   # stage -> [seconds, count]


def record(stage: str, seconds: float) -> None:
    with _LOCK:
        cur = _ACC.setdefault(stage, [0.0, 0])
        cur[0] += float(seconds or 0.0)
        cur[1] += 1


@contextmanager
def timed(stage: str):
    t0 = time.perf_counter()
    try:
        yield
    finally:
        record(stage, time.perf_counter() - t0)


def timed_fn(stage: str):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            with timed(stage):
                return fn(*args, **kwargs)
        return wrapper
    return deco


def snapshot() -> Dict[str, Dict[str, float]]:
    with _LOCK:
        return {k: {"sec": round(v[0], 3), "n": v[1]} for k, v in _ACC.items()}


def reset() -> None:
    with _LOCK:
        _ACC.clear()
