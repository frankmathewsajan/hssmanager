from django.contrib import admin
from .models import Student, StudentProfile


class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = "Profile Data (IDs & Parents)"
    fk_name = "student"


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("ad_num", "name", "class_now", "study_status")

    # The Magic Fix:
    # 'ad_year' filters by the year they joined the school.
    # 'class_now__academic_year' looks inside the SchoolClass model to see if they are 1st/2nd year!
    list_filter = (
        "study_status",
        "class_now",
        "gender",
        "ad_year",
        "class_now__academic_year",
    )

    search_fields = ("name", "ad_num")
    autocomplete_fields = ("ad_class", "class_now")

    inlines = [StudentProfileInline]
