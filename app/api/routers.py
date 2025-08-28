from app.api.auth import router as auth_router
from app.api.users import router as users_router

all_routers = [
    auth_router,
    users_router,
]
