from django.db import models

from core.models import Quota, Status
from students.models import Student


class TransferCertificate(models.Model):
    """Only exists if a student has been processed for leaving."""

    # Links back to the students app
    student = models.OneToOneField(
        Student, on_delete=models.CASCADE, related_name="tc_record"
    )

    tc_num = models.IntegerField(null=True, blank=True)
    tc_year = models.CharField(max_length=9, null=True, blank=True)
    tc_date = models.DateField(null=True, blank=True)
    date_of_leaving = models.DateField(null=True, blank=True)
    reason_for_leave = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True)

    class Meta:
        # Ensures we don't accidentally issue two TCs with the same number in a year
        unique_together = ["tc_num", "tc_year"]


class InclusionRecord(models.Model):
    """Tracks IED (Special Needs) data for government quotas."""

    student = models.OneToOneField(
        Student, on_delete=models.CASCADE, related_name="inclusion_data"
    )
    ad_quota = models.ForeignKey(Quota, on_delete=models.RESTRICT)
    is_ied = models.BooleanField(default=False)
    ied_remarks = models.CharField(max_length=255, blank=True)
