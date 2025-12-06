# Routers package
from .auth import router as auth_router
from .cars import router as cars_router
from .stations import router as stations_router
from .trips import router as trips_router
from .suggestions import router as suggestions_router
from .dashboard import router as dashboard_router

__all__ = [
    "auth_router",
    "cars_router",
    "stations_router",
    "trips_router",
    "suggestions_router",
    "dashboard_router"
]