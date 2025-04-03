# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Iterator
from starneighbours.models.github import (
    GitHubUser,
    StarNeighbour,
    GitHubAPIError,
    RateLimitError,
)
from starneighbours.repositories.sqlite_api_token import SQLiteAPITokenRepository


@pytest.fixture
def test_token() -> str:
    """Create a test API token."""
    return "test-api-token"


@pytest.fixture
def test_db_path(tmp_path: Path) -> Path:
    """Create a temporary database path."""
    return tmp_path / "test_api_tokens.db"


@pytest.fixture
def test_token_repo(test_db_path: Path) -> SQLiteAPITokenRepository:
    """Create a test token repository with a valid token."""
    # Override the DB_PATH in the repository
    SQLiteAPITokenRepository.DB_PATH = test_db_path
    repo = SQLiteAPITokenRepository()

    return repo


@pytest.fixture
def mock_github_repo() -> Iterator[MagicMock]:
    with patch("starneighbours.repositories.api.GitHubAPIRepository") as mock:
        yield mock


@pytest.fixture
def mock_starneighbour_service(mock_github_repo: MagicMock) -> Iterator[AsyncMock]:
    with patch("starneighbours.repositories.api.StarNeighbourService") as mock:
        service = AsyncMock()
        mock.return_value = service
        yield service


def test_get_starneighbours_success(
    mock_starneighbour_service: AsyncMock, logged_client_http: TestClient
) -> None:
    mock_starneighbour_service.find_neighbours.return_value = [
        StarNeighbour(
            repo="user1/repo1",
            stargazers=[GitHubUser(login="stargazer1"), GitHubUser(login="stargazer2")],
        ),
        StarNeighbour(
            repo="user2/repo2",
            stargazers=[GitHubUser(login="stargazer1")],
        ),
    ]

    response = logged_client_http.get("/api/v1/repos/testuser/testrepo/starneighbours")

    assert response.status_code == 200
    assert response.json() == [
        {
            "repo": "user1/repo1",
            "stargazers": [{"login": "stargazer1"}, {"login": "stargazer2"}],
        },
        {
            "repo": "user2/repo2",
            "stargazers": [{"login": "stargazer1"}],
        },
    ]
    mock_starneighbour_service.find_neighbours.assert_called_once_with(
        "testuser", "testrepo"
    )


def test_get_starneighbours_rate_limit(
    mock_starneighbour_service: AsyncMock, logged_client_http: TestClient
) -> None:
    mock_starneighbour_service.find_neighbours.side_effect = RateLimitError(1234567890)

    response = logged_client_http.get("/api/v1/repos/testuser/testrepo/starneighbours")

    assert response.status_code == 429
    assert response.json() == {
        "detail": "GitHub API rate limit exceeded. Reset at 1234567890"
    }


def test_get_starneighbours_api_error(
    mock_starneighbour_service: AsyncMock, logged_client_http: TestClient
) -> None:
    mock_starneighbour_service.find_neighbours.side_effect = GitHubAPIError()

    response = logged_client_http.get("/api/v1/repos/testuser/testrepo/starneighbours")

    assert response.status_code == 500
    assert response.json() == {"detail": "Error fetching data from GitHub API"}


def test_get_starneighbours_unauthorized(client_http: TestClient) -> None:
    """Test that requests without a valid token are rejected."""

    response = client_http.get("/api/v1/repos/testuser/testrepo/starneighbours")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}

    response = client_http.get(
        "/api/v1/repos/testuser/testrepo/starneighbours",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid authentication credentials"}
