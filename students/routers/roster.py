# backend/students/routers/roster.py
from ninja import Router
from typing import List

from students.models import Student
from students.schemas import StudentOut
from core.security import check_permission

router = Router()

@router.get("/", response=List[StudentOut])
def list_students(request):
    """Fetch the main student roster for the school."""
    check_permission(request, "students.view_student")
    school_code = request.auth.employee_profile.school.tenant_code
    return Student.objects.select_related("gender", "class_now").filter(
        school__tenant_code=school_code
    )