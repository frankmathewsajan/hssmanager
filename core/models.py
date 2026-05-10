from django.db import models


# 1. THE BLUEPRINT (Abstract Base Class)
class LookupBase(models.Model):
    """
    An abstract base class for simple dropdown/lookup tables.
    Django will NOT create a database table for this specific class.
    """

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        abstract = True  # The magic word that makes it a blueprint
        ordering = ["name"]  # Automatically alphabetizes dropdowns in the UI

    def __str__(self):
        return self.name  # Ensures it says "Catholic" instead of "Religion object (1)"


# 2. THE DICTIONARIES (Inheriting the Blueprint)
class Gender(LookupBase):
    pass  # Inherits 'name' automatically


class Religion(LookupBase):
    pass


class Community(LookupBase):
    pass


class Caste(LookupBase):
    community = models.ForeignKey(
        Community, on_delete=models.RESTRICT, related_name="castes"
    )


class Quota(LookupBase):
    pass


class SecondLanguage(LookupBase):
    pass  # Second Languages (Malayalam, Hindi, etc.)


class Parish(LookupBase):
    diocese = models.CharField(max_length=100, blank=True)


class Occupation(LookupBase):
    pass


# 3. THE EXCEPTIONS (Lookups that need extra fields)
class Bank(LookupBase):
    # Inherits 'name', but adds an extra field for Indian banking
    ifsc_code = models.CharField(max_length=20, blank=True)


class Status(LookupBase):
    # Your father's code used integers (0=Active, 1=TC Issued)
    code = models.IntegerField(unique=True, help_text="e.g., 0 for Active, 1 for Left")
