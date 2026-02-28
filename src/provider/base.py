from __future__ import annotations

from abc import ABC, abstractmethod

from src.models import VehicleType, Violation


class ViolationProvider(ABC):
    @abstractmethod
    async def check_violations(
        self, plate: str, vehicle_type: VehicleType
    ) -> list[Violation]:
        raise NotImplementedError
