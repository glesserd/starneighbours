from fastapi import FastAPI

from starneighbours.repositories import api

app = FastAPI(
    title="StarNeighbours API",
    description="Find what stargazers of a repo have also starred",
    version="0.1.0",
)

# Include routers
app.include_router(api.router, prefix="/api/v1", tags=["health"])
