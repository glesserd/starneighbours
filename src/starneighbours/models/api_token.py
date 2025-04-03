# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from datetime import datetime
from abc import ABC, abstractmethod
from pydantic import BaseModel


class APIToken(BaseModel):
    id: int
    name: str
    hashed_token: str
    created_at: datetime
    updated_at: datetime
    comments: str = ""


class APITokenRepository(ABC):
    @abstractmethod
    def get_by_token(self, token: str) -> APIToken | None:
        """Get an API token by its hashed value."""
        raise NotImplementedError
