# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from ..models.api_token import APIToken, APITokenRepository


class SQLiteAPITokenRepository(APITokenRepository):
    """SQLite implementation of the API token repository."""

    DB_PATH = Path("data/api_tokens.db")

    def __init__(self) -> None:
        """Initialize the database if it doesn't exist."""
        self.DB_PATH.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    hashed_token TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    comments TEXT
                )
            """)
            conn.commit()

    def get_by_token(self, token: str) -> Optional[APIToken]:
        """Get an API token by its hashed value."""
        hashed_token = hashlib.sha256(token.encode()).hexdigest()

        with sqlite3.connect(self.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, name, hashed_token, created_at, updated_at, comments
                FROM api_tokens
                WHERE hashed_token = ?
                """,
                (hashed_token,),
            )

            row = cursor.fetchone()
            if not row:
                return None

            return APIToken(
                id=row[0],
                name=row[1],
                hashed_token=row[2],
                created_at=datetime.fromisoformat(row[3]),
                updated_at=datetime.fromisoformat(row[4]),
                comments=row[5],
            )

    def create(self, token_name: str, token: str, comments: str = "") -> str:
        """Create a new API token."""
        hashed_token = hashlib.sha256(token.encode()).hexdigest()
        now = datetime.now(tz=timezone.utc).isoformat()

        with sqlite3.connect(self.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO api_tokens (name, hashed_token, created_at, updated_at, comments)
                VALUES (?, ?, ?, ?, ?)
                """,
                (token_name, hashed_token, now, now, comments),
            )
            conn.commit()
        return hashed_token
