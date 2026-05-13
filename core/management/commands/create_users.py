from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from staff.models import Employee


class Command(BaseCommand):
    help = "Generates login credentials for all existing employees."

    def handle(self, *args, **kwargs):
        employees = Employee.objects.filter(user__isnull=True)
        count = 0

        for emp in employees:
            # We will use their ShortName (e.g., 'jjs') or StaffID as their username
            username = (emp.short_name or f"staff_{emp.staff_id}").lower()

            # Create the Django User
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password("password123")  # Default password for testing
                user.save()

            # Link it to the Employee
            emp.user = user
            emp.save()
            count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Successfully generated accounts for {count} teachers.")
        )
        self.stdout.write(
            self.style.WARNING("Test Login -> Username: jjs | Password: password123")
        )
