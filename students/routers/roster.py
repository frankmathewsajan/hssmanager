# backend/students/routers/roster.py
from ninja import Router
from typing import List

from students.models import Student
from students.schemas import StudentOut
from core.security import check_permission

router = Router()

@router.get("/", response=List[StudentOut])
def list_students(request):
    """Fetch the main student roster for the school.
    What it does:
    - Checks if the user has permission to view students.
    - Retrieves all students for the user's school, including related gender and class information for efficient access.
    - Returns a list of students with their details.
    - Note: This endpoint is optimized for the main roster view, so it includes select_related for gender and class_now to minimize database queries when rendering the roster. 
    """
    check_permission(request, "students.view_student")
    school_code = request.auth.employee_profile.school.tenant_code
    return Student.objects.select_related("gender", "class_now").filter(
        school__tenant_code=school_code
    )