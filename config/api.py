# backend/config/api.py
from ninja import NinjaAPI, Schema
from typing import List
from academics.models import SchoolClass
from .auth_router import auth_router

# 1. Import the JWT Authenticator
from ninja_jwt.authentication import JWTAuth

api = NinjaAPI(title="HSS Manager API", version="1.0.0")

# Mount the auth router (Public - no token needed to log in)
api.add_router("/auth", auth_router)


class SchoolClassOut(Schema):
    id: int
    name: str
    academic_year: int
    group_name: str
    class_teacher_name: str = None

    @staticmethod
    def resolve_group_name(obj):
        return obj.academic_group.name if obj.academic_group else "Unassigned"

    @staticmethod
    def resolve_class_teacher_name(obj):
        return obj.class_teacher.name if obj.class_teacher else "No Teacher"


# 2. Secure the endpoint using auth=JWTAuth()
@api.get("/classes", response=List[SchoolClassOut], auth=JWTAuth())
def list_classes(request):
    """
    Returns classes ONLY for the school of the logged-in user.
    If the token is missing or invalid, Ninja automatically returns a 401 Unauthorized.
    """
    # Because of JWTAuth, request.user is now a real Django User object!
    # We navigate through the OneToOne field to get the Employee, then the School.
    user_school = request.user.employee_profile.school

    return SchoolClass.objects.select_related("academic_group", "class_teacher").filter(
        school=user_school
    )
