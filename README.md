# starneighbours

Find what stargazers of a repo have also starred.



## About the project

The goal is to provide an API that from a GitHub repository provides a list of repositories that are starred by at least one people in common.


## Running

1. Get a GitHub token.

Follow the [documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token). No rights required.
Once done, set it to your env variables:

```sh
export GITHUB_TOKEN="your token here"
```


2. Start the server

```sh
uv run uvicorn src.starneighbours.main:app  --host 0.0.0.0 --port 8080
```


3. Perform requests

Go to http://127.0.0.1:8080/docs, or:
```sh
curl -X 'GET' \
  'http://127.0.0.1:8080/api/v1/repos/DigitalCarbonFramework/DigitalCarbonFramework/starneighbours' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer your-api-token'
```


## API Token Management

The API requires authentication using a bearer token. Tokens are stored in a SQLite database at `data/api_tokens.db`.

To add a new API token, you can use the following command:

```sh
uv run python -c "from src.starneighbours.repositories.sqlite_api_token import SQLiteAPITokenRepository ; SQLiteAPITokenRepositor
y().create('token-name', 'your-secret-token-here')"
```

Replace `your-secret-token-here` with your desired token, `token-name` with a descriptive name, and optionally add comments.

## Develop

You can start the server in debug mode by setting the `DEBUG` env variable.
It gives access to the swagger documentation in `/docs`.

To test, run `pytest .`.

Every merge requests should satisfy `mypy`, `ruff format` and `ruff check`.
```sh
uv run ruff format .
uv run ruff check .
uv run mypy .
```

You can calculate the coverage using `coverage`:
```sh
uv run coverage run -m pytest
uv run coverage report -m
```

As we use the MPL2 license, don't forget to add following the header to all "important" files:
```python
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
```

Architecture:

**Services**
- Services encapsulate the business logic of the application.
- Functions within services follow the naming convention: <entity>_<action>. For example: user_create.
    - The entity can either represent a highly technical component (e.g., S3) or something easily understood by the app's users.
    - The action is a verb, typically one of: get, list, update, create, or delete.
- A service will manipulate objects declared in models.
- A service can never dependes on a repository. Use the injection dependency framework of fastAPI to declare the necessity to use a repository.

**Repositories**
- Repositories handle communication with external systems such as databases or APIs.
- Public methods only handle basic python types or types declared in models
- Repositories implement classes declared in models.
- A repository cannot depends on a service.

**Models**
- Define the basic data manipulated by the APP
- Declare interfaces that will be used by services and implemented by repositories
- Models can only depends on models.



## Roadmap

- [x] Create a basic README
- [x] Set-up the structure
- [x] Create a starneighbour service that depends on a github repository.
    The repository can, from a `github_user` and `github_repo`, get the stargazers of that repo.
    The repository can also from a `github_user`, get the repositories that it has starred.
    The starneighbour service returns the list of neighbours repositories, meaning repositories where at least one stargazer is found in common.
    ```
      [
        {
        "repo": <repoA>,
            "stargazers": [<stargazers in common>, ...],
        },
        {
        "repo": <repo>,
            "stargazers": [<stargazers in common>, ...],
        },
        ...
      ]
    ```
    When writing tests, don't forget to mock the github API.
    Be careful, the github API endpoints might returns error or unexpected data.
    If the githib API returns a `x-ratelimit-reset` header, relay this error and raise an error. Document all of that.
- [x] Create the `GET /repos/<user>/<repo>/starneighbours` endpoint that uses the starneighbour service.
    Write tests, don't forget to mock GitHub API.
- [x] Add auth using a bearer token.
    Use an sqlite database, performing SQL request without any ORM.
    Have a `api_tokens` table with `name`, `hashed_token`, `update_at`, `created_at`, `comments`.
    Add to the README a bash on liner to add an hashed token to an existing database.
- [ ] Use a singleton for the DB, see `dependency-injector`.
- [ ] Use some salt for the hash.
- [ ] use OAuth auth. If it make sense to have a piece of frontend, it could reduce the probability of exceeding the rate limit of github API.
- [ ] Check lint, mypy and tests in the CI.
- [ ] cache requests and/or paginate results. Technically its a big plus. Ask PO if it can be done.
- [ ] add sorting by proximity and alphanumeric.
- [ ] manage nicely exceptions and errors. Use a tool like Sentry and manage mre nicely errors (eg. timeout).
- [ ] check json data returned by api. 
- [ ] use a real dependency injection lib, like `dependency-injector`.
- [ ] centralized settings that reads env variables.
