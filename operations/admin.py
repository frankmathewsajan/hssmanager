from django.contrib import admin
from .models import TransferCertificate, InclusionRecord


@admin.register(TransferCertificate)
class TransferCertificateAdmin(admin.ModelAdmin):
    list_display = ("tc_num", "tc_year", "student", "tc_date")
    search_fields = ("tc_num", "student__name", "student__ad_num")
    autocomplete_fields = (
        "student",
    )  # Searches the Student table without loading 2500 rows


@admin.register(InclusionRecord)
class InclusionRecordAdmin(admin.ModelAdmin):
    list_display = ("student", "ad_quota", "is_ied")
    list_filter = ("is_ied", "ad_quota")
    search_fields = ("student__name",)
