# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import os
from typing import Any, Final
import httpx
from ..models.github import (
    GitHubRepo,
    GitHubRepository,
    GitHubUser,
    GitHubAPIError,
    RateLimitError,
)


class GitHubAPIRepository(GitHubRepository):
    # We request 100 items per page, so 1M is too many objects for sure
    MAX_PAGES: Final[int] = 100_000
    # see https://docs.github.com/en/rest/activity/starring?apiVersion=2022-11-28#list-repositories-starred-by-the-authenticated-user
    PER_PAGE: Final[int] = 100

    def __init__(self, token: str | None = None):
        self.token = token or os.environ.get("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GitHub token is required")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.token}",
        }

    async def _make_request(
        self, method: str, path: str, params: dict[str, int | str]
    ) -> list[dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"{self.base_url}{path}",
                params={**params, "per_page": self.PER_PAGE},
                headers=self.headers,
            )

            if response.status_code == 403 and "x-ratelimit-reset" in response.headers:
                reset_time = int(response.headers["x-ratelimit-reset"])
                raise RateLimitError(reset_time)

            if not response.is_success:
                raise GitHubAPIError(
                    f"GitHub API error: {response.status_code} - {response.text}"
                )

            return response.json()

    async def get_stargazers(self, user: str, repo: str) -> list[GitHubUser]:
        stargazers = []
        page = 1

        while page < self.MAX_PAGES:
            returned_data = await self._make_request(
                method="GET",
                path=f"/repos/{user}/{repo}/stargazers",
                params={"page": page},
            )
            stargazers.extend(
                [GitHubUser(login=data["login"]) for data in returned_data]
            )

            if not returned_data or len(returned_data) < self.PER_PAGE:
                break

            page += 1

        return stargazers

    async def get_starred_repos(self, user: str) -> list[GitHubRepo]:
        repos = []
        page = 1

        while page < self.MAX_PAGES:
            data = await self._make_request(
                method="GET",
                path=f"/users/{user}/starred",
                params={"page": page},
            )
            repos.extend(
                [
                    GitHubRepo(
                        name=repo["name"],
                        full_name=repo["full_name"],
                        description=repo.get("description"),
                        html_url=repo["html_url"],
                        stargazers_count=repo["stargazers_count"],
                    )
                    for repo in data
                ]
            )
            if not data or len(data) < self.PER_PAGE:
                break

            page += 1

        return repos
