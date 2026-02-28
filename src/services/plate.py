from __future__ import annotations

import re

from src.models import VehicleType

_TYPE_ALIASES = {
    "oto": VehicleType.CAR,
    "car": VehicleType.CAR,
    "auto": VehicleType.CAR,
    "o_to": VehicleType.CAR,
    "xeoto": VehicleType.CAR,
    "xemay": VehicleType.MOTORBIKE,
    "motorbike": VehicleType.MOTORBIKE,
    "bike": VehicleType.MOTORBIKE,
    "xe_may": VehicleType.MOTORBIKE,
}


def normalize_plate(raw_plate: str) -> str:
    cleaned = re.sub(r"[^A-Z0-9]", "", raw_plate.upper())
    if not cleaned:
        raise ValueError("Biển số không hợp lệ.")
    return cleaned


def validate_plate(normalized_plate: str) -> None:
    if len(normalized_plate) < 7 or len(normalized_plate) > 11:
        raise ValueError("Biển số phải có độ dài từ 7-11 ký tự.")
    if not normalized_plate[:2].isdigit():
        raise ValueError("Biển số phải bắt đầu bằng mã tỉnh (2 chữ số).")
    if not re.search(r"[A-Z]", normalized_plate):
        raise ValueError("Biển số phải chứa ký tự chữ cái.")


def parse_vehicle_type(raw_type: str) -> VehicleType:
    normalized = re.sub(r"[^a-z_]", "", raw_type.lower())
    vehicle_type = _TYPE_ALIASES.get(normalized)
    if vehicle_type is None:
        raise ValueError("Loại xe chỉ nhận 'oto' hoặc 'xemay'.")
    return vehicle_type
