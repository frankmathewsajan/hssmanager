import csv
import logging
import re
from pathlib import Path
from datetime import datetime

from django.core.management.base import BaseCommand
from django.conf import settings

# Import all models
from core.models import (
    Gender,
    Religion,
    Community,
    Caste,
    Status,
    Quota,
    Parish,
    SecondLanguage,
    District,
    Bank,
    BusRoute,
    Occupation,
    StudyType,
)
from staff.models import Designation, Employee
from academics.models import SchoolClass, Subject, AcademicGroup
from students.models import Student


class Command(BaseCommand):
    help = "Audits the ETL migration by comparing CSV row counts against the PostgreSQL database."

    def setup_logger(self, log_dir: Path):
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"etl_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logger = logging.getLogger("etl_audit")
        logger.setLevel(logging.INFO)
        if logger.hasHandlers():
            logger.handlers.clear()
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
        return logger, log_file

    def clean_id(self, value):
        if value is None:
            return ""
        return re.sub(r"\.0$", "", str(value).strip())

    def handle(self, *args, **kwargs):
        data_dir = settings.BASE_DIR.parent / "legacy" / "tables"
        log_dir = settings.BASE_DIR.parent / "legacy" / "logs"
        self.logger, log_path = self.setup_logger(log_dir)

        self.stdout.write(self.style.WARNING(f"\n--- INITIATING ETL AUDIT ---"))
        self.stdout.write(f"Detailed missing IDs will be logged to: {log_path}\n")

        # Format: (File Name, Django Model, CSV ID Column, DB ID Column)
        audit_plan = [
            # Core Dictionaries (These have legacy_code)
            ("tblSex.csv", Gender, "SexId", "legacy_code"),
            ("tblReligion.csv", Religion, "RelgId", "legacy_code"),
            ("tblCommunity.csv", Community, "CommunityId", "legacy_code"),
            ("tblCaste.csv", Caste, "CasteId", "legacy_code"),
            ("tblStudentStatus.csv", Status, "StatusId", "legacy_code"),
            ("tblAdmissionQuota.csv", Quota, "QuotaId", "legacy_code"),
            ("tblParish.csv", Parish, "ParishId", "legacy_code"),
            ("tblSLang.csv", SecondLanguage, "SLCode", "legacy_code"),
            ("tblDistricts.csv", District, "txtDistId", "legacy_code"),
            ("tblBank.csv", Bank, "BankID", "legacy_code"),
            ("tblBusRoutePlace.csv", BusRoute, "PlaceId", "legacy_code"),
            ("tblParentOccupation.csv", Occupation, "OccupationId", "legacy_code"),
            ("tblStudyType.csv", StudyType, "StudyTypeId", "legacy_code"),
            # Academics & Staff (Custom Fields)
            (
                "tblDesignation.csv",
                Designation,
                "Name",
                "name",
            ),  # We used Name as the unique key
            (
                "tblOptionalSub.csv",
                Subject,
                "ShortName",
                "code",
            ),  # We mapped ShortName to 'code'
            ("tblGroup.csv", AcademicGroup, "txtCode", "code"),
            # The Main Entities
            ("tblStaff.csv", Employee, "StaffID", "staff_id"),
            ("tblStudent.csv", Student, "AdNum", "ad_num"),
        ]

        # Print Table Header
        self.stdout.write(
            f"{'TABLE / MODEL':<25} | {'CSV ROWS':<10} | {'DB ROWS':<10} | {'MISSING':<10}"
        )
        self.stdout.write("-" * 65)

        total_csv = 0
        total_db = 0
        total_missing = 0

        for filename, model, csv_col, db_col in audit_plan:
            csv_path = data_dir / filename
            if not csv_path.exists():
                self.stdout.write(self.style.ERROR(f"{filename:<25} | FILE NOT FOUND"))
                continue

            # 1. Extract IDs from CSV
            csv_ids = set()
            with open(csv_path, mode="r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    val = self.clean_id(row.get(csv_col))
                    if val:  # Ignore completely empty rows
                        csv_ids.add(val)

            # 2. Extract IDs from Database
            # We convert DB IDs to strings so they map perfectly against CSV strings
            db_ids = set(map(str, model.objects.values_list(db_col, flat=True)))

            # 3. Calculate Discrepancies
            missing_in_db = csv_ids - db_ids

            # 4. Metrics
            csv_count = len(csv_ids)
            db_count = len(db_ids)  # Note: DB might have more due to 'UNK' fallbacks
            missing_count = len(missing_in_db)

            total_csv += csv_count
            total_db += db_count
            total_missing += missing_count

            # 5. Output to Terminal
            if missing_count == 0:
                status = self.style.SUCCESS(f"{missing_count:<10} (PERFECT)")
            else:
                status = self.style.ERROR(f"{missing_count:<10} (DROPPED)")

            model_name = model.__name__
            self.stdout.write(
                f"{model_name:<25} | {csv_count:<10} | {db_count:<10} | {status}"
            )

            # 6. Log specific missing records
            if missing_count > 0:
                self.logger.warning(f"--- {model_name.upper()} ({filename}) ---")
                self.logger.warning(
                    f"Missing {missing_count} rows. CSV IDs not found in DB:"
                )
                # Log them sorted for easy reading
                sorted_missing = sorted(
                    list(missing_in_db), key=lambda x: self.clean_sort(x)
                )
                self.logger.warning(f"{', '.join(sorted_missing)}\n")

        self.stdout.write("-" * 65)
        self.stdout.write(
            self.style.WARNING(
                f"{'TOTALS':<25} | {total_csv:<10} | {total_db:<10} | {total_missing:<10}"
            )
        )
        self.stdout.write(
            self.style.WARNING(
                "\nAudit complete! Check the log file to see exactly which IDs were intentionally dropped (like Julius Ceasor)."
            )
        )

    def clean_sort(self, val):
        """Helper to sort alphanumeric IDs cleanly in the logs"""
        try:
            return float(val)
        except ValueError:
            return val
