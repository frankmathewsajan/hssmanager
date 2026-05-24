# backend/scripts/sanitize.py
from faker import Faker
import random
from students.models import Student, StudentProfile

fake = Faker("en_IN")  # Use Indian locale for realistic names


def sanitize_database():
    print("Starting sanitization...")

    # 1. Sanitize Student Basic Info
    students = Student.objects.all()
    for s in students:
        s.name = fake.name()
        # Keep consistent DOB distribution
        s.dob = fake.date_of_birth(minimum_age=14, maximum_age=18)
        s.save()

    # 2. Sanitize Sidecar Profiles
    profiles = StudentProfile.objects.all()
    for p in profiles:
        # Generate fake 12-digit number
        p.aadhar_number = "".join([str(random.randint(0, 9)) for _ in range(12)])
        p.father_name = fake.name_male()
        p.mother_name = fake.name_female()
        p.pmt_phone = fake.phone_number()
        p.save()

    print("Sanitization complete. Records are now anonymized.")
