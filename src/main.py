from __future__ import annotations

import asyncio
import logging

from telegram import BotCommand
from telegram.error import TelegramError
from telegram.ext import Application, CommandHandler

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


def main() -> None:
    settings = load_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level, logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    repo = Repository(settings.sqlite_path)
    provider = build_provider(settings)

    application = (
        Application.builder()
        .token(settings.telegram_bot_token)
        .post_init(register_bot_commands)
        .build()
    )
    application.bot_data["repo"] = repo
    application.bot_data["provider"] = provider

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("check", check_command))
    application.add_handler(CommandHandler("track", track_command))
    application.add_handler(CommandHandler("untrack", untrack_command))
    application.add_handler(CommandHandler("list", list_command))

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
        application.run_polling(drop_pending_updates=True, close_loop=False)
    finally:
        loop.close()


if __name__ == "__main__":
    main()
