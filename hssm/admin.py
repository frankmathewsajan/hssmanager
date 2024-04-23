from django.contrib import admin
from .models import Group, District,Constant, Gender
# Register your models here.

admin.site.register(Group)
admin.site.register(District)
admin.site.register(Constant)
admin.site.register(Gender)