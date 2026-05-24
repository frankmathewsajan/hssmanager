# staff/admin.py
from django.contrib import admin
from .models import Designation, ScaleOfPay, Employee


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ("name", "short_name", "is_teaching_staff", "ui_priority")


@admin.register(ScaleOfPay)
class ScaleOfPayAdmin(admin.ModelAdmin):
    list_display = ("scale_range", "remarks")


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    # Match the name exactly here!
    list_display = ("staff_id", "name", "designation", "get_mobile_no")
    list_filter = ("designation__is_teaching_staff", "status")
    search_fields = ("name", "staff_id", "pen_no")

    def get_mobile_no(self, obj):
        # Accessing the sidecar record
        if hasattr(obj, "demographic_record"):
            return obj.demographic_record.phone_no
        return "N/A"

    get_mobile_no.short_description = "Mobile Number"
