from ninja import Router, File
from ninja.files import UploadedFile
from ninja_jwt.authentication import JWTAuth
from typing import List
from django.db import transaction
from django.http import Http404
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import Student, StudentAcademicRecord, HscapCandidate
from academics.models import SchoolClass
from core.models import Gender, Religion, Caste, Quota, Status, SecondLanguage
from core.security import check_permission

from .schemas import (
    StudentOut,
    StudentIn,
    HSCAPPreviewOut,
    HSCAPBatchConfirmIn,
    AdmitCandidateIn,
)
from .services import extract_hscap_allotment

students_router = Router(tags=["Students"], auth=JWTAuth())


@students_router.get("/", response=List[StudentOut])
def list_students(request):
    check_permission(request, "students.view_student")
    school_code = request.auth.employee_profile.school.tenant_code
    return Student.objects.select_related("gender", "class_now").filter(
        school__tenant_code=school_code
    )


@students_router.post("/", response={201: StudentOut})
def admit_student(request, data: StudentIn):
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

    parsed_data = extract_hscap_allotment(file.file.read())

    if "error" in parsed_data:
        return 400, {"detail": parsed_data["error"]}
    return 200, parsed_data


@students_router.post("/onboard/confirm", response={201: dict, 400: dict})
def confirm_hscap_batch(request, payload: HSCAPBatchConfirmIn):
    check_permission(request, "students.add_student")
    user_school = request.auth.employee_profile.school

    success_count = 0
    skipped_count = 0
    
    with transaction.atomic():
        for student_data in payload.students:
            app_num_clean = str(student_data.app_num).strip()
            
            # Idempotency Lock: Skip processing if they are already fully admitted
            if Student.objects.filter(school=user_school, app_num=int(app_num_clean)).exists():
                skipped_count += 1
                continue

            # Standardized filter query logic to handle explicit index race conditions safely
            HscapCandidate.objects.update_or_create(
                school=user_school,
                app_num=app_num_clean,
                defaults={
                    "name": student_data.name,
                    "reg_num": student_data.reg_num,
                    "dob": student_data.dob if student_data.dob else None,
                    "gender_text": student_data.gender,
                    "second_language_text": student_data.second_language,
                    "status": "PENDING",
                },
            )
            success_count += 1

    return 201, {
        "detail": f"Successfully queued {success_count} candidates. Skipped {skipped_count} active students."
    }


from .schemas import HscapCandidateOut


@students_router.get("/staging-queue", response=List[HscapCandidateOut])
def list_staged_candidates(request):
    """Fetches all inbound candidates waiting for physical admission."""
    check_permission(request, "students.view_student")
    user_school = request.auth.employee_profile.school

    return (
        HscapCandidate.objects.filter(school=user_school, status="PENDING")
        .select_related("target_class")
        .order_by("name")
    )


@students_router.post("/admit-candidate/", response={200: dict})
def admit_physical_candidate(request, payload: AdmitCandidateIn):
    """Step 3: The student physically arrived. Move from Staging to Permanent Database Pool."""
    check_permission(request, "students.add_student")
    user_school = request.auth.employee_profile.school
    
    candidate = get_object_or_404(
        HscapCandidate, id=payload.candidate_id, school=user_school
    )

    with transaction.atomic():
        gender_str = candidate.gender_text.lower()
        if "f" in gender_str:
            gender = Gender.objects.filter(name__icontains="female").first()
        else:
            gender = Gender.objects.filter(name__icontains="male").first()

        slang = SecondLanguage.objects.filter(
            name__icontains=candidate.second_language_text
        ).first()
        status = (
            Status.objects.filter(name__iexact="Studying").first()
            or Status.objects.first()
        )
        quota = Quota.objects.first()
        religion = Religion.objects.first()
        caste = Caste.objects.first()

        last_student = (
            Student.objects.filter(school=user_school).order_by("-ad_num").first()
        )
        current_ad_num = (last_student.ad_num + 1) if last_student else 1000

        # Note: ad_class and class_now are omitted here so the student joins the unassigned pool
        new_student = Student.objects.create(
            ad_num=current_ad_num,
            app_num=int(candidate.app_num),
            name=candidate.name,
            dob=candidate.dob,
            gender=gender,
            religion=religion,
            caste=caste,
            ad_date=timezone.now().date(),
            ad_year="2026-27",
            ad_quota=quota,
            second_language=slang,
            study_status=status,
            school=user_school,
        )

        acad_record = StudentAcademicRecord.objects.get(student=new_student)
        acad_record.sec_reg_num = candidate.reg_num
        acad_record.save()

        if payload.is_permanent:
            candidate.delete()
        else:
            candidate.status = "TEMP_ADMIT"
            candidate.save()

    return 200, {
        "detail": f"Admitted {new_student.name} with Admission No: {new_student.ad_num}"
    }


@students_router.get("/meta/lookups", response={200: dict})
def get_admission_metadata(request):
    employee = getattr(request.auth, "employee_profile", None)
    if not employee:
        raise Http404("Active employment context missing.")

    user_school = employee.school
    return 200, {
        "classes": list(
            SchoolClass.objects.filter(school=user_school).values("id", "name")
        ),
        "genders": list(Gender.objects.values("id", "name")),
        "rel religions": list(Religion.objects.values("id", "name")),
        "castes": list(Caste.objects.values("id", "name")),
        "quotas": list(Quota.objects.values("id", "name")),
        "statuses": list(Status.objects.values("id", "name")),
    }