# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from unittest.mock import MagicMock, patch
import pytest
from starneighbours.models.github import GitHubAPIError, RateLimitError
from starneighbours.repositories.github import GitHubAPIRepository


@pytest.mark.asyncio
async def test_github_repository_rate_limit() -> None:
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.headers = {"x-ratelimit-reset": "1234567890"}
        mock_response.is_success = False
        mock_response.text = "Rate limit exceeded"

        mock_client.return_value.__aenter__.return_value.request.return_value = (
            mock_response
        )

        repo = GitHubAPIRepository("test-token")

        with pytest.raises(RateLimitError) as exc_info:
            await repo.get_stargazers("owner", "repo")

        assert exc_info.value.reset_time == 1234567890


@pytest.mark.asyncio
async def test_github_repository_api_error() -> None:
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.is_success = False
        mock_response.text = "Not found"

        mock_client.return_value.__aenter__.return_value.request.return_value = (
            mock_response
        )

        repo = GitHubAPIRepository("test-token")

        with pytest.raises(GitHubAPIError) as exc_info:
            await repo.get_stargazers("owner", "repo")

        assert "GitHub API error: 404 - Not found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_github_repository_get_stargazers_success() -> None:
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = [{"login": "user1"}, {"login": "user2"}]

        mock_client.return_value.__aenter__.return_value.request.return_value = (
            mock_response
        )

        repo = GitHubAPIRepository("test-token")
        stargazers = await repo.get_stargazers("owner", "repo")

        assert len(stargazers) == 2
        assert {stargazers[0].login, stargazers[1].login} == {"user1", "user2"}


@pytest.mark.asyncio
async def test_github_repository_get_starred_repos_success() -> None:
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = [
            {
                "name": "repo1",
                "full_name": "owner/repo1",
                "description": "Test repo 1",
                "html_url": "https://github.com/owner/repo1",
                "stargazers_count": 100,
            },
            {
                "name": "repo2",
                "full_name": "owner/repo2",
                "description": None,
                "html_url": "https://github.com/owner/repo2",
                "stargazers_count": 200,
            },
        ]

        mock_client.return_value.__aenter__.return_value.request.return_value = (
            mock_response
        )

        repo = GitHubAPIRepository("test-token")
        repos = await repo.get_starred_repos("user")

        assert len(repos) == 2
        assert repos[0].name == "repo1"
        assert repos[0].full_name == "owner/repo1"
        assert repos[0].description == "Test repo 1"
        assert repos[0].html_url == "https://github.com/owner/repo1"
        assert repos[0].stargazers_count == 100
        assert repos[1].name == "repo2"
        assert repos[1].full_name == "owner/repo2"
        assert repos[1].description is None
        assert repos[1].html_url == "https://github.com/owner/repo2"
        assert repos[1].stargazers_count == 200


@pytest.mark.asyncio
async def test_github_repository_pagination() -> None:
    with patch("httpx.AsyncClient") as mock_client:
        # First page response
        mock_response1 = MagicMock()
        mock_response1.status_code = 200
        mock_response1.is_success = True
        mock_response1.json.return_value = [{"login": "user1"}, {"login": "user2"}]

        # Second page response (empty)
        mock_response2 = MagicMock()
        mock_response2.status_code = 200
        mock_response2.is_success = True
        mock_response2.json.return_value = []

        mock_client_instance = mock_client.return_value.__aenter__.return_value
        mock_client_instance.request.side_effect = [mock_response1, mock_response2]

        repo = GitHubAPIRepository("test-token")
        repo.PER_PAGE = 2  # type: ignore[misc]
        stargazers = await repo.get_stargazers("owner", "repo")

        assert len(stargazers) == 2
        assert mock_client_instance.request.call_count == 2
        # Verify the pagination parameter was used
        assert 1 == mock_client_instance.request.call_args_list[0][1]["params"]["page"]
        assert 2 == mock_client_instance.request.call_args_list[1][1]["params"]["page"]
