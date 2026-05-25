# backend/config/api.py
from ninja import NinjaAPI
from django.core.exceptions import PermissionDenied
from config.routers.auth import auth_router
from students.router import students_router

api = NinjaAPI(title="HSS Manager API", version="1.0.0")


# Catch Django's native PermissionDenied exception and transform it into a clean 403 API response
@api.exception_handler(PermissionDenied)
def permission_denied_handler(request, exc):
    return api.create_response(request, {"detail": str(exc)}, status=403)


api.add_router("/auth", auth_router)
api.add_router("/students", students_router)
