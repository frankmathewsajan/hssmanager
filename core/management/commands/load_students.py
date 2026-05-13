import csv
import logging
import re
from pathlib import Path
from datetime import datetime

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction

# Core Lookups
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
from academics.models import SchoolClass
from students.models import Student, StudentProfile, StudentAcademicRecord


class Command(BaseCommand):
    help = "Phase 4 ETL: Bulletproof import into 3NF Student architecture."

    def setup_logger(self, log_dir: Path):
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = (
            log_dir / f"etl_students_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        logger = logging.getLogger("etl_students")
        logger.setLevel(logging.INFO)
        if logger.hasHandlers():
            logger.handlers.clear()
        handler = logging.FileHandler(log_file)
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(handler)
        return logger, log_file

    def clean_id(self, value):
        if value is None:
            return ""
        return re.sub(r"\.0$", "", str(value).strip())

    def clean_str(self, value, max_len=None):
        val = str(value).strip() if value else ""
        if max_len and val:
            return val[:max_len]
        return val

    def clean_aadhar(self, value):
        val = self.clean_str(value).replace(" ", "").replace("-", "")
        return val[:12] if val else None

    def parse_int(self, value, default=None):
        try:
            return int(float(str(value).strip()))
        except (ValueError, TypeError):
            return default

    def parse_float(self, value, default=None):
        try:
            return float(str(value).strip())
        except (ValueError, TypeError):
            return default

    def parse_date(self, value, default="2000-01-01"):
        val = self.clean_str(value)
        if not val:
            return default
        return val.split(" ")[0]

    # --- FALLBACK GENERATORS ---
    def get_fallback(self, model, name="Unknown", **kwargs):
        obj, _ = model.objects.get_or_create(name=name, defaults=kwargs)
        return obj

    def handle(self, *args, **kwargs):
        data_dir = settings.BASE_DIR.parent / "legacy" / "tables"
        log_dir = settings.BASE_DIR.parent / "legacy" / "logs"
        self.logger, log_path = self.setup_logger(log_dir)

        self.stdout.write(self.style.WARNING(f"Phase 4 Started. Logs: {log_path}"))

        # ---------------------------------------------------------
        # 1. LOAD & CACHE DICTIONARIES (using legacy_code)
        # ---------------------------------------------------------
        self.stdout.write("Caching Dictionaries...")
        self.sex_map = self.load_lookup(data_dir / "tblSex.csv", Gender, "SexId", "Sex")
        self.rel_map = self.load_lookup(
            data_dir / "tblReligion.csv", Religion, "RelgId", "Religion"
        )
        self.parish_map = self.load_lookup(
            data_dir / "tblParish.csv", Parish, "ParishId", "ParishName"
        )
        self.quota_map = self.load_lookup(
            data_dir / "tblAdmissionQuota.csv", Quota, "QuotaId", "QuotaType"
        )
        self.slang_map = self.load_lookup(
            data_dir / "tblSLang.csv", SecondLanguage, "SLCode", "SLang"
        )

        self.dist_map = self.load_lookup(
            data_dir / "tblDistricts.csv", District, "txtDistId", "txtDistName"
        )
        self.route_map = self.load_lookup(
            data_dir / "tblBusRoutePlace.csv", BusRoute, "PlaceId", "Place"
        )
        self.occ_map = self.load_lookup(
            data_dir / "tblParentOccupation.csv",
            Occupation,
            "OccupationId",
            "Occupation",
        )
        self.study_map = self.load_lookup(
            data_dir / "tblStudyType.csv", StudyType, "StudyTypeId", "StudyTypeText"
        )

        self.stat_map = self.load_status(data_dir / "tblStudentStatus.csv")
        self.bank_map = self.load_bank(data_dir / "tblBank.csv")

        self.comm_map = self.load_lookup(
            data_dir / "tblCommunity.csv", Community, "CommunityId", "Community"
        )
        self.caste_map = self.load_castes(data_dir / "tblCaste.csv")

        # Fallbacks for dirty data
        self.fb_comm = self.get_fallback(Community, legacy_code="UNK")
        self.fb_caste = self.get_fallback(
            Caste, community=self.fb_comm, legacy_code="UNK"
        )
        self.fb_rel = self.get_fallback(Religion, legacy_code="UNK")
        self.fb_gen = self.get_fallback(Gender, legacy_code="UNK")
        self.fb_quota = self.get_fallback(Quota, name="Open Merit", legacy_code="UNK")
        self.fb_status = self.get_fallback(Status, code=99, legacy_code="UNK")

        # ---------------------------------------------------------
        # 2. THE CLASSROOM BRIDGE
        # ---------------------------------------------------------
        self.class_map = self.build_class_bridge(data_dir / "tblClass.csv")

        # ---------------------------------------------------------
        # 3. POUR THE STUDENTS (The 3NF Split)
        # ---------------------------------------------------------
        self.load_students(data_dir / "tblStudent.csv")

    def load_lookup(self, path, model, id_col, name_col):
        mapping = {}
        if not path.exists():
            return mapping
        with open(path, mode="r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                lid = self.clean_id(row[id_col])
                name = self.clean_str(row[name_col])
                if name:
                    obj, _ = model.objects.update_or_create(
                        name=name, defaults={"legacy_code": lid}
                    )
                    mapping[lid] = obj
        return mapping

    def load_status(self, path):
        mapping = {}
        if not path.exists():
            return mapping
        with open(path, mode="r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                lid = self.clean_id(row["StatusId"])
                obj, _ = Status.objects.update_or_create(
                    name=self.clean_str(row["Status"]),
                    defaults={"code": self.parse_int(lid), "legacy_code": lid},
                )
                mapping[lid] = obj
        return mapping

    def load_bank(self, path):
        mapping = {}
        if not path.exists():
            return mapping
        with open(path, mode="r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                lid = self.clean_id(row["BankID"])
                obj, _ = Bank.objects.update_or_create(
                    name=self.clean_str(row["BankNameWithBranch"]),
                    defaults={
                        "ifsc_code": self.clean_str(row.get("IFSECode")),
                        "legacy_code": lid,
                    },
                )
                mapping[lid] = obj
        return mapping

    def load_castes(self, path):
        mapping = {}
        if not path.exists():
            return mapping
        with open(path, mode="r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                cid = self.clean_id(row["CasteId"])
                obj, _ = Caste.objects.update_or_create(
                    name=self.clean_str(row["Caste"]),
                    defaults={
                        "community": self.comm_map.get(
                            self.clean_id(row["CommunityID"])
                        ),
                        "legacy_code": cid,
                    },
                )
                mapping[cid] = obj
        return mapping

    def build_class_bridge(self, path):
        mapping = {}
        if not path.exists():
            return mapping
        with open(path, mode="r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                cid = self.clean_id(row.get("ClassId") or row.get("ClassID"))
                sc = SchoolClass.objects.filter(
                    name=self.clean_str(row["ClassName"])
                ).first()
                if sc:
                    mapping[cid] = sc
        return mapping

    def load_students(self, path):
        self.stdout.write("Injecting 3NF Students (Resuming & Cleaning)...")
        if not path.exists():
            return

        success, fail = 0, 0
        with open(path, mode="r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                try:
                    ad_num = self.parse_int(row.get("AdNum"))
                    if not ad_num:
                        continue

                    with transaction.atomic():

                        # --- DATA SANITIZATION ---
                        rel_obj = (
                            self.rel_map.get(self.clean_id(row.get("Religion")))
                            or self.fb_rel
                        )
                        parish_obj = self.parish_map.get(
                            self.clean_id(row.get("Parish"))
                        )

                        # Fix the Parish Validation Crash
                        if parish_obj and rel_obj.name not in ["Christian", "Catholic"]:
                            parish_obj = None

                        caste_obj = (
                            self.caste_map.get(self.clean_id(row.get("Caste")))
                            or self.fb_caste
                        )
                        gen_obj = (
                            self.sex_map.get(self.clean_id(row.get("Sex")))
                            or self.fb_gen
                        )
                        quota_obj = (
                            self.quota_map.get(self.clean_id(row.get("AdQuota")))
                            or self.fb_quota
                        )
                        status_obj = (
                            self.stat_map.get(self.clean_id(row.get("StudStatus")))
                            or self.fb_status
                        )

                        # TABLE 1: Student
                        student, _ = Student.objects.update_or_create(
                            ad_num=ad_num,
                            defaults={
                                "app_num": self.parse_int(row.get("AppNum")),
                                "name": self.clean_str(row.get("StudName")),
                                "dob": self.parse_date(row.get("BirthDate")),
                                "gender": gen_obj,
                                "religion": rel_obj,
                                "parish": parish_obj,
                                "caste": caste_obj,
                                "is_catholic": self.clean_str(row.get("Catholic"))
                                == "1",
                                "ad_date": self.parse_date(row.get("AdmDate")),
                                "ad_year": self.clean_str(row.get("AdYear"), max_len=9),
                                "ad_quota": quota_obj,
                                "ad_class": self.class_map.get(
                                    self.clean_id(row.get("AdClass"))
                                ),
                                "class_now": self.class_map.get(
                                    self.clean_id(row.get("ClassNow"))
                                ),
                                "class_roll_num": self.parse_int(row.get("ClassNum")),
                                "second_language": self.slang_map.get(
                                    self.clean_id(row.get("SLang"))
                                ),
                                "study_status": status_obj,
                            },
                        )

                        # TABLE 2: StudentProfile
                        StudentProfile.objects.update_or_create(
                            student=student,
                            defaults={
                                "aadhar_number": self.clean_aadhar(row.get("AdharNo")),
                                "bank": self.bank_map.get(
                                    self.clean_id(row.get("BankBranch"))
                                ),
                                "bank_ac_number": self.clean_str(
                                    row.get("BankAcNumber"), max_len=30
                                ),
                                "father_name": self.clean_str(row.get("FatherName")),
                                "father_occupation": self.occ_map.get(
                                    self.clean_id(row.get("FOccupation"))
                                ),
                                "mother_name": self.clean_str(row.get("MotherName")),
                                "mother_occupation": self.occ_map.get(
                                    self.clean_id(row.get("MOccupation"))
                                ),
                                "guardian_name": self.clean_str(
                                    row.get("GuardianName")
                                ),
                                "pmt_address_1": self.clean_str(row.get("PmtAddress1")),
                                "pmt_address_2": self.clean_str(row.get("PmtAddress2")),
                                "pmt_district": self.dist_map.get(
                                    self.clean_id(row.get("PmtDist"))
                                ),
                                "pmt_pin": self.clean_str(
                                    row.get("PmtPIN"), max_len=10
                                ),
                                "pmt_phone": self.clean_str(
                                    row.get("PmtPhone"), max_len=20
                                ),
                                "pst_address_1": self.clean_str(row.get("PstAddress1")),
                                "pst_address_2": self.clean_str(row.get("PstAddress2")),
                                "pst_district": self.dist_map.get(
                                    self.clean_id(row.get("PstDist"))
                                ),
                                "pst_pin": self.clean_str(
                                    row.get("PstPIN"), max_len=10
                                ),
                                "pst_phone": self.clean_str(
                                    row.get("PstPhone"), max_len=20
                                ),
                                "bus_route": self.route_map.get(
                                    self.clean_id(row.get("BusRoutePlace"))
                                ),
                            },
                        )

                        # TABLE 3: StudentAcademicRecord
                        StudentAcademicRecord.objects.update_or_create(
                            student=student,
                            defaults={
                                "prev_school": self.clean_str(row.get("PrevSchool")),
                                "sec_study_type": self.study_map.get(
                                    self.clean_id(row.get("SecStudyType"))
                                ),
                                "sec_reg_num": self.clean_str(
                                    row.get("SecRegNum"), max_len=50
                                ),
                                "index_score": self.parse_float(row.get("IndexScore")),
                                "tc_date": self.parse_date(
                                    row.get("TCDate"), default=None
                                ),
                                "tc_number": self.clean_str(
                                    row.get("TCNum"), max_len=50
                                ),
                                "reason_for_leave": self.clean_str(
                                    row.get("ReasonforLeave")
                                ),
                                "passed_hse": str(row.get("PassedHSE")).strip().lower()
                                == "true",
                                "hse_reg_no": self.clean_str(
                                    row.get("HSERegNo"), max_len=50
                                ),
                            },
                        )
                    success += 1
                except Exception as e:
                    fail += 1
                    self.logger.error(f"STUDENT FAIL | AdNum {row.get('AdNum')} | {e}")

        self.stdout.write(
            self.style.SUCCESS(f"  -> Final Count: {success} loaded, {fail} failed.")
        )
