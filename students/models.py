from django.db import models
from django.core.exceptions import ValidationError

from core.models import Gender, Parish, Religion, Caste, Status, Quota

from academics.models import SchoolClass


class Student(models.Model):
    """The Core Identity - The anchor for the whole system."""

    ad_num = models.IntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=150)
    dob = models.DateField()
    gender = models.ForeignKey(Gender, on_delete=models.RESTRICT)

    # -------------------------------------------------------------------------
    # DEMOGRAPHICS
    # -------------------------------------------------------------------------
    religion = models.ForeignKey(Religion, on_delete=models.RESTRICT)
    parish = models.ForeignKey(Parish, on_delete=models.SET_NULL, null=True, blank=True)
    caste = models.ForeignKey(Caste, on_delete=models.RESTRICT)

    # -------------------------------------------------------------------------
    # ADMISSION DETAILS (The Human Data)
    # -------------------------------------------------------------------------
    ad_date = models.DateField()
    ad_year = models.CharField(max_length=9)  # e.g., "2016-17"
    ad_quota = models.ForeignKey(Quota, on_delete=models.RESTRICT)

    # -------------------------------------------------------------------------
    # ACADEMIC STATE (The Room Data)
    # -------------------------------------------------------------------------
    # The room they sat in on Day 1 (Historical)
    ad_class = models.ForeignKey(
        SchoolClass, on_delete=models.RESTRICT, related_name="admissions"
    )
    # The room they are sitting in today (Current)
    class_now = models.ForeignKey(
        SchoolClass, on_delete=models.RESTRICT, related_name="current_students"
    )
    study_status = models.ForeignKey(Status, on_delete=models.RESTRICT)

    def __str__(self):
        return f"{self.ad_num} - {self.name}"

    def clean(self):
        super().clean()

        # Rule: Parish is ONLY valid if the student is Christian/Catholic
        if self.parish is not None:
            if self.religion.name not in ["Christian", "Catholic"]:
                raise ValidationError(
                    {
                        "parish": "A Parish can only be assigned to Catholic/Christian students."
                    }
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class StudentProfile(models.Model):
    """The sensitive/contact data. Linked 1-to-1 with Student."""

    # This is the magic link. If a student is deleted, this profile dies with them.
    student = models.OneToOneField(
        Student, on_delete=models.CASCADE, related_name="profile"
    )

    # Government IDs
    aadhar_number = models.CharField(max_length=12, blank=True, null=True, unique=True)
    bank_ac_number = models.CharField(max_length=30, blank=True, null=True)

    # Parents & Contacts
    father_name = models.CharField(max_length=150)
    mother_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    pmt_address = models.TextField(blank=True)
