# backend/students/router.py
from ninja import Router, Schema
from ninja_jwt.authentication import JWTAuth

from typing import List
from django.db import transaction
from django.http import Http404
from django.core.exceptions import PermissionDenied

from .models import Student
from academics.models import SchoolClass
from core.models import Gender, Religion, Caste, Quota, Status
from core.security import check_permission

# Instantiate the router. The global auth setup is passed down natively.
students_router = Router(tags=["Students"], auth=JWTAuth())


class StudentOut(Schema):
    id: int
    ad_num: int | None = None
    name: str
    gender_name: str
    class_name: str

    @staticmethod
    def resolve_gender_name(obj):
        return obj.gender.name if obj.gender else "Unknown"

    @staticmethod
    def resolve_class_name(obj):
        return obj.class_now.name if obj.class_now else "Unassigned"


class StudentIn(Schema):
    name: str
    dob: str
    gender_id: int
    religion_id: int
    caste_id: int
    ad_date: str
    ad_year: str
    ad_quota_id: int
    ad_class_id: int
    class_now_id: int
    study_status_id: int


@students_router.get("/", response=List[StudentOut])
def list_students(request):
    """
    Returns all students belonging to the authenticated tenant school.
    Guarded by standard Django permissions framework.
    """
    # 1. Enforce the permission check natively using Django's auth backend
    check_permission(request, "students.view_student")

    # 2. Proceed with multi-tenant filtering safely
    employee = request.auth.employee_profile
    school_code = employee.school.tenant_code
    return Student.objects.select_related("gender", "class_now").filter(
        school__tenant_code=school_code
    )


@students_router.post("/", response={201: StudentOut})
def admit_student(request, data: StudentIn):
    """Admits a new student inside the correct school context."""
    # 1. Enforce the add permission cleanly
    check_permission(request, "students.add_student")

    user_school = request.auth.employee_profile.school
    create_params = data.dict()
    create_params["school"] = user_school

    with transaction.atomic():
        if not create_params.get("ad_num"):
            last_student = (
                Student.objects.filter(school=user_school).order_by("-ad_num").first()
            )
            create_params["ad_num"] = (
                (last_student.ad_num + 1)
                if (last_student and last_student.ad_num)
                else 1000
            )

        student = Student.objects.create(**create_params)

    return 201, student


@students_router.get("/meta/lookups", response={200: dict})
def get_admission_metadata(request):
    """Utility endpoint providing lookup data for the frontend."""
    employee = getattr(request.auth, "employee_profile", None)
    if not employee:
        raise Http404("Active employment context missing.")

    user_school = employee.school
    return 200, {
        "classes": list(
            SchoolClass.objects.filter(school=user_school).values("id", "name")
        ),
        "genders": list(Gender.objects.values("id", "name")),
        "religions": list(Religion.objects.values("id", "name")),
        "castes": list(Caste.objects.values("id", "name")),
        "quotas": list(Quota.objects.values("id", "name")),
        "statuses": list(Status.objects.values("id", "name")),
    }
