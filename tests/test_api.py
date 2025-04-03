# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Iterator
from starneighbours.main import app
from starneighbours.models.github import (
    GitHubUser,
    StarNeighbour,
    GitHubAPIError,
    RateLimitError,
)


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


def test_get_starneighbours_success(mock_starneighbour_service: AsyncMock) -> None:
    client = TestClient(app)
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

    response = client.get("/api/v1/repos/testuser/testrepo/starneighbours")

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


def test_get_starneighbours_rate_limit(mock_starneighbour_service: AsyncMock) -> None:
    client = TestClient(app)
    mock_starneighbour_service.find_neighbours.side_effect = RateLimitError(1234567890)

    response = client.get("/api/v1/repos/testuser/testrepo/starneighbours")

    assert response.status_code == 429
    assert response.json() == {
        "detail": "GitHub API rate limit exceeded. Reset at 1234567890"
    }


def test_get_starneighbours_api_error(mock_starneighbour_service: AsyncMock) -> None:
    client = TestClient(app)
    mock_starneighbour_service.find_neighbours.side_effect = GitHubAPIError()

    response = client.get("/api/v1/repos/testuser/testrepo/starneighbours")

    assert response.status_code == 500
    assert response.json() == {"detail": "Error fetching data from GitHub API"}
