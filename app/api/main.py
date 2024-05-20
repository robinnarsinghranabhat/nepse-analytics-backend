from fastapi import APIRouter

from app.api.routes import daily_trades

api_router = APIRouter()

api_router.include_router(daily_trades.router, tags=["daily_trades"])
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
# api_router.include_router(items.router, prefix="/items", tags=["items"])
