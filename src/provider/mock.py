from __future__ import annotations

from src.models import VehicleType, Violation
from src.provider.base import ViolationProvider


class MockViolationProvider(ViolationProvider):
    async def check_violations(
        self, plate: str, vehicle_type: VehicleType
    ) -> list[Violation]:
        # Useful for local development without external API integration.
        if int(sum(ord(ch) for ch in plate) % 2) == 0:
            return []

        return [
            Violation(
                violation_id=f"MOCK-{plate[-4:]}-001",
                occurred_at="2026-01-18 10:45",
                location="Nguyen Trai, Ha Noi",
                behavior="Vuot den do",
                fine="4.000.000 - 6.000.000 VND",
                source=f"mock/{vehicle_type.value}",
            )
        ]
