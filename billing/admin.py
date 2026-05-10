from django.contrib import admin
from .models import FeeStructure, StudentInvoice


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = (
        "academic_group",
        "tuition_fee",
        "tuition_concession",
        "pta_fund",
        "uniform_boys",
        "uniform_girls",
    )
    search_fields = ("academic_group__name",)
    autocomplete_fields = ("academic_group",)


@admin.register(StudentInvoice)
class StudentInvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "academic_year",
        "total_due",
        "total_paid",
        "is_cleared",
        "generated_on",
    )
    list_filter = ("academic_year", "is_cleared")
    search_fields = ("student__name", "student__ad_num")
    autocomplete_fields = ("student",)

    # Invoices are historical ledgers. We shouldn't be editing the 'due' amount manually here.
    readonly_fields = ("generated_on",)
