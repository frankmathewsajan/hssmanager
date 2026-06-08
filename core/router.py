# backend/core/router.py
from ninja import Router
from django.http import Http404
from ninja_jwt.authentication import JWTAuth

from academics.models import SchoolClass
from core.models import Gender, Religion, Caste, Community, Quota, Status

router = Router(tags=["Core Configuration"], auth=JWTAuth())

@router.get("/lookups", response={200: dict})
def get_global_lookups(request):
    """Fetches clean runtime dropdown metadata with strict relational mappings."""
    employee = getattr(request.auth, "employee_profile", None)
    if not employee:
        raise Http404("Active employment context missing.")
    user_school = employee.school
    
    return 200, {
        "classes": list(SchoolClass.objects.filter(school=user_school).values("id", "name")),
        "genders": list(Gender.objects.values("id", "name")),
        "religions": list(Religion.objects.values("id", "name")),
        "communities": list(Community.objects.values("id", "name")),
        "castes": list(Caste.objects.values("id", "name", "community_id")), # 👈 Injects relational key
        "quotas": list(Quota.objects.values("id", "name")),
        "statuses": list(Status.objects.values("id", "name")),
    }