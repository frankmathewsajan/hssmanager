from django.db import models, transaction
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


class Student(TenantAwareModel):
    ad_num = models.PositiveIntegerField(unique=True, blank=True)
    app_num = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=150, db_index=True)
    dob = models.DateField()
    gender = models.ForeignKey(Gender, on_delete=models.RESTRICT)

    religion = models.ForeignKey(Religion, on_delete=models.RESTRICT)
    parish = models.ForeignKey(Parish, on_delete=models.SET_NULL, null=True, blank=True)
    caste = models.ForeignKey(Caste, on_delete=models.RESTRICT)
    is_catholic = models.BooleanField(default=False)

    ad_date = models.DateField()
    ad_year = models.CharField(max_length=9)
    ad_quota = models.ForeignKey(Quota, on_delete=models.RESTRICT)

    ad_class = models.ForeignKey(
        SchoolClass, on_delete=models.RESTRICT, related_name="admissions"
    )
    class_now = models.ForeignKey(
        SchoolClass, on_delete=models.RESTRICT, related_name="current_students"
    )
    class_roll_num = models.IntegerField(null=True, blank=True)

    second_language = models.ForeignKey(
        SecondLanguage, on_delete=models.RESTRICT, null=True, blank=True
    )
    study_status = models.ForeignKey(Status, on_delete=models.RESTRICT)

    def __str__(self):
        return f"{self.ad_num} - {self.name}"

    def clean(self):
        super().clean()
        if self.parish and self.religion:
            if self.religion.name not in ["Christian", "Catholic"]:
                raise ValidationError(
                    {
                        "parish": "A Parish can only be assigned to Catholic/Christian students."
                    }
                )

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.ad_num:
                last_student = (
                    Student.objects.filter(school=self.school)
                    .order_by("-ad_num")
                    .first()
                )
                self.ad_num = (last_student.ad_num + 1) if last_student else 1000

            self.full_clean()
            super().save(*args, **kwargs)


class StudentProfile(models.Model):
    student = models.OneToOneField(
        Student, on_delete=models.CASCADE, related_name="profile"
    )
    aadhar_number = models.CharField(max_length=12, blank=True, null=True, unique=True)
    bank = models.ForeignKey(Bank, on_delete=models.SET_NULL, null=True, blank=True)
    bank_ac_number = models.CharField(max_length=30, blank=True, null=True)

    father_name = models.CharField(max_length=150, blank=True)
    father_occupation = models.ForeignKey(
        Occupation, on_delete=models.SET_NULL, null=True, related_name="fathers"
    )
    mother_name = models.CharField(max_length=150, blank=True)
    mother_occupation = models.ForeignKey(
        Occupation, on_delete=models.SET_NULL, null=True, related_name="mothers"
    )
    guardian_name = models.CharField(max_length=150, blank=True)

    pmt_address_1 = models.CharField(max_length=200, blank=True)
    pmt_address_2 = models.CharField(max_length=200, blank=True)
    pmt_district = models.ForeignKey(
        District, on_delete=models.SET_NULL, null=True, related_name="pmt_residents"
    )
    pmt_pin = models.CharField(max_length=10, blank=True)
    pmt_phone = models.CharField(max_length=20, blank=True)

    pst_address_1 = models.CharField(max_length=200, blank=True)
    pst_address_2 = models.CharField(max_length=200, blank=True)
    pst_district = models.ForeignKey(
        District, on_delete=models.SET_NULL, null=True, related_name="pst_residents"
    )
    pst_pin = models.CharField(max_length=10, blank=True)
    pst_phone = models.CharField(max_length=20, blank=True)

    bus_route = models.ForeignKey(
        BusRoute, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"Profile: {self.student.name}"

    def save(self, *args, **kwargs):
        if self.aadhar_number == "":
            self.aadhar_number = None
        super().save(*args, **kwargs)


class StudentAcademicRecord(models.Model):
    student = models.OneToOneField(
        Student, on_delete=models.CASCADE, related_name="academic_record"
    )
    prev_school = models.CharField(max_length=250, blank=True)
    sec_study_type = models.ForeignKey(
        StudyType, on_delete=models.SET_NULL, null=True, blank=True
    )
    sec_reg_num = models.CharField(max_length=50, blank=True)
    index_score = models.FloatField(null=True, blank=True)

    tc_date = models.DateField(null=True, blank=True)
    tc_number = models.CharField(max_length=50, blank=True)
    reason_for_leave = models.CharField(max_length=250, blank=True)

    passed_hse = models.BooleanField(default=False)
    hse_reg_no = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"Records: {self.student.name}"
