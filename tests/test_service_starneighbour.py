# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from unittest.mock import AsyncMock
import pytest
from starneighbours.models.github import (
    GitHubRepo,
    GitHubUser,
    StarNeighbour,
    GitHubAPIError,
)
from starneighbours.services.starneighbour import StarNeighbourService


@pytest.mark.asyncio
async def test_find_neighbours() -> None:
    mock_github_repo = AsyncMock()
    mock_github_repo.get_stargazers.return_value = [
        GitHubUser(login="user1"),
        GitHubUser(login="user2"),
    ]
    mock_github_repo.get_starred_repos.side_effect = [
        [
            GitHubRepo(
                name="repo1",
                full_name="owner1/repo1",
                description="Repo 1",
                html_url="https://github.com/owner1/repo1",
                stargazers_count=100,
            ),
        ],
        [
            GitHubRepo(
                name="repo2",
                full_name="owner2/repo2",
                description="Repo 2",
                html_url="https://github.com/owner2/repo2",
                stargazers_count=200,
            ),
        ],
    ]

    service = StarNeighbourService(mock_github_repo)
    neighbours = await service.find_neighbours("owner", "target-repo")

    assert len(neighbours) == 2
    assert all(isinstance(n, StarNeighbour) for n in neighbours)
    assert {n.repo for n in neighbours} == {"owner1/repo1", "owner2/repo2"}

    # Verify the repository was called correctly
    mock_github_repo.get_stargazers.assert_called_once_with("owner", "target-repo")
    assert mock_github_repo.get_starred_repos.call_count == 2
    mock_github_repo.get_starred_repos.assert_any_call("user1")
    mock_github_repo.get_starred_repos.assert_any_call("user2")


@pytest.mark.asyncio
async def test_find_neighbours_excludes_target_repo() -> None:
    mock_github_repo = AsyncMock()
    mock_github_repo.get_stargazers.return_value = [
        GitHubUser(login="user1"),
    ]

    mock_github_repo.get_starred_repos.return_value = [
        GitHubRepo(
            name="target-repo",
            full_name="owner/target-repo",
            description="Target repo",
            html_url="https://github.com/owner/target-repo",
            stargazers_count=100,
        ),
        GitHubRepo(
            name="other-repo",
            full_name="owner/other-repo",
            description="Other repo",
            html_url="https://github.com/owner/other-repo",
            stargazers_count=200,
        ),
    ]
    service = StarNeighbourService(mock_github_repo)
    neighbours = await service.find_neighbours("owner", "target-repo")

    assert len(neighbours) == 1
    assert neighbours[0].repo == "owner/other-repo"


@pytest.mark.asyncio
async def test_find_neighbours_handles_errors() -> None:
    mock_github_repo = AsyncMock()
    mock_github_repo.get_stargazers.return_value = [
        GitHubUser(login="user1"),
        GitHubUser(login="user2"),
    ]

    mock_github_repo.get_starred_repos.side_effect = [
        [
            GitHubRepo(
                name="repo1",
                full_name="owner1/repo1",
                description="Repo 1",
                html_url="https://github.com/owner1/repo1",
                stargazers_count=100,
            ),
        ],
        GitHubAPIError("API Error"),
    ]

    service = StarNeighbourService(mock_github_repo)
    with pytest.raises(GitHubAPIError):
        await service.find_neighbours("owner", "target-repo")
