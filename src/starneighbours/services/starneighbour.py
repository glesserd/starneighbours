# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from collections import defaultdict
from typing import List
from ..models.github import GitHubRepository, StarNeighbour


class StarNeighbourService:
    def __init__(self, github_repo: GitHubRepository):
        self.github_repo = github_repo

    async def find_neighbours(self, user: str, repo: str) -> List[StarNeighbour]:
        """Find repositories that share stargazers with the given repository.

        Args:
            user: GitHub username
            repo: Repository name

        Returns:
            List of StarNeighbour objects containing repositories and their common stargazers

        Raises:
            GitHubAPIError: If the GitHub API returns an error
            RateLimitError: If we hit the GitHub API rate limit
        """

        target_stargazers = await self.github_repo.get_stargazers(user, repo)

        repo_to_stargazers = defaultdict(list)

        for stargazer in target_stargazers:
            starred_repos = await self.github_repo.get_starred_repos(stargazer.login)
            for starred_repo in starred_repos:
                # Don't include the target repository itself
                if f"{user}/{repo}" != starred_repo.full_name:
                    repo_to_stargazers[starred_repo.full_name].append(stargazer)

        # Convert to StarNeighbour objects
        return [
            StarNeighbour(repo=starred_repo, stargazers=stargazers)
            for starred_repo, stargazers in repo_to_stargazers.items()
        ]
