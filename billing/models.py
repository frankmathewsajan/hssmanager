from django.db import models
from decimal import Decimal
import logging

from academics.models import AcademicGroup
from students.models import Student

logger = logging.getLogger(__name__)

class FeeStructure(models.Model):
    """
    The 'Menu'. Replaces the fee columns from tblGroup.
    Linked 1-to-1 with AcademicGroup.
    """
    academic_group = models.OneToOneField(
        AcademicGroup,
        on_delete=models.CASCADE,
        related_name="fee_structure",
    )

    # Core Fees
    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tuition_concession = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )  # For SC/ST/OEC

    # Standard Funds
    pta_fund = models.DecimalField(max_digits=10, decimal_places=2, default=500)
    library_fee = models.DecimalField(max_digits=10, decimal_places=2, default=100)
    other_fees = models.DecimalField(max_digits=10, decimal_places=2, default=800)

    # Gendered Uniforms
    uniform_boys = models.DecimalField(max_digits=10, decimal_places=2, default=1300)
    uniform_girls = models.DecimalField(max_digits=10, decimal_places=2, default=1800)

    def __str__(self):
        return f"Fees: {self.academic_group.name}"


class StudentInvoice(models.Model):
    """
    The 'Receipt'. A permanent, unchangeable snapshot of what a student owes for a specific year.
    """
    student = models.ForeignKey(
        Student, on_delete=models.RESTRICT, related_name="invoices"
    )
    academic_year = models.CharField(max_length=9)  # e.g., "2026-27"

    # The calculated totals (Saved permanently here)
    total_due = models.DecimalField(max_digits=10, decimal_places=2)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_cleared = models.BooleanField(default=False)

    generated_on = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ["student", "academic_year"]

    def __str__(self):
        return f"Invoice: {self.student.name} ({self.academic_year})"

    @classmethod
    def generate_invoice(cls, student, academic_year):
        """
        THE SPECIAL SAUCE: Safely calculates and locks in a student's invoice 
        dues without breaking runtime operations.
        """
        # 1. Defensive Guard: Ensure student is assigned to a physical class layout context
        if not student.class_now:
            logger.warning(f"Aborting Invoice generation: Student {student.id} has no class assigned.")
            return None

        # 2. Extract relationships safely via attributes check guards
        academic_group = getattr(student.class_now, "academic_group", None)
        if not academic_group:
            logger.warning(f"Aborting Invoice: Class {student.class_now} lacks an AcademicGroup.")
            return None

        structure = getattr(academic_group, "fee_structure", None)
        if not structure:
            logger.warning(f"Aborting Invoice: Academic Group {academic_group} has no fee structure set.")
            return None

        # 3. Base Fee Calculation
        total = structure.pta_fund + structure.library_fee + structure.other_fees

        # 4. Defensive Gender Logic
        gender_name = student.gender.name.lower() if student.gender else "male"
        if gender_name == "male":
            total += structure.uniform_boys
        else:
            total += structure.uniform_girls

        # 5. Community/Caste Concession Logic
        # We explicitly look at student.caste, then fall back safely if unassigned
        concession_communities = ["S. C.", "S. T.", "O. E. C."]
        
        community_name = None
        if student.caste and student.caste.community:
            community_name = student.caste.community.name

        if community_name in concession_communities:
            total += structure.tuition_concession
        else:
            total += structure.tuition_fee

        # 6. Create or overwrite the permanent snapshot map
        invoice, created = cls.objects.update_or_create(
            student=student,
            academic_year=academic_year,
            defaults={"total_due": total}
        )
        return invoice