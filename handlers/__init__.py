from .base import router as base_router
from .russian import router as ru_router
from .uzbek import router as uz_router


routers = [
    base_router,
    ru_router,
    uz_router,
]