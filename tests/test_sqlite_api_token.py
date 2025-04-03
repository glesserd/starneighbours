# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from datetime import datetime
import sqlite3
from starneighbours.models.api_token import APIToken
from starneighbours.repositories.sqlite_api_token import SQLiteAPITokenRepository


def test_init_creates_table(repo_token: SQLiteAPITokenRepository) -> None:
    """Test that initialization creates the api_tokens table."""

    with sqlite3.connect(SQLiteAPITokenRepository.DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='api_tokens'
        """)
        assert cursor.fetchone() is not None


def test_get_by_token_returns_none_for_nonexistent_token(
    repo_token: SQLiteAPITokenRepository,
) -> None:
    """Test that get_by_token returns None for a nonexistent token."""
    assert repo_token.get_by_token("nonexistent-token") is None


def test_get_by_token_returns_token(
    repo_token: SQLiteAPITokenRepository, test_token_name: str
) -> None:
    """Test that get_by_token returns the correct token."""

    result = repo_token.get_by_token(test_token_name)
    assert result is not None
    assert isinstance(result, APIToken)
    assert result.name == "test-name"
    assert result.comments == "test-comments"
    assert isinstance(result.created_at, datetime)
    assert isinstance(result.updated_at, datetime)


def test_get_by_token_returns_none_for_wrong_token(
    repo_token: SQLiteAPITokenRepository,
) -> None:
    """Test that get_by_token returns None for a wrong token."""

    assert repo_token.get_by_token("wrong-token") is None
