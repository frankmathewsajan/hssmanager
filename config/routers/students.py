from ninja import Router, Schema
from typing import List
from students.models import Student
from academics.models import SchoolClass
from core.models import School, Gender, Religion, Caste, Quota, Status
from ninja_jwt.authentication import JWTAuth
from django.shortcuts import get_object_or_404
from django.db import transaction

students_router = Router(tags=["Students"], auth=JWTAuth())

# --- SCHEMAS ---


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


# A pure explicit schema matching exactly what Next.js is sending
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


# --- ENDPOINTS ---


@students_router.get("/", response=List[StudentOut])
def list_students(request):
    school_code = request.auth.employee_profile.school.tenant_code
    return Student.objects.select_related("gender", "class_now").filter(
        school__tenant_code=school_code
    )


@students_router.post("/", response={201: StudentOut})
def admit_student(request, data: StudentIn):
    """
    Admits a new student inside the correct school context.
    Sidecar rows are safely managed by active background model signals.
    """
    user_school = request.auth.employee_profile.school

    # We turn the parsed Pydantic payload directly into a dictionary
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

        # This invocation natively triggers handle_student_automation inside signals!
        student = Student.objects.create(**create_params)

        # FIX: Explicit manual instantiation of StudentProfile and StudentAcademicRecord
        # has been removed here to completely eliminate the 500 UniqueViolation crash loop.

    return 201, student


@students_router.get("/meta/lookups", response={200: dict})
def get_admission_metadata(request):
    user_school = request.auth.employee_profile.school
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
