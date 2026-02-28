from __future__ import annotations

from src.config import Settings
from src.provider.base import ViolationProvider
from src.provider.http_provider import HttpViolationProvider
from src.provider.mock import MockViolationProvider


def build_provider(settings: Settings) -> ViolationProvider:
    if settings.provider_mode == "mock":
        return MockViolationProvider()

    if not settings.http_provider_url:
        raise ValueError("HTTP_PROVIDER_URL is required when PROVIDER_MODE=http.")

    return HttpViolationProvider(
        base_url=settings.http_provider_url,
        token=settings.http_provider_token,
        timeout_seconds=settings.request_timeout_seconds,
    )
