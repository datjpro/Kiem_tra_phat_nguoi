from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class VehicleType(str, Enum):
    CAR = "oto"
    MOTORBIKE = "xemay"


@dataclass(frozen=True)
class Violation:
    violation_id: str
    occurred_at: str
    location: str
    behavior: str
    fine: str
    source: str


@dataclass(frozen=True)
class QueryResult:
    plate: str
    vehicle_type: VehicleType
    violations: list[Violation]
    checked_at: datetime


def now_utc() -> datetime:
    return datetime.now(tz=timezone.utc)
