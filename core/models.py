# core/models.py
from django.db import models
from django.utils import timezone
import uuid


class SoftDeleteManager(models.Manager):
    """Custom manager that automatically filters out deleted rows."""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteModel(models.Model):
    """Abstract base class for safe deletions."""

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # The default manager hides deleted items
    objects = SoftDeleteManager()
    # A secondary manager allows admins to see everything
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Override the default delete to perform a soft delete."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Bring the record back from the dead."""
        self.is_deleted = False
        self.deleted_at = None
        self.save()


class School(SoftDeleteModel):
    """The Multi-Tenant Anchor."""

    # We use UUIDs for tenants so competitors can't guess how many schools you have (e.g., School ID 1, 2, 3)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    tenant_code = models.CharField(
        max_length=50, unique=True, help_text="e.g., 'kaliyar'"
    )

    # We can pull from your old tblGeneral later, but this is the core
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name


class TenantAwareModel(SoftDeleteModel):
    """
    Every model that belongs to a specific school will inherit this.
    It combines Soft Deletes with Tenant Tracking.
    """

    # NOTE: null=True temporarily so our 2,500 existing students don't crash the database!
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        abstract = True


class LookupBase(models.Model):
    """An abstract base class for simple dropdown/lookup tables."""

    name = models.CharField(max_length=100, unique=True)

    # NEW: Saves the MS Access ID so the ETL script can link them flawlessly
    legacy_code = models.CharField(max_length=20, unique=True, null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self):
        return self.name


# --- Existing Lookups ---
class Gender(LookupBase):
    pass


class Religion(LookupBase):
    pass


class Community(LookupBase):
    pass


class Quota(LookupBase):
    pass


class SecondLanguage(LookupBase):
    pass


class Occupation(LookupBase):
    pass  # Renamed to fit ParentOccupation CSV


class Caste(LookupBase):
    community = models.ForeignKey(
        Community, on_delete=models.RESTRICT, related_name="castes"
    )


class Parish(LookupBase):
    diocese = models.CharField(max_length=100, blank=True)


class Status(LookupBase):
    code = models.IntegerField(unique=True, help_text="e.g., 0 for Active, 1 for Left")


class Bank(LookupBase):
    ifsc_code = models.CharField(max_length=20, blank=True)


# --- NEW LOOKUPS (From your CSVs) ---
class District(LookupBase):
    pass


class BusRoute(LookupBase):
    pass


class StudyType(LookupBase):
    """Replaces tblStudyType (e.g., SSLC, CBSE)"""

    pass
