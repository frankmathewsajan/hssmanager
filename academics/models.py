from django.db import models

from core.models import TenantAwareModel
from staff.models import Employee


class Subject(models.Model):
    """Replaces tblOptionalSub. A clean dictionary of all subjects."""

    code = models.CharField(
        max_length=20, unique=True, help_text="e.g., PHY, MATH, ENG"
    )
    name = models.CharField(max_length=100)

    # Optional: If subjects are strictly practical or theory
    is_practical = models.BooleanField(default=False)
    practical_max_marks = models.IntegerField(default=0)

    is_placeholder = models.BooleanField(default=False)

    # This is for subjects that are just placeholders in the curriculum, like 'Second Language' or 'Elective'.
    # They won't have actual marks or teachers assigned, but they help structure the academic groups.
    # If this is True, the system knows this isn't a real class (like Subject 21)
    # and it needs to check the Student's personal 'SecondLanguage' choice.
    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class AcademicGroup(TenantAwareModel):
    """
    Replaces tblGroup (The Academic side).
    e.g., 'Science with Biology', 'Commerce with Computer'.
    NOTE: The financial fields (Fees, Uniforms) will live in the 'billing' app.
    """

    code = models.CharField(
        max_length=10, unique=True, db_index=True
    )  # The old txtCode
    name = models.CharField(max_length=100)  # The old txtGroup
    stream = models.CharField(max_length=50)  # e.g., 'Science', 'Humanities'

    # We use a ManyToManyField instead of Sub1, Sub2, etc.
    # This means a Group can have 1 subject or 20 subjects without changing the database schema.
    core_subjects = models.ManyToManyField(Subject, related_name="groups")

    def __str__(self):
        return f"{self.stream}: {self.name}"


class SchoolClass(TenantAwareModel):
    """
    Replaces tblClass. Links a physical classroom to an Academic Group.
    We name it SchoolClass to avoid Python's 'class' keyword constraint.
    """

    # e.g., "A1", "B1"
    name = models.CharField(max_length=50, unique=True)

    YEAR_CHOICES = [
        (1, "1st Year (Plus One)"),
        (2, "2nd Year (Plus Two)"),
    ]
    academic_year = models.IntegerField(choices=YEAR_CHOICES)

    # Links this specific class to the broader curriculum/stream
    academic_group = models.ForeignKey(
        AcademicGroup, on_delete=models.RESTRICT, related_name="classes"
    )

    # From CSV: ClassTeacher (Homeroom/Main point of contact)
    class_teacher = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name="homeroom_classes",
    )

    # From CSV: Tutor (Assistant/Secondary point of contact)
    tutor = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name="tutored_classes",
    )

    # From CSV: RoomNo
    room_number = models.CharField(max_length=20, blank=True)

    # From CSV: nPriority (Used to sort classes in the UI)
    ui_priority = models.IntegerField(default=0, blank=True, null=True)

    class Meta:
        verbose_name_plural = "School Classes"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ClassTeacherAssignment(models.Model):
    """
    Absorbs tblClassDetails.
    Answers: Who teaches what to whom?
    """

    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Employee, on_delete=models.CASCADE)

    class Meta:
        # A teacher can't be assigned to teach the exact same subject to the same class twice
        unique_together = ["school_class", "subject", "teacher"]
