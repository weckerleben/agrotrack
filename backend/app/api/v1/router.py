from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, silos, alerts, logistics, dashboard, weather

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(silos.router, prefix="/silos", tags=["silos"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(logistics.router, prefix="/logistics", tags=["logistics"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(weather.router, prefix="/weather", tags=["weather"]) 