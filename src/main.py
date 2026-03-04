from __future__ import annotations

import asyncio
import logging
import sys

from telegram import BotCommand, Update
from telegram.error import TelegramError
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.request import HTTPXRequest

from src.bot.handlers import (
    check_command,
    help_command,
    list_command,
    start_command,
    track_command,
    untrack_command,
)
from src.config import load_settings
from src.db import Repository
from src.provider import build_provider
from src.services.monitor import run_monitor_cycle

BOT_COMMANDS = [
    BotCommand("start", "Bat dau va xem huong dan"),
    BotCommand("help", "Xem danh sach lenh"),
    BotCommand("check", "Kiem tra phat nguoi ngay"),
    BotCommand("track", "Bat theo doi bien so"),
    BotCommand("untrack", "Tat theo doi bien so"),
    BotCommand("list", "Xem bien so dang theo doi"),
]


async def monitor_job(context) -> None:
    await run_monitor_cycle(context.application)


async def register_bot_commands(application: Application) -> None:
    logger = logging.getLogger(__name__)
    try:
        await application.bot.set_my_commands(BOT_COMMANDS)
    except TelegramError:
        logger.exception("Khong the dang ky command menu voi Telegram.")
        return
    logger.info("Da dang ky %d command voi Telegram.", len(BOT_COMMANDS))


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger = logging.getLogger(__name__)
    logger.exception("Unhandled error while processing update.", exc_info=context.error)

    if isinstance(update, Update) and update.effective_message is not None:
        try:
            await update.effective_message.reply_text(
                "Bot dang gap loi tam thoi. Ban thu lai sau it phut."
            )
        except TelegramError:
            logger.warning("Khong gui duoc thong bao loi toi nguoi dung.", exc_info=True)


async def close_provider(application: Application) -> None:
    logger = logging.getLogger(__name__)
    provider = application.bot_data.get("provider")
    aclose = getattr(provider, "aclose", None)
    if callable(aclose):
        try:
            await aclose()
        except Exception:  # pragma: no cover - runtime guard.
            logger.exception("Khong dong duoc ket noi provider.")


def main() -> None:
    settings = load_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level, logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    logger = logging.getLogger(__name__)
    if sys.version_info >= (3, 14):
        logger.warning(
            "Dang chay voi Python %s. python-telegram-bot 21.x chi khai bao den Python 3.13.",
            sys.version.split()[0],
        )

    repo = Repository(settings.sqlite_path)
    provider = build_provider(settings)

    request_timeout = float(settings.request_timeout_seconds)
    message_request = HTTPXRequest(
        connect_timeout=10.0,
        read_timeout=request_timeout,
        write_timeout=10.0,
        pool_timeout=10.0,
    )
    updates_request = HTTPXRequest(
        connect_timeout=10.0,
        read_timeout=35.0,
        write_timeout=10.0,
        pool_timeout=10.0,
    )

    application = (
        Application.builder()
        .token(settings.telegram_bot_token)
        .request(message_request)
        .get_updates_request(updates_request)
        .post_init(register_bot_commands)
        .post_shutdown(close_provider)
        .build()
    )
    application.bot_data["repo"] = repo
    application.bot_data["provider"] = provider
    application.bot_data["request_timeout_seconds"] = settings.request_timeout_seconds

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("check", check_command))
    application.add_handler(CommandHandler("track", track_command))
    application.add_handler(CommandHandler("untrack", untrack_command))
    application.add_handler(CommandHandler("list", list_command))
    application.add_error_handler(on_error)

    if application.job_queue is None:
        raise RuntimeError(
            "JobQueue is not available. Ensure python-telegram-bot[job-queue] is installed."
        )
    application.job_queue.run_repeating(
        callback=monitor_job,
        interval=settings.poll_interval_seconds,
        first=20,
        name="violation-monitor",
    )

    # Python 3.14 no longer provides an implicit default event loop.
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        application.run_polling(
            drop_pending_updates=True,
            close_loop=False,
            bootstrap_retries=-1,
        )
    finally:
        loop.close()


if __name__ == "__main__":
    main()
