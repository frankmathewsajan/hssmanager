from ninja import Router
from typing import List
from django.db import transaction
from ninja_jwt.authentication import JWTAuth
from django.http import Http404

from .models import SchoolClass, Subject, ClassTeacherAssignment
from students.models import Student
from core.security import check_permission

router = Router(tags=["Academics"], auth=JWTAuth())

@router.get("/classes", response=List[dict])
def list_classes(request):
    """Returns all physical classrooms for the school."""
    user_school = request.auth.employee_profile.school
    return list(SchoolClass.objects.filter(school=user_school).values("id", "name", "academic_year"))

# Future: The 'Allocate Pool to Classes' endpoint we discussed earlier will go exactly here, 
# because it requires manipulating the SchoolClass models heavily.