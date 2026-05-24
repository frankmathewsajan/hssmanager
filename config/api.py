from ninja import NinjaAPI

# Import from your new 'routers' directory
from .routers.auth import auth_router
from .routers.students import students_router

api = NinjaAPI(title="HSS Manager API", version="1.0.0")

# 1. Mount the Public Router (Login)
api.add_router("/auth", auth_router)

# 2. Mount the Secure Router (Students)
# (Assuming you already added auth=JWTAuth() inside the students_router itself)
api.add_router("/students", students_router)
