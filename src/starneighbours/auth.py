# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from .models.api_token import APIToken
from .repositories.sqlite_api_token import SQLiteAPITokenRepository


security = HTTPBearer()


async def get_current_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    token_repo: SQLiteAPITokenRepository = Depends(SQLiteAPITokenRepository),
) -> APIToken:
    """Validate and return the current API token."""
    token = token_repo.get_by_token(credentials.credentials)
    if not token:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )
    return token
