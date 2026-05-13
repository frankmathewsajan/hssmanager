# students/models.py
from django.db import models
from django.core.exceptions import ValidationError

from core.models import (
    Gender,
    Parish,
    Religion,
    Caste,
    Status,
    Quota,
    SecondLanguage,
    District,
    BusRoute,
    Occupation,
    Bank,
    StudyType,
    TenantAwareModel,
)
from academics.models import SchoolClass


# -----------------------------------------------------------------------------
# TABLE 1: THE ANCHOR (Strictly Core Identity & Current State)
# -----------------------------------------------------------------------------
class Student(TenantAwareModel):
    ad_num = models.IntegerField(unique=True, db_index=True)
    app_num = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=150)
    dob = models.DateField()
    gender = models.ForeignKey(Gender, on_delete=models.RESTRICT)

    # Demographics
    religion = models.ForeignKey(Religion, on_delete=models.RESTRICT)
    parish = models.ForeignKey(Parish, on_delete=models.SET_NULL, null=True, blank=True)
    caste = models.ForeignKey(Caste, on_delete=models.RESTRICT)
    is_catholic = models.BooleanField(default=False)

    # Admission Details
    ad_date = models.DateField()
    ad_year = models.CharField(max_length=9)  # e.g., "2016-17"
    ad_quota = models.ForeignKey(Quota, on_delete=models.RESTRICT)

    # Academic State
    ad_class = models.ForeignKey(
        SchoolClass, on_delete=models.RESTRICT, related_name="admissions"
    )
    class_now = models.ForeignKey(
        SchoolClass, on_delete=models.RESTRICT, related_name="current_students"
    )
    class_roll_num = models.IntegerField(null=True, blank=True)

    # We map this to the SecondLanguage lookup table instead of flat text
    second_language = models.ForeignKey(
        SecondLanguage, on_delete=models.RESTRICT, null=True
    )
    study_status = models.ForeignKey(Status, on_delete=models.RESTRICT)

    def __str__(self):
        return f"{self.ad_num} - {self.name}"

    def clean(self):
        super().clean()
        if self.parish is not None and self.religion.name not in [
            "Christian",
            "Catholic",
        ]:
            raise ValidationError(
                {
                    "parish": "A Parish can only be assigned to Catholic/Christian students."
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


# -----------------------------------------------------------------------------
# TABLE 2: THE PROFILE (Family, Addresses, Sensitive Data)
# -----------------------------------------------------------------------------
class StudentProfile(models.Model):
    student = models.OneToOneField(
        Student, on_delete=models.CASCADE, related_name="profile"
    )

    # Sensitive / Government (Separated for security)
    aadhar_number = models.CharField(max_length=12, blank=True, null=True, unique=True)
    bank = models.ForeignKey(Bank, on_delete=models.SET_NULL, null=True, blank=True)
    bank_ac_number = models.CharField(max_length=30, blank=True, null=True)

    # Parents
    father_name = models.CharField(max_length=150, blank=True)
    father_occupation = models.ForeignKey(
        Occupation, on_delete=models.SET_NULL, null=True, related_name="fathers"
    )
    mother_name = models.CharField(max_length=150, blank=True)
    mother_occupation = models.ForeignKey(
        Occupation, on_delete=models.SET_NULL, null=True, related_name="mothers"
    )
    guardian_name = models.CharField(max_length=150, blank=True)

    # Permanent Address
    pmt_address_1 = models.CharField(max_length=200, blank=True)
    pmt_address_2 = models.CharField(max_length=200, blank=True)
    pmt_district = models.ForeignKey(
        District, on_delete=models.SET_NULL, null=True, related_name="pmt_residents"
    )
    pmt_pin = models.CharField(max_length=10, blank=True)
    pmt_phone = models.CharField(max_length=20, blank=True)

    # Present Address (Only filled if different)
    pst_address_1 = models.CharField(max_length=200, blank=True)
    pst_address_2 = models.CharField(max_length=200, blank=True)
    pst_district = models.ForeignKey(
        District, on_delete=models.SET_NULL, null=True, related_name="pst_residents"
    )
    pst_pin = models.CharField(max_length=10, blank=True)
    pst_phone = models.CharField(max_length=20, blank=True)

    # Transport
    bus_route = models.ForeignKey(
        BusRoute, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"Profile: {self.student.name}"


# -----------------------------------------------------------------------------
# TABLE 3: ACADEMIC HISTORY (Past Schooling & TC Records)
# -----------------------------------------------------------------------------
class StudentAcademicRecord(models.Model):
    """Isolates data that happened *before* they joined, or *after* they left."""

    student = models.OneToOneField(
        Student, on_delete=models.CASCADE, related_name="academic_record"
    )

    # Before HSS
    prev_school = models.CharField(max_length=250, blank=True)
    sec_study_type = models.ForeignKey(
        StudyType, on_delete=models.SET_NULL, null=True, blank=True
    )
    sec_reg_num = models.CharField(max_length=50, blank=True)
    index_score = models.FloatField(null=True, blank=True)

    # Exit / TC Details (Stays null until they leave)
    tc_date = models.DateField(null=True, blank=True)
    tc_number = models.CharField(max_length=50, blank=True)
    reason_for_leave = models.CharField(max_length=250, blank=True)

    # Board Results
    passed_hse = models.BooleanField(default=False)
    hse_reg_no = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"Records: {self.student.name}"
