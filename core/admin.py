from django.contrib import admin
from .models import (
    Bank,
    Caste,
    Community,
    Gender,
    Occupation,
    Parish,
    Quota,
    Religion,
    SecondLanguage,
    Status,
    School,
)


# Standard dictionaries registered in bulk
@admin.register(Community, Gender, Occupation, Quota, Religion, SecondLanguage)
class StandardLookupAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


# Custom lookups with extra data
@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    ordering = ("code",)


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ("name", "ifsc_code")
    search_fields = ("name", "ifsc_code")


@admin.register(Parish)
class ParishAdmin(admin.ModelAdmin):
    list_display = ("name", "diocese")
    list_filter = ("diocese",)
    search_fields = ("name",)


@admin.register(Caste)
class CasteAdmin(admin.ModelAdmin):
    list_display = ("name", "community")
    list_filter = ("community",)
    search_fields = ("name",)


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant_code")
    search_fields = ("name", "tenant_code")
