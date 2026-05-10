from django.contrib import admin
from .models import Designation, ScaleOfPay, Employee


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ("name", "short_name", "is_teaching_staff", "ui_priority")
    list_filter = ("is_teaching_staff",)
    ordering = ("ui_priority",)


@admin.register(ScaleOfPay)
class ScaleOfPayAdmin(admin.ModelAdmin):
    list_display = ("scale_range", "remarks")


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("staff_id", "name", "designation", "mobile_no")
    list_filter = ("designation__is_teaching_staff", "status")
    search_fields = ("name", "staff_id", "pen_no")

    # Critical for academics/admin.py's autocomplete_fields to work
    # Django needs to know what to search for when looking up a teacher
    ordering = ("designation__ui_priority", "name")
