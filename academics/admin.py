from django.contrib import admin
from .models import Subject, AcademicGroup, SchoolClass, ClassTeacherAssignment
from billing.models import FeeStructure  # For the inline in AcademicGroupAdmin


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "practical_max_marks",
        "is_practical",
        "is_placeholder",
    )
    list_filter = ("is_practical", "is_placeholder")
    search_fields = ("code", "name")


class FeeStructureInline(admin.StackedInline):
    model = FeeStructure
    can_delete = False
    verbose_name_plural = "Fee Menu (Financial Details)"
    # This matches the OneToOneField in billing/models.py
    fk_name = "academic_group"


@admin.register(AcademicGroup)
class AcademicGroupAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "stream")
    list_filter = ("stream",)
    filter_horizontal = ("core_subjects",)  # The magic UI trick for ManyToMany

    search_fields = ("name", "code")
    inlines = [FeeStructureInline]


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ("name", "academic_year", "academic_group", "class_teacher")
    list_filter = ("academic_year", "academic_group")
    search_fields = ("name",)
    autocomplete_fields = (
        "class_teacher",
        "tutor",
    )  # Prevents UI lag when you have 100+ staff


@admin.register(ClassTeacherAssignment)
class ClassTeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ("school_class", "subject", "teacher")
    list_filter = ("school_class", "subject")
    autocomplete_fields = ("teacher",)
