import os
import sys
import django

# Resolve runtime python paths cleanly
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from faker import Faker
from staff.models import Employee, EmployeeFinanceRecord, EmployeeDemographicRecord
from core.models import Gender, Status, School
from staff.models import Designation

fake = Faker("en_IN")


def seed():
    print("Initializing decoupled database seeding pass...")

    school = School.objects.first()
    gender = Gender.objects.first()
    status = Status.objects.first()
    designation = Designation.objects.first()

    if not all([school, gender, status, designation]):
        print("Error: Missing mandatory lookups. Populate lookups first.")
        return

    # Seed 5 Fake Employees
    for i in range(5):
        unique_id = 5000 + i

        # This invocation triggers handle_employee_automation inside signals!
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
        print(f"Created Employee: {emp.name} | Linked Auth User: {account_name}")

    print("Seeding pass completed successfully.")


if __name__ == "__main__":
    seed()
