# backend/config/api.py
from ninja import NinjaAPI
from django.core.exceptions import PermissionDenied

# Import Auth
from config.routers.auth import auth_router

# Import Domain Routers
from core.router import router as core_router
from academics.router import router as academics_router
from students.routers import router as students_router

api = NinjaAPI(title="HSS Manager API", version="1.0.0")

# Catch Django's native PermissionDenied exception and transform it into a clean 403 API response
@api.exception_handler(PermissionDenied)
def permission_denied_handler(request, exc):
    return api.create_response(request, {"detail": str(exc)}, status=403)

# 1. Authentication
api.add_router("/auth", auth_router)

# 2. Domains
api.add_router("/core", core_router)           # Meta lookups, global settings
api.add_router("/academics", academics_router) # Classes, subjects, teachers
api.add_router("/students", students_router)   # The master student router