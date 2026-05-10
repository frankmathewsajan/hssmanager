from django.db import models
from decimal import Decimal
from academics.models import AcademicGroup
from students.models import Student


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
    academic_year = models.CharField(max_length=9)  # e.g., "2016-17"

    # The calculated totals (Saved permanently here)
    total_due = models.DecimalField(max_digits=10, decimal_places=2)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_cleared = models.BooleanField(default=False)

    generated_on = models.DateField(auto_now_add=True)

    class Meta:
        # A student can only have one master invoice per academic year
        unique_together = ["student", "academic_year"]

    def __str__(self):
        return f"Invoice: {self.student.name} ({self.academic_year})"

    @classmethod
    def generate_invoice(cls, student, academic_year):
        """
        THE SPECIAL SAUCE: Your father's FindFee logic translated to 2026 Python.
        This is called explicitly ONLY when a student is admitted or promoted.
        """
        # 1. Get the Menu
        structure = student.class_now.academic_group.fee_structure

        # 2. Base Fees (PTA + Library + Other)
        total = structure.pta_fund + structure.library_fee + structure.other_fees

        # 3. Gender Logic
        if student.gender.name.lower() == "male":
            total += structure.uniform_boys
        else:
            total += structure.uniform_girls

        # 4. Community/Caste Concession Logic
        concession_communities = ["S. C.", "S. T.", "O. E. C."]
        if student.caste.community.name in concession_communities:
            total += structure.tuition_concession
        else:
            total += structure.tuition_fee

        # 5. Create the permanent snapshot
        return cls.objects.create(
            student=student, academic_year=academic_year, total_due=total
        )
