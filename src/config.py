from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    provider_mode: str
    http_provider_url: str
    http_provider_token: str
    poll_interval_seconds: int
    request_timeout_seconds: int
    sqlite_path: str
    log_level: str


def load_settings() -> Settings:
    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise ValueError("Missing TELEGRAM_BOT_TOKEN in environment.")

    provider_mode = os.getenv("PROVIDER_MODE", "mock").strip().lower()
    if provider_mode not in {"mock", "http"}:
        raise ValueError("PROVIDER_MODE must be 'mock' or 'http'.")

    return Settings(
        telegram_bot_token=token,
        provider_mode=provider_mode,
        http_provider_url=os.getenv("HTTP_PROVIDER_URL", "").strip(),
        http_provider_token=os.getenv("HTTP_PROVIDER_TOKEN", "").strip(),
        poll_interval_seconds=int(os.getenv("POLL_INTERVAL_SECONDS", "600")),
        request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20")),
        sqlite_path=os.getenv("SQLITE_PATH", "data/bot.db").strip(),
        log_level=os.getenv("LOG_LEVEL", "INFO").strip().upper(),
    )
