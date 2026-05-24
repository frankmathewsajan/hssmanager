from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Student, StudentProfile, StudentAcademicRecord


@receiver(post_save, sender=Student)
def handle_student_automation(sender, instance, created, **kwargs):
    """
    Triggers automatically when a Student row is saved.
    Ensures sidecar structural containers are flawlessly bound.
    """
    if created:
        StudentProfile.objects.get_or_create(student=instance)
        StudentAcademicRecord.objects.get_or_create(student=instance)
