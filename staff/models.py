from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from core.models import TenantAwareModel


class Designation(models.Model):
    """
    Replaces tblDesignation.
    Maps organizational titles directly to technical permission groups.
    """

    name = models.CharField(max_length=100, unique=True)
    short_name = models.CharField(max_length=20, blank=True)
    is_teaching_staff = models.BooleanField(default=True)
    ui_priority = models.FloatField(default=0.0)

    # Long-term architecture hook: Safe to migrate into populated tables
    system_group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="linked_designations",
        help_text="The security permission group automatically mapped to this employment title.",
    )

    class Meta:
        ordering = ["ui_priority"]

    def __str__(self):
        return self.name


class ScaleOfPay(models.Model):
    """Replaces tblScaleOfPay"""

    scale_range = models.CharField(max_length=50, unique=True)
    remarks = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name_plural = "Scales of Pay"

    def __str__(self):
        return self.scale_range


class Employee(TenantAwareModel):
    """The Anchor: Minimal identity. Access this to list staff names."""

    staff_id = models.IntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=150)
    short_name = models.CharField(max_length=10, blank=True)
    gender = models.ForeignKey("core.Gender", on_delete=models.RESTRICT)
    designation = models.ForeignKey(Designation, on_delete=models.RESTRICT)
    status = models.ForeignKey("core.Status", on_delete=models.RESTRICT)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="employee_profile",
    )

    class Meta:
        ordering = ["designation__ui_priority", "name"]
        # Database constraint removed to keep your pre-existing data perfectly safe

    def __str__(self):
        return f"{self.name} ({self.designation.short_name})"

    def clean(self):
        """
        Application-Level Guardian:
        Strictly restricts the system from assigning more than one Principal
        to a single school tenant context. Runs in Admin and full API lifecycle.
        """
        super().clean()
        if hasattr(self, "school") and hasattr(self, "designation"):
            if self.designation.name.lower() == "principal":
                existing_principals = Employee.objects.filter(
                    school=self.school, designation=self.designation
                ).exclude(id=self.id)

                if existing_principals.exists():
                    raise ValidationError(
                        {
                            "designation": f"Operational conflict: '{self.school.name}' already has an active Principal assigned."
                        }
                    )

    def save(self, *args, **kwargs):
        # Enforces validation clean checks during manual script data executions
        self.full_clean()
        super().save(*args, **kwargs)


class EmployeeServiceRecord(models.Model):
    """HR Access Zone: Service history."""

    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE, related_name="service_record"
    )
    join_date = models.DateField(null=True, blank=True)
    ret_date = models.DateField(null=True, blank=True)
    qualification = models.CharField(max_length=150, blank=True)
    primary_subject = models.ForeignKey(
        "academics.Subject", on_delete=models.SET_NULL, null=True
    )


class EmployeeFinanceRecord(models.Model):
    """Finance Access Zone: Restricted to specific authorized staff only."""

    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE, related_name="finance_record"
    )
    pan_no = models.CharField(max_length=20, blank=True)
    pen_no = models.CharField(max_length=20, blank=True)
    pf_account_no = models.CharField(max_length=50, blank=True)
    bank_ac_no = models.CharField(max_length=50, blank=True)
    bank = models.ForeignKey("core.Bank", on_delete=models.SET_NULL, null=True)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True)


class EmployeeDemographicRecord(models.Model):
    """Private Access Zone: PII/Sensitive data."""

    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE, related_name="demographic_record"
    )
    dob = models.DateField(null=True, blank=True)
    religion = models.ForeignKey("core.Religion", on_delete=models.SET_NULL, null=True)
    caste = models.ForeignKey("core.Caste", on_delete=models.SET_NULL, null=True)
    phone_no = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
