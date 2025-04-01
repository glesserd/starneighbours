from fastapi import APIRouter, Depends

router = APIRouter()


async def get_health_checker() -> dict[str, str]:
    # This is a simple dependency that could be expanded
    # to check database connections, external services, etc.
    return {"status": "healthy"}


@router.get("/health", response_model=dict[str, str])
async def health_check(
    health_status: dict[str, str] = Depends(get_health_checker),
) -> dict[str, str]:
    return health_status
