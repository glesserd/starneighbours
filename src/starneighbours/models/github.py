# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class GitHubUser:
    login: str


@dataclass
class GitHubRepo:
    name: str
    full_name: str
    description: Optional[str]
    html_url: str
    stargazers_count: int


@dataclass
class StarNeighbour:
    repo: str
    stargazers: List[GitHubUser]


class GitHubAPIError(Exception):
    """Raised when the GitHub API returns an error."""

    pass


class RateLimitError(Exception):
    """Raised when we hit the GitHub API rate limit."""

    def __init__(self, reset_time: int):
        self.reset_time = reset_time
        super().__init__(f"Rate limit exceeded. Reset at {reset_time}")


class GitHubRepository(ABC):
    @abstractmethod
    async def get_stargazers(self, user: str, repo: str) -> List[GitHubUser]:
        """Get all stargazers of a repository.

        Args:
            user: GitHub username
            repo: Repository name

        Returns:
            List of GitHub users who starred the repository

        Raises:
            GitHubAPIError: If the GitHub API returns an error
            RateLimitError: If we hit the GitHub API rate limit
        """
        pass

    @abstractmethod
    async def get_starred_repos(self, user: str) -> List[GitHubRepo]:
        """Get all repositories starred by a user.

        Args:
            user: GitHub username

        Returns:
            List of repositories starred by the user

        Raises:
            GitHubAPIError: If the GitHub API returns an error
            RateLimitError: If we hit the GitHub API rate limit
        """
        pass
