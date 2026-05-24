from django.core.management.base import BaseCommand
from core.models import School
from students.models import Student
from staff.models import Employee
from academics.models import SchoolClass, AcademicGroup


class Command(BaseCommand):
    help = "Creates the pioneer school and assigns all legacy data to it."

    def handle(self, *args, **kwargs):
        # 1. Create the Pioneer School
        school, created = School.objects.get_or_create(
            tenant_code="06018", defaults={"name": "Kaliyar Govt. HSS"}
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f"Created Pioneer Tenant: {school.name}")
            )

        # 2. Claim all the data!
        stud_count = Student.objects.filter(school__isnull=True).update(school=school)
        emp_count = Employee.objects.filter(school__isnull=True).update(school=school)
        class_count = SchoolClass.objects.filter(school__isnull=True).update(
            school=school
        )
        group_count = AcademicGroup.objects.filter(school__isnull=True).update(
            school=school
        )

        self.stdout.write(self.style.SUCCESS(f"Claimed {stud_count} Students"))
        self.stdout.write(self.style.SUCCESS(f"Claimed {emp_count} Teachers"))
        self.stdout.write(self.style.SUCCESS(f"Claimed {class_count} Classrooms"))
        self.stdout.write(self.style.SUCCESS(f"Claimed {group_count} Academic Groups"))
        self.stdout.write(
            self.style.WARNING(
                "All legacy data is now safely housed inside the Kaliyar Tenant!"
            )
        )
