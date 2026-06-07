# backend/core/router.py
from ninja import Router
from django.http import Http404
from ninja_jwt.authentication import JWTAuth

from academics.models import SchoolClass
from core.models import Gender, Religion, Caste, Quota, Status

# Added tags and auth
router = Router(tags=["Core Configuration"], auth=JWTAuth())

@router.get("/lookups", response={200: dict})
def get_global_lookups(request):
    """Fetches all dropdown metadata for forms across the app."""
    employee = getattr(request.auth, "employee_profile", None)
    if not employee:
        raise Http404("Active employment context missing.")
    user_school = employee.school
    
    return 200, {
        "classes": list(SchoolClass.objects.filter(school=user_school).values("id", "name")),
        "genders": list(Gender.objects.values("id", "name")),
        "religions": list(Religion.objects.values("id", "name")),
        "castes": list(Caste.objects.values("id", "name")),
        "quotas": list(Quota.objects.values("id", "name")),
        "statuses": list(Status.objects.values("id", "name")),
    }