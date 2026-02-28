from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass

from src.models import VehicleType


@dataclass(frozen=True)
class Subscription:
    row_id: int
    chat_id: int
    plate: str
    vehicle_type: VehicleType
    last_fingerprint: str


class Repository:
    def __init__(self, sqlite_path: str) -> None:
        self._sqlite_path = sqlite_path
        db_dir = os.path.dirname(sqlite_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._sqlite_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    plate TEXT NOT NULL,
                    vehicle_type TEXT NOT NULL,
                    last_fingerprint TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(chat_id, plate, vehicle_type)
                );
                """
            )
            conn.commit()

    def add_subscription(
        self, chat_id: int, plate: str, vehicle_type: VehicleType
    ) -> bool:
        try:
            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO subscriptions (chat_id, plate, vehicle_type)
                    VALUES (?, ?, ?);
                    """,
                    (chat_id, plate, vehicle_type.value),
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def remove_subscription(
        self, chat_id: int, plate: str, vehicle_type: VehicleType
    ) -> bool:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                DELETE FROM subscriptions
                WHERE chat_id = ? AND plate = ? AND vehicle_type = ?;
                """,
                (chat_id, plate, vehicle_type.value),
            )
            conn.commit()
            return cursor.rowcount > 0

    def list_subscriptions(self, chat_id: int) -> list[Subscription]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, chat_id, plate, vehicle_type, last_fingerprint
                FROM subscriptions
                WHERE chat_id = ?
                ORDER BY id DESC;
                """,
                (chat_id,),
            ).fetchall()
        return [
            Subscription(
                row_id=row[0],
                chat_id=row[1],
                plate=row[2],
                vehicle_type=VehicleType(row[3]),
                last_fingerprint=row[4],
            )
            for row in rows
        ]

    def list_all_subscriptions(self) -> list[Subscription]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, chat_id, plate, vehicle_type, last_fingerprint
                FROM subscriptions
                ORDER BY id ASC;
                """
            ).fetchall()

        return [
            Subscription(
                row_id=row[0],
                chat_id=row[1],
                plate=row[2],
                vehicle_type=VehicleType(row[3]),
                last_fingerprint=row[4],
            )
            for row in rows
        ]

    def update_fingerprint(self, row_id: int, fingerprint: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE subscriptions
                SET last_fingerprint = ?
                WHERE id = ?;
                """,
                (fingerprint, row_id),
            )
            conn.commit()
