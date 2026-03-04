from __future__ import annotations

import asyncio
import hashlib
import logging

from telegram.error import TelegramError
from telegram.ext import Application

from src.db import Repository, Subscription
from src.models import QueryResult, VehicleType, Violation, now_utc
from src.provider.base import ViolationProvider

logger = logging.getLogger(__name__)


def build_fingerprint(violations: list[Violation]) -> str:
    if not violations:
        return "EMPTY"

    ordered = sorted(
        violations,
        key=lambda item: (
            item.violation_id,
            item.occurred_at,
            item.location,
            item.behavior,
            item.fine,
        ),
    )
    raw = "|".join(
        f"{item.violation_id}:{item.occurred_at}:{item.location}:{item.behavior}:{item.fine}"
        for item in ordered
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def format_vehicle_type(vehicle_type: VehicleType) -> str:
    return "O to" if vehicle_type == VehicleType.CAR else "Xe may"


def format_query_result(result: QueryResult) -> str:
    lines = [
        f"Bien so: {result.plate}",
        f"Loai xe: {format_vehicle_type(result.vehicle_type)}",
        f"Thoi diem kiem tra (UTC): {result.checked_at.isoformat(timespec='seconds')}",
    ]
    if not result.violations:
        lines.append("Trang thai: Chua ghi nhan vi pham.")
        return "\n".join(lines)

    lines.append(f"Trang thai: Co {len(result.violations)} vi pham.")
    for idx, item in enumerate(result.violations, start=1):
        lines.extend(
            [
                f"{idx}. [{item.violation_id}] {item.behavior}",
                f"   - Thoi gian: {item.occurred_at}",
                f"   - Vi tri: {item.location}",
                f"   - Muc phat: {item.fine}",
                f"   - Nguon: {item.source}",
            ]
        )
    return "\n".join(lines)


async def check_single(
    provider: ViolationProvider, plate: str, vehicle_type: VehicleType
) -> QueryResult:
    violations = await provider.check_violations(plate=plate, vehicle_type=vehicle_type)
    return QueryResult(
        plate=plate,
        vehicle_type=vehicle_type,
        violations=violations,
        checked_at=now_utc(),
    )


async def run_monitor_cycle(application: Application) -> None:
    repo: Repository = application.bot_data["repo"]
    provider: ViolationProvider = application.bot_data["provider"]
    timeout_seconds = int(application.bot_data.get("request_timeout_seconds", 20))
    monitor_lock: asyncio.Lock = application.bot_data.setdefault(
        "monitor_lock", asyncio.Lock()
    )

    if monitor_lock.locked():
        logger.warning("Bo qua monitor cycle vi lan truoc van dang chay.")
        return

    async with monitor_lock:
        subscriptions = repo.list_all_subscriptions()
        if not subscriptions:
            return

        for item in subscriptions:
            await _check_subscription(
                application=application,
                repo=repo,
                provider=provider,
                item=item,
                timeout_seconds=timeout_seconds,
            )


async def _check_subscription(
    application: Application,
    repo: Repository,
    provider: ViolationProvider,
    item: Subscription,
    timeout_seconds: int,
) -> None:
    try:
        result = await asyncio.wait_for(
            check_single(provider, item.plate, item.vehicle_type),
            timeout=max(5, timeout_seconds),
        )
        fingerprint = build_fingerprint(result.violations)

        if item.last_fingerprint and item.last_fingerprint != fingerprint:
            text = "Canh bao: Co thay doi thong tin phat nguoi.\n\n" + format_query_result(
                result
            )
            await asyncio.wait_for(
                application.bot.send_message(chat_id=item.chat_id, text=text),
                timeout=max(10, timeout_seconds),
            )
        repo.update_fingerprint(item.row_id, fingerprint)
    except asyncio.TimeoutError:
        logger.warning(
            "Monitor timeout for %s/%s (chat_id=%s).",
            item.plate,
            item.vehicle_type.value,
            item.chat_id,
        )
    except TelegramError as exc:
        logger.warning("Telegram send failed for chat_id=%s: %s", item.chat_id, exc)
    except Exception as exc:  # pragma: no cover - runtime guard
        logger.exception("Monitor failed for %s/%s: %s", item.plate, item.vehicle_type, exc)
