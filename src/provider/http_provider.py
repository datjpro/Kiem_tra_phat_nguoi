from __future__ import annotations

import httpx

from src.models import VehicleType, Violation
from src.provider.base import ViolationProvider


class HttpViolationProvider(ViolationProvider):
    def __init__(self, base_url: str, token: str, timeout_seconds: int) -> None:
        self._base_url = base_url.rstrip("/")
        self._token = token
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout=max(1, float(timeout_seconds)))
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def check_violations(
        self, plate: str, vehicle_type: VehicleType
    ) -> list[Violation]:
        url = f"{self._base_url}/check"
        headers = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        payload = {"plate": plate, "vehicle_type": vehicle_type.value}
        resp = await self._client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

        violations = []
        for item in data.get("violations", []):
            violations.append(
                Violation(
                    violation_id=str(item.get("id", "")),
                    occurred_at=str(item.get("date", "")),
                    location=str(item.get("location", "")),
                    behavior=str(item.get("behavior", "")),
                    fine=str(item.get("fine", "")),
                    source=str(item.get("source", "http_provider")),
                )
            )

        return violations
