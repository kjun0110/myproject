# 동시성 1개 제한(세마포어)입니다.

import asyncio

# 절대 임포트 시도, 실패하면 상대 임포트 사용
try:
    from core.config import MAX_CONCURRENCY
except ImportError:
    from .config import MAX_CONCURRENCY

_semaphore = asyncio.Semaphore(MAX_CONCURRENCY)


def get_semaphore() -> asyncio.Semaphore:
    return _semaphore
