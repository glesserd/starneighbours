# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from fastapi import APIRouter, Depends, HTTPException
from starneighbours.models.github import GitHubRepository, StarNeighbour, GitHubAPIError, RateLimitError
from starneighbours.services.starneighbour import StarNeighbourService
from starneighbours.repositories.github import GitHubAPIRepository

router = APIRouter()


async def get_github_repo() -> GitHubRepository:
    return GitHubAPIRepository()


async def get_starneighbour_service(
    github_repo: GitHubRepository = Depends(get_github_repo),
) -> StarNeighbourService:
    return StarNeighbourService(github_repo)


@router.get("/repos/{user}/{repo}/starneighbours", response_model=list[StarNeighbour])
async def get_starneighbours(
    user: str,
    repo: str,
    service: StarNeighbourService = Depends(get_starneighbour_service),
) -> list[StarNeighbour]:
    """Get repositories that share stargazers with the given repository.

    Args:
        user: GitHub username
        repo: Repository name
        service: StarNeighbourService instance

    Returns:
        List of repositories that share stargazers with the given repository

    Raises:
        HTTPException: If the GitHub API returns an error or rate limit is exceeded
    """
    try:
        return await service.find_neighbours(user, repo)
    except RateLimitError as e:
        raise HTTPException(
            status_code=429,
            detail=f"GitHub API rate limit exceeded. Reset at {e.reset_time}",
        )
    except GitHubAPIError as e:
        raise HTTPException(
            status_code=500,
            detail="Error fetching data from GitHub API",
        )
