import os
import sys
import django

# Resolve runtime python paths cleanly
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from faker import Faker
from django.contrib.auth.models import Group, Permission
from staff.models import (
    Employee,
    EmployeeFinanceRecord,
    EmployeeDemographicRecord,
    Designation,
)
from core.models import Gender, Status, School

fake = Faker("en_IN")


def seed():
    print("🚀 Running data-driven architecture database seeding pass...")

    school = School.objects.first()
    gender = Gender.objects.first()
    status = Status.objects.first()

    if not all([school, gender, status]):
        print(
            "❌ Error: Missing core system lookups. Populate School, Gender, and Status first."
        )
        return

    # 1. Standardize structural security group creation
    group, _ = Group.objects.get_or_create(name="School Admin")

    try:
        view_perm = Permission.objects.get(
            codename="view_student", content_type__app_label="students"
        )
        add_perm = Permission.objects.get(
            codename="add_student", content_type__app_label="students"
        )
        group.permissions.add(view_perm, add_perm)
    except Permission.DoesNotExist:
        print(
            "⚠️ Warning: Student app permissions not found. Ensure migrations have run completely."
        )

    # 2. Bind the designation directly to the security group
    designation, _ = Designation.objects.get_or_create(
        name="Principal",
        defaults={
            "short_name": "PRIN",
            "is_teaching_staff": True,
            "ui_priority": 1.0,
            "system_group": group,
        },
    )

    # 3. Seed 5 Fake Employees using our strict architecture bounds
    for i in range(5):
        unique_id = 7000 + i

        try:
            emp = Employee.objects.create(
                staff_id=unique_id,
                name=fake.name(),
                gender=gender,
                designation=designation,
                status=status,
                school=school,
            )

            # Safely populate real-world formatting attributes into the signal-created rows
            EmployeeFinanceRecord.objects.filter(employee=emp).update(
                pan_no=fake.bothify(text="?????####?").upper(),
                pen_no=fake.numerify(text="######"),
            )
            EmployeeDemographicRecord.objects.filter(employee=emp).update(
                phone_no=fake.phone_number(), address=fake.address().replace("\n", ", ")
            )

            account_name = emp.user.username if emp.user else "Pending Generation"
            inherited_group = (
                emp.user.groups.first().name
                if emp.user and emp.user.groups.exists()
                else "None"
            )
            print(
                f"✅ Created Employee: {emp.name} | Linked User: {account_name} | Role Group: {inherited_group}"
            )

        except django.db.utils.IntegrityError:
            print(
                f"🚫 Single-Principal Constraint blocked employee entry number {i+1} as expected."
            )

    print("🎉 Seeding pass execution sequence finished.")


if __name__ == "__main__":
    seed()
