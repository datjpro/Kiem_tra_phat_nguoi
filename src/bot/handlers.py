from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from src.db import Repository
from src.models import VehicleType
from src.provider.base import ViolationProvider
from src.services.monitor import check_single, format_query_result
from src.services.plate import normalize_plate, parse_vehicle_type, validate_plate

HELP_TEXT = (
    "Lenh ho tro:\n"
    "/check <bien_so> <oto|xemay> - Kiem tra ngay\n"
    "/track <bien_so> <oto|xemay> - Bat theo doi dinh ky\n"
    "/untrack <bien_so> <oto|xemay> - Tat theo doi\n"
    "/list - Danh sach bien so dang theo doi\n"
)


def _parse_check_args(args: list[str]) -> tuple[str, VehicleType]:
    if len(args) < 2:
        raise ValueError("Cu phap: <bien_so> <oto|xemay>")
    plate = normalize_plate(args[0])
    validate_plate(plate)
    vehicle_type = parse_vehicle_type(args[1])
    return plate, vehicle_type


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Bot kiem tra phat nguoi cho xe may va o to.\n" + HELP_TEXT
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT)


async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    provider: ViolationProvider = context.application.bot_data["provider"]
    try:
        plate, vehicle_type = _parse_check_args(context.args)
    except ValueError as exc:
        await update.message.reply_text(str(exc))
        return

    await update.message.reply_text("Dang kiem tra, vui long cho...")
    result = await check_single(provider, plate, vehicle_type)
    await update.message.reply_text(format_query_result(result))


async def track_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    repo: Repository = context.application.bot_data["repo"]
    try:
        plate, vehicle_type = _parse_check_args(context.args)
    except ValueError as exc:
        await update.message.reply_text(str(exc))
        return

    created = repo.add_subscription(
        chat_id=update.effective_chat.id,
        plate=plate,
        vehicle_type=vehicle_type,
    )
    if not created:
        await update.message.reply_text("Bien so nay da ton tai trong danh sach theo doi.")
        return

    await update.message.reply_text(
        f"Da bat theo doi: {plate} ({vehicle_type.value}). "
        "Bot se thong bao khi co thay doi."
    )


async def untrack_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    repo: Repository = context.application.bot_data["repo"]
    try:
        plate, vehicle_type = _parse_check_args(context.args)
    except ValueError as exc:
        await update.message.reply_text(str(exc))
        return

    removed = repo.remove_subscription(
        chat_id=update.effective_chat.id,
        plate=plate,
        vehicle_type=vehicle_type,
    )
    if not removed:
        await update.message.reply_text("Khong tim thay bien so trong danh sach theo doi.")
        return
    await update.message.reply_text(f"Da tat theo doi: {plate} ({vehicle_type.value}).")


async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    repo: Repository = context.application.bot_data["repo"]
    records = repo.list_subscriptions(chat_id=update.effective_chat.id)
    if not records:
        await update.message.reply_text("Ban chua theo doi bien so nao.")
        return

    lines = ["Danh sach dang theo doi:"]
    for item in records:
        lines.append(f"- {item.plate} ({item.vehicle_type.value})")
    await update.message.reply_text("\n".join(lines))
