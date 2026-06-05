# backend/students/schemas.py
from ninja import Schema
from typing import List, Optional
from datetime import date


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


# --- HSCAP Onboarding Schemas ---


class HSCAPPreviewStudent(Schema):
    app_num: str
    rank: str  # NEW
    option: str  # NEW
    name: str
    reg_num: str
    dob: str
    gender: str
    second_language: str
    fee_status: str  # NEW


class HSCAPPreviewOut(Schema):
    course_info: Optional[str]
    students: List[HSCAPPreviewStudent]


class HSCAPBatchConfirmIn(Schema):
    ad_date: str
    students: List[HSCAPPreviewStudent]


class AdmitCandidateIn(Schema):
    candidate_id: int
    class_id: int
    is_permanent: bool  # True = Permanent Admission, False = Temporary (Waiting for higher option)


class HscapCandidateOut(Schema):
    id: int
    app_num: str
    name: str
    reg_num: str
    dob: date | None = None  # 👈 2. CHANGE 'str' TO 'date'
    gender_text: str
    second_language_text: str
    target_class_name: str
    status: str
    allotment_round: str

    @staticmethod
    def resolve_target_class_name(obj):
        return obj.target_class.name if obj.target_class else "Unassigned"
