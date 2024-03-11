from django.contrib import admin
from hsem.models import (User, StudentStatus)
""" from hsem.models import (
    User,
    StudentStatus,
    Bank,
    BusRoute,
    District,
    Community,
    Religion,
    DesignationType,
    AdmissionQuota,
    Medium,
    StudyType,
    Language,
    Caste,
    Occupation,
    Designation,
    School,
    Class,
    Student,
) """



admin.site.register(User)
admin.site.register(StudentStatus)
