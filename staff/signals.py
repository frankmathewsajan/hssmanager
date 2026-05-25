from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import (
    Employee,
    EmployeeServiceRecord,
    EmployeeFinanceRecord,
    EmployeeDemographicRecord,
)


@receiver(post_save, sender=Employee)
def handle_employee_automation(sender, instance, created, **kwargs):
    """
    Triggers automatically when an Employee row is saved.
    Ensures sidecars, user credentials, and dynamic RBAC groups are resolved.
    """
    if created:
        User = get_user_model()
        user_account = instance.user

        # 1. Automate User Account Generation if not explicitly provided
        if not user_account:
            base_slug = instance.name.split()[0].lower() if instance.name else "staff"
            generated_username = f"{base_slug}.{instance.staff_id}"
            generated_email = f"{generated_username}@school.edu"

            if not User.objects.filter(username=generated_username).exists():
                user_account = User.objects.create(
                    username=generated_username,
                    email=generated_email,
                    is_staff=True,
                )
                user_account.set_password("password123")
                user_account.save()

                # Bind back to the main Employee anchor safely without loops
                Employee.objects.filter(id=instance.id).update(user=user_account)
                instance.user = user_account

        # 2. Data-Driven RBAC Allocation (Zero hardcoding)
        if user_account and instance.designation.system_group:
            user_account.groups.add(instance.designation.system_group)

        # 3. Automatically provision the normalized private data zones defensively
        EmployeeServiceRecord.objects.get_or_create(employee=instance)
        EmployeeFinanceRecord.objects.get_or_create(employee=instance)
        EmployeeDemographicRecord.objects.get_or_create(employee=instance)
