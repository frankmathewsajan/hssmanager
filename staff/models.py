# staff/models.py
from django.db import models


class Designation(models.Model):
    """Replaces tblDesignation"""

    name = models.CharField(max_length=100, unique=True)  # e.g., 'Principal'
    short_name = models.CharField(max_length=20, blank=True)  # e.g., 'HSST (Jr)'

    # Replaces the text "Teaching" / "Non Teaching" with a clean boolean
    is_teaching_staff = models.BooleanField(default=True)

    ui_priority = models.FloatField(default=0.0)  # From nPriority (e.g., 1.0, 2.0)

    class Meta:
        ordering = ["ui_priority"]

    def __str__(self):
        return self.name


class ScaleOfPay(models.Model):
    """Replaces tblScaleOfPay"""

    # E.g., '21240-37040'
    scale_range = models.CharField(max_length=50, unique=True)
    remarks = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name_plural = "Scales of Pay"

    def __str__(self):
        return self.scale_range


class Employee(models.Model):
    """Replaces tblStaff. The master record for a staff member."""

    # -------------------------------------------------------------------------
    # 1. CORE IDENTITY
    # -------------------------------------------------------------------------
    staff_id = models.IntegerField(unique=True, db_index=True)  # E.g., 69
    name = models.CharField(max_length=150)
    short_name = models.CharField(max_length=10, blank=True)  # E.g., 'JJS'
    gender = models.ForeignKey("core.Gender", on_delete=models.RESTRICT)
    dob = models.DateField(null=True, blank=True)

    # -------------------------------------------------------------------------
    # 2. ROLE & ACADEMICS
    # -------------------------------------------------------------------------
    designation = models.ForeignKey(Designation, on_delete=models.RESTRICT)

    # Nullable because Menial/Peon won't have a subject
    primary_subject = models.ForeignKey(
        "academics.Subject", on_delete=models.SET_NULL, null=True, blank=True
    )
    status = models.ForeignKey("core.Status", on_delete=models.RESTRICT)

    # -------------------------------------------------------------------------
    # 3. SERVICE HISTORY
    # -------------------------------------------------------------------------
    join_date = models.DateField(null=True, blank=True)
    ret_date = models.DateField(null=True, blank=True)  # Retirement Date
    transfer_date = models.DateField(null=True, blank=True)
    qualification = models.CharField(max_length=150, blank=True)

    # -------------------------------------------------------------------------
    # 4. GOVERNMENT & FINANCIAL (SPARK / KERALA DB)
    # -------------------------------------------------------------------------
    pan_no = models.CharField(max_length=20, blank=True)
    pen_no = models.CharField(max_length=20, blank=True)  # Kerala Employee ID
    election_id_no = models.CharField(max_length=30, blank=True)
    name_of_lac = models.CharField(max_length=100, blank=True)  # Constituency

    scale_of_pay = models.ForeignKey(
        ScaleOfPay, on_delete=models.SET_NULL, null=True, blank=True
    )
    basic_salary = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    pf_account_no = models.CharField(max_length=50, blank=True)
    bank_ac_no = models.CharField(max_length=50, blank=True)
    bank = models.ForeignKey(
        "core.Bank", on_delete=models.SET_NULL, null=True, blank=True
    )

    # -------------------------------------------------------------------------
    # 5. DEMOGRAPHICS & CONTACT
    # -------------------------------------------------------------------------
    religion = models.ForeignKey(
        "core.Religion", on_delete=models.SET_NULL, null=True, blank=True
    )
    caste = models.ForeignKey(
        "core.Caste", on_delete=models.SET_NULL, null=True, blank=True
    )
    parish = models.ForeignKey(
        "core.Parish", on_delete=models.SET_NULL, null=True, blank=True
    )

    address = models.TextField(blank=True)
    phone_no = models.CharField(max_length=20, blank=True)
    mobile_no = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ["designation__ui_priority", "name"]

    def __str__(self):
        return f"{self.name} ({self.designation.short_name})"
