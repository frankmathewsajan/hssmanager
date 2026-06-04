# backend/students/schemas.py
from ninja import Schema
from typing import List, Optional


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
    name: str
    reg_num: str
    dob: str
    gender: str
    second_language: str


class HSCAPPreviewOut(Schema):
    course_info: Optional[str]
    students: List[HSCAPPreviewStudent]


class HSCAPBatchConfirmIn(Schema):
    class_id: int
    ad_date: str
    students: List[HSCAPPreviewStudent]
