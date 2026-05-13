# billing/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from students.models import Student
from billing.models import StudentInvoice


@receiver(post_save, sender=Student)
def generate_initial_invoice(sender, instance, created, **kwargs):
    """
    Listens for new Student admissions.
    If a new student is created, automatically generate their first invoice.
    """
    if created:  # Only fire on brand new admissions, not everyday profile updates
        # Grab the academic year they were admitted in
        current_year = instance.ad_year

        # Use the class method we built way back in Phase 1!
        StudentInvoice.generate_invoice(student=instance, academic_year=current_year)

        print(f"EVENT TRIGGERED: Auto-generated invoice for {instance.name}")
