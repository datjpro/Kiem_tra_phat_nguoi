from __future__ import annotations

import re
import unicodedata

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
        raise ValueError("Bien so khong hop le.")
    return cleaned


def validate_plate(normalized_plate: str) -> None:
    if len(normalized_plate) < 7 or len(normalized_plate) > 11:
        raise ValueError("Bien so phai co do dai tu 7-11 ky tu.")
    if not normalized_plate[:2].isdigit():
        raise ValueError("Bien so phai bat dau bang ma tinh (2 chu so).")
    if not re.search(r"[A-Z]", normalized_plate):
        raise ValueError("Bien so phai chua ky tu chu cai.")


def parse_vehicle_type(raw_type: str) -> VehicleType:
    normalized_ascii = (
        unicodedata.normalize("NFKD", raw_type).encode("ascii", "ignore").decode("ascii")
    )
    normalized = re.sub(r"[^a-z_]", "", normalized_ascii.lower())
    vehicle_type = _TYPE_ALIASES.get(normalized)
    if vehicle_type is None:
        raise ValueError("Loai xe chi nhan 'oto' hoac 'xemay'.")
    return vehicle_type
