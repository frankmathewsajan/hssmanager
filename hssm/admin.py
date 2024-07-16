from django.contrib import admin
from django.contrib.auth.models import User, Group as DefaultGroup
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin, GroupAdmin as DefaultGroupAdmin
from django.http import HttpResponseRedirect

from .models.primary_models import Group, Constant, Gender, Subject, Student, Class, Teacher
from .models.secondary_models import District, Client, School
from .views.util import get_client, current_adyear


class SuperUserOnlyAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


admin.site.unregister(User)
admin.site.unregister(DefaultGroup)


class UserAdmin(SuperUserOnlyAdmin, DefaultUserAdmin):
    pass


class GroupAdmin(SuperUserOnlyAdmin, DefaultGroupAdmin):
    pass


admin.site.register(User, UserAdmin)
admin.site.register(DefaultGroup, GroupAdmin)


@admin.register(District)
class DistrictAdmin(SuperUserOnlyAdmin):
    pass


@admin.register(Gender)
class GenderAdmin(SuperUserOnlyAdmin):
    pass


@admin.register(School)
class SchoolAdmin(SuperUserOnlyAdmin):
    pass


@admin.register(Subject)
class SubjectAdmin(SuperUserOnlyAdmin):
    pass


@admin.register(Client)
class ClientAdmin(SuperUserOnlyAdmin):
    pass


class AdYearFilter(admin.SimpleListFilter):
    title = current_adyear()
    parameter_name = 'AdYear'

    def lookups(self, request, model_admin):
        return [(yr, f'{yr} (Current)' if yr == current_adyear() else yr) for yr in current_adyear(True)]

    def queryset(self, request, queryset):
        option_value = self.value() or current_adyear()
        option_value = option_value if len(option_value) == 7 else current_adyear()
        return queryset.filter(AdYear=option_value, client=get_client(request.user))


# Register the Student model without restriction
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    exclude = ["client"]
    list_display = ["id", "AdNum", "AdYear", "name", "dob", "AdClassNow", "gender"]
    list_filter = ["id", "AdNum", "name", "dob", "AdBranch", "AdClassNow", "gender", AdYearFilter]

    def has_change_permission(self, request, obj=None):
        return False

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        student = self.get_object(request, object_id)
        extra_context['student'] = student
        return super().changeform_view(request, object_id, form_url, extra_context)


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    exclude = ["client"]
    list_display = ["id", "group", "year", "code"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(client=get_client(request.user))


@admin.register(Constant)
class ConstantAdmin(admin.ModelAdmin):
    exclude = ["client"]
    list_editable = ["value"]
    list_display = ["name", "value"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(client=get_client(request.user))


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    exclude = ["client"]
    list_display = ["name", "subject", "gender"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(client=get_client(request.user))


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    exclude = ["client"]
    list_editable = ["seats", "fee"]
    list_display = ["group", "fee", "stream", "seats"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(client=get_client(request.user))
