from ninja import Router, File
from ninja.files import UploadedFile
from typing import List
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404

from students.models import Student, StudentAcademicRecord, HscapCandidate
from core.models import Gender, Religion, Caste, Quota, Status, SecondLanguage
from core.security import check_permission
from students.schemas import HSCAPPreviewOut, HSCAPBatchConfirmIn, AdmitCandidateIn, HscapCandidateOut
from students.services import extract_hscap_allotment

router = Router()

@router.post("/parse", response={200: HSCAPPreviewOut, 400: dict})
def parse_hscap_pdf(request, file: UploadedFile = File(...)):
    check_permission(request, "students.add_student")
    if not file.name.lower().endswith(".pdf"):
        return 400, {"detail": "Invalid file format. Please upload the official HSCAP PDF."}
    parsed_data = extract_hscap_allotment(file.file.read())
    if "error" in parsed_data:
        return 400, {"detail": parsed_data["error"]}
    return 200, parsed_data

@router.post("/confirm", response={201: dict})
def confirm_hscap_batch(request, payload: HSCAPBatchConfirmIn):
    check_permission(request, "students.add_student")
    user_school = request.auth.employee_profile.school
    success_count = 0
    skipped_count = 0
    
    with transaction.atomic():
        for student_data in payload.students:
            app_num_clean = str(student_data.app_num).strip()
            if Student.objects.filter(school=user_school, app_num=int(app_num_clean)).exists():
                skipped_count += 1
                continue

            HscapCandidate.objects.update_or_create(
                school=user_school, app_num=app_num_clean,
                defaults={
                    "name": student_data.name, "reg_num": student_data.reg_num,
                    "dob": student_data.dob if student_data.dob else None,
                    "gender_text": student_data.gender, "second_language_text": student_data.second_language,
                    "status": "PENDING",
                }
            )
            success_count += 1
    return 201, {"detail": f"Successfully queued {success_count} candidates. Skipped {skipped_count} active students."}

@router.get("/staging-queue", response=List[HscapCandidateOut])
def list_staged_candidates(request):
    check_permission(request, "students.view_student")
    user_school = request.auth.employee_profile.school
    return HscapCandidate.objects.filter(school=user_school, status="PENDING").order_by("name")

@router.post("/admit-physical/", response={200: dict})
def admit_physical_candidate(request, payload: AdmitCandidateIn):
    check_permission(request, "students.add_student")
    user_school = request.auth.employee_profile.school
    candidate = get_object_or_404(HscapCandidate, id=payload.candidate_id, school=user_school)

    with transaction.atomic():
        gender_str = candidate.gender_text.lower()
        gender = Gender.objects.filter(name__icontains="female").first() if "f" in gender_str else Gender.objects.filter(name__icontains="male").first()
        slang = SecondLanguage.objects.filter(name__icontains=candidate.second_language_text).first()
        status = Status.objects.filter(name__iexact="Studying").first() or Status.objects.first()

        last_student = Student.objects.filter(school=user_school).order_by("-ad_num").first()
        current_ad_num = (last_student.ad_num + 1) if last_student else 1000

        new_student = Student.objects.create(
            ad_num=current_ad_num, app_num=int(candidate.app_num), name=candidate.name,
            dob=candidate.dob, gender=gender, religion=Religion.objects.first(),
            caste=Caste.objects.first(), ad_date=timezone.now().date(), ad_year="2026-27",
            ad_quota=Quota.objects.first(), second_language=slang, study_status=status,
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

    return 200, {"detail": f"Admitted {new_student.name} with Admission No: {new_student.ad_num}"}