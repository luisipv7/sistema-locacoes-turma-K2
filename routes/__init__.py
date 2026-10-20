from routes.auth import router as auth_router
from routes.health import router as health_check
from routes.category import router as category

__all__ = ["auth_router", "category"]
