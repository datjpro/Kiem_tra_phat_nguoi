from __future__ import annotations

from typing import TYPE_CHECKING

from src.provider.base import ViolationProvider

if TYPE_CHECKING:
    from src.config import Settings


def build_provider(settings: Settings) -> ViolationProvider:
    if settings.provider_mode == "mock":
        from src.provider.mock import MockViolationProvider

        return MockViolationProvider()

    if not settings.http_provider_url:
        raise ValueError("HTTP_PROVIDER_URL is required when PROVIDER_MODE=http.")

    from src.provider.http_provider import HttpViolationProvider

    return HttpViolationProvider(
        base_url=settings.http_provider_url,
        token=settings.http_provider_token,
        timeout_seconds=settings.request_timeout_seconds,
    )
