# backend/students/router.py
from ninja import Router, File
from ninja.files import UploadedFile
from ninja_jwt.authentication import JWTAuth
from typing import List
from django.db import transaction
from django.http import Http404

from .models import Student, StudentAcademicRecord
from academics.models import SchoolClass
from core.models import Gender, Religion, Caste, Quota, Status, SecondLanguage
from core.security import check_permission

from .schemas import StudentOut, StudentIn, HSCAPPreviewOut, HSCAPBatchConfirmIn
from .services import extract_hscap_allotment

students_router = Router(tags=["Students"], auth=JWTAuth())


@students_router.get("/", response=List[StudentOut])
def list_students(request):
    """Returns all students belonging to the authenticated tenant school."""
    check_permission(request, "students.view_student")
    school_code = request.auth.employee_profile.school.tenant_code
    return Student.objects.select_related("gender", "class_now").filter(
        school__tenant_code=school_code
    )


@students_router.post("/", response={201: StudentOut})
def admit_student(request, data: StudentIn):
    """Admits a single student inside the correct school context."""
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
                (last_student.ad_num + 1) if last_student else 1000
            )

        student = Student.objects.create(**create_params)

    return 201, student


@students_router.post("/onboard/parse", response={200: HSCAPPreviewOut, 400: dict})
def parse_hscap_pdf(request, file: UploadedFile = File(...)):
    """Step 1: Extracts data from the uploaded HSCAP PDF and returns a structured preview."""
    check_permission(request, "students.add_student")

    if not file.name.lower().endswith(".pdf"):
        return 400, {
            "detail": "Invalid file format. Please upload the official HSCAP PDF."
        }

    # Pass the raw file bytes to our service layer
    parsed_data = extract_hscap_allotment(file.file.read())

    if "error" in parsed_data:
        return 400, {"detail": parsed_data["error"]}

    return 200, parsed_data


@students_router.post("/onboard/confirm", response={201: dict, 400: dict})
def confirm_hscap_batch(request, payload: HSCAPBatchConfirmIn):
    """Step 2: Commits the verified batch of students into the database."""
    check_permission(request, "students.add_student")
    user_school = request.auth.employee_profile.school

    try:
        target_class = SchoolClass.objects.get(id=payload.class_id, school=user_school)
    except SchoolClass.DoesNotExist:
        return 400, {"detail": "Target class not found or belongs to another school."}

    # Caching lookup records to prevent N+1 database queries inside the loop
    gender_map = {g.name.lower(): g for g in Gender.objects.all()}
    slang_map = {sl.name.lower(): sl for sl in SecondLanguage.objects.all()}

    # Resolving mandatory baseline defaults for fields not provided by the PDF
    default_status = (
        Status.objects.filter(name__iexact="Studying").first() or Status.objects.first()
    )
    default_quota = (
        Quota.objects.filter(name__icontains="Merit").first() or Quota.objects.first()
    )
    default_religion = Religion.objects.first()
    default_caste = Caste.objects.first()

    success_count = 0

    with transaction.atomic():
        # Retrieve the highest current admission number to sequence the new batch
        last_student = (
            Student.objects.filter(school=user_school).order_by("-ad_num").first()
        )
        current_ad_num = (last_student.ad_num + 1) if last_student else 1000

        for student_data in payload.students:
            # Fuzzy match gender (e.g., "Male", "Female")
            matched_gender = gender_map.get(
                student_data.gender.lower()
            ) or gender_map.get("male")
            matched_slang = slang_map.get(student_data.second_language.lower())

            # 1. Create the base anchor.
            # Note: The signals framework will catch this and automatically provision the sidecars.
            new_student = Student.objects.create(
                ad_num=current_ad_num,
                app_num=(
                    int(student_data.app_num)
                    if student_data.app_num.isdigit()
                    else None
                ),
                name=student_data.name,
                dob=student_data.dob,
                gender=matched_gender,
                religion=default_religion,
                caste=default_caste,
                ad_date=payload.ad_date,
                ad_year="2026-27",
                ad_quota=default_quota,
                ad_class=target_class,
                class_now=target_class,
                second_language=matched_slang,
                study_status=default_status,
                school=user_school,
            )

            # 2. Update the academic record sidecar with the 10th grade register number
            # Using get() because the signal guarantees the record exists
            acad_record = StudentAcademicRecord.objects.get(student=new_student)
            acad_record.sec_reg_num = student_data.reg_num
            acad_record.save()

            current_ad_num += 1
            success_count += 1

    return 201, {
        "detail": f"Successfully enrolled {success_count} students into {target_class.name}."
    }


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
