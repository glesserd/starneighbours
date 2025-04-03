# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from fastapi import FastAPI, Depends

from .repositories.api import router
from .auth import get_current_token


app = FastAPI(
    title="Starneighbours",
    description="Find what stargazers of a repo have also starred.",
    version="1.0.0",
)

# Include routers
app.include_router(router, prefix="/api/v1", dependencies=[Depends(get_current_token)])
