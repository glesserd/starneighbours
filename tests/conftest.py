from pathlib import Path
from typing import Iterator
from starneighbours.main import app
from fastapi.testclient import TestClient
import pytest
from starneighbours.repositories.sqlite_api_token import SQLiteAPITokenRepository


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    """Create a temporary database path."""
    return tmp_path / "test_api_tokens.db"


@pytest.fixture
def test_token_name() -> str:
    return "test-token"


@pytest.fixture
def repo_token(
    db_path: Path, test_token_name: str
) -> Iterator[SQLiteAPITokenRepository]:
    """Create a repository with a temporary database."""
    # Override the DB_PATH in the repository
    SQLiteAPITokenRepository.DB_PATH = db_path
    repo = SQLiteAPITokenRepository()

    # Insert a test token
    repo.create("test-name", test_token_name, "test-comments")

    yield repo


@pytest.fixture
def logged_client_http(
    test_token_repo: SQLiteAPITokenRepository,
) -> Iterator[TestClient]:
    test_token_repo.create("test-token", "test-api-token", "Test token for API tests")
    client = TestClient(app, headers={"Authorization": "Bearer test-api-token"})
    yield client


@pytest.fixture
def client_http() -> Iterator[TestClient]:
    client = TestClient(app, headers={"Authorization": ""})
    yield client
