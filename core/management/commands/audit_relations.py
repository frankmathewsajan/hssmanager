import csv
import logging
import re
from pathlib import Path

from django.core.management.base import BaseCommand
from django.conf import settings

from students.models import Student
from academics.models import ClassTeacherAssignment, SchoolClass, Subject
from staff.models import Employee


class Command(BaseCommand):
    help = "Deep Relational Integrity Audit: Verifies Foreign Key connections match legacy CSVs."

    def clean_id(self, value):
        if value is None:
            return ""
        return re.sub(r"\.0$", "", str(value).strip())

    def clean_str(self, value):
        return str(value).strip() if value else ""

    def parse_int(self, value):
        try:
            return int(float(str(value).strip()))
        except:
            return None

    def handle(self, *args, **kwargs):
        data_dir = settings.BASE_DIR.parent / "legacy" / "tables"

        self.stdout.write(
            self.style.WARNING("\n--- INITIATING DEEP RELATIONAL AUDIT ---")
        )

        # 1. Audit Student Relationships
        self.audit_students(data_dir / "tblStudent.csv")

        # 2. Audit Teacher Assignments
        self.audit_teacher_assignments(
            data_dir / "tblClassDetails.csv", data_dir / "tblClass.csv"
        )

        self.stdout.write(self.style.SUCCESS("\nRelational Audit Complete!"))

    def audit_students(self, path):
        self.stdout.write(
            "\nAuditing Student Foreign Keys (Identity, Demographics, Profile)..."
        )
        if not path.exists():
            return

        total_checked = 0
        fk_errors = 0

        with open(path, mode="r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                ad_num = self.parse_int(row.get("AdNum"))
                if not ad_num:
                    continue

                student = (
                    Student.objects.filter(ad_num=ad_num)
                    .select_related("gender", "religion", "caste", "profile__bus_route")
                    .first()
                )
                if not student:
                    continue

                total_checked += 1
                errors = []

                # 1. Check Identity (Gender)
                legacy_sex = self.clean_id(row.get("Sex"))
                db_sex = student.gender.legacy_code if student.gender else "UNK"
                if legacy_sex and legacy_sex != db_sex and db_sex != "UNK":
                    errors.append(f"Gender: CSV '{legacy_sex}' vs DB '{db_sex}'")

                # 2. Check Demographics (Religion)
                legacy_rel = self.clean_id(row.get("Religion"))
                db_rel = student.religion.legacy_code if student.religion else "UNK"
                if legacy_rel and legacy_rel != db_rel and db_rel != "UNK":
                    errors.append(f"Religion: CSV '{legacy_rel}' vs DB '{db_rel}'")

                # 3. Check Profile (Bus Route)
                legacy_route = self.clean_id(row.get("BusRoutePlace"))
                try:
                    db_route = (
                        student.profile.bus_route.legacy_code
                        if student.profile.bus_route
                        else ""
                    )

                    # THE FIX: If CSV is '0' (None) and DB is '' (Blank), it's a match!
                    if legacy_route and legacy_route != db_route:
                        if not (legacy_route == "0" and db_route == ""):
                            errors.append(
                                f"Bus Route: CSV '{legacy_route}' vs DB '{db_route}'"
                            )
                except Exception:
                    errors.append("Profile Table missing!")

                if errors:
                    fk_errors += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f"Student {ad_num} Failure: {', '.join(errors)}"
                        )
                    )

        success_rate = (
            ((total_checked - fk_errors) / total_checked) * 100 if total_checked else 0
        )
        self.stdout.write(f"Scanned {total_checked} Students.")

        if fk_errors == 0:
            self.stdout.write(
                self.style.SUCCESS(f"Relational Integrity: 100% PERFECT.")
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"Relational Integrity: {success_rate:.2f}% ({fk_errors} broken links)"
                )
            )

    def audit_teacher_assignments(self, details_path, class_path):
        self.stdout.write("\nAuditing Teacher-Subject-Class Matrix...")
        if not details_path.exists() or not class_path.exists():
            return

        # 1. Map Class IDs to Names
        legacy_class_map = {}
        with open(class_path, mode="r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                legacy_class_map[
                    self.clean_id(row.get("ClassId") or row.get("ClassID"))
                ] = self.clean_str(row.get("ClassName"))

        # 2. Map Subject IDs to ShortNames (Because DB uses ShortName as 'code')
        legacy_subject_map = {}
        sub_path = details_path.parent / "tblOptionalSub.csv"
        with open(sub_path, mode="r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                legacy_subject_map[self.clean_id(row.get("SubjectId"))] = (
                    self.clean_str(row.get("ShortName"))
                )

        total_checked = 0
        fk_errors = 0

        with open(details_path, mode="r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                class_name = legacy_class_map.get(
                    self.clean_id(row.get("ClassID") or row.get("ClassId"))
                )
                sub_code = legacy_subject_map.get(self.clean_id(row.get("SubjectID")))
                t_id = self.parse_int(row.get("TeacherID") or row.get("StaffID"))

                if not class_name or not t_id or not sub_code:
                    continue

                total_checked += 1

                # Query using the Subject code (ShortName) instead of legacy_code
                assignment_exists = ClassTeacherAssignment.objects.filter(
                    school_class__name=class_name,
                    teacher__staff_id=t_id,
                    subject__code=sub_code,
                ).exists()

                if not assignment_exists:
                    fk_errors += 1

        success_rate = (
            ((total_checked - fk_errors) / total_checked) * 100 if total_checked else 0
        )
        self.stdout.write(f"Scanned {total_checked} Teacher Assignments.")

        if fk_errors == 0:
            self.stdout.write(self.style.SUCCESS(f"Matrix Integrity: 100% PERFECT."))
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"Matrix Integrity: {success_rate:.2f}% ({fk_errors} broken links)"
                )
            )
