import csv
import logging
import re
from pathlib import Path
from datetime import datetime

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction

# Model Imports
from core.models import Gender, Religion, Community, Caste, Status, Quota, Parish
from staff.models import Designation, Employee, ScaleOfPay
from academics.models import ClassTeacherAssignment, SchoolClass, Subject, AcademicGroup
from billing.models import FeeStructure


class Command(BaseCommand):
    """
    ETL Pipeline: Migrates legacy school data from CSVs to PostgreSQL.

    Logic Flow:
    1. Lookups (Genders, Religions, etc.)
    2. Hierarchy (Communities -> Castes)
    3. Infrastructure (Designations, Subjects, Academic Groups + Fees)
    4. Personnel (Employees)
    5. School Layout (Subject Mappings -> Classes -> Teacher Assignments)
    """

    help = "Professional ETL Pipeline for HSS Manager"

    def setup_logger(self, log_dir: Path):
        """Initializes file logging for data auditing."""
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"etl_session_{timestamp}.log"

        logger = logging.getLogger("etl_logger")
        logger.setLevel(logging.INFO)
        if logger.hasHandlers():
            logger.handlers.clear()

        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger, log_file

    def clean_id(self, value):
        """Cleans legacy IDs, specifically removing '.0' suffixes from floats."""
        if value is None:
            return ""
        val = str(value).strip()
        return re.sub(r"\.0$", "", val)

    def clean_str(self, value):
        """Trims whitespace and handles nulls."""
        return str(value).strip() if value else ""

    def parse_int(self, value, default=0):
        """Safely casts string/float inputs to integers."""
        try:
            return int(float(str(value).strip()))
        except (ValueError, TypeError):
            return default

    def handle(self, *args, **kwargs):
        # 1. Path Configuration
        data_dir = settings.BASE_DIR.parent / "legacy" / "tables"
        log_dir = settings.BASE_DIR.parent / "legacy" / "logs"
        self.logger, log_path = self.setup_logger(log_dir)

        self.stdout.write(self.style.WARNING(f"ETL Started. Log: {log_path}"))

        # ---------------------------------------------------------
        # PHASE 1: CORE LOOKUPS (Independent)
        # ---------------------------------------------------------
        self.stdout.write("Phasing: Core Lookups...")
        self.sex_map = self.load_generic_lookup(
            data_dir / "tblSex.csv", Gender, "SexId", "Sex"
        )
        self.rel_map = self.load_generic_lookup(
            data_dir / "tblReligion.csv", Religion, "RelgId", "Religion"
        )
        self.comm_map = self.load_generic_lookup(
            data_dir / "tblCommunity.csv", Community, "CommunityId", "Community"
        )
        self.stat_map = self.load_generic_lookup(
            data_dir / "tblStudentStatus.csv", Status, "StatusId", "Status"
        )
        self.quota_map = self.load_generic_lookup(
            data_dir / "tblAdmissionQuota.csv", Quota, "QuotaId", "QuotaType"
        )
        self.parish_map = self.load_generic_lookup(
            data_dir / "tblParish.csv", Parish, "ParishId", "ParishName"
        )
        self.caste_map = self.load_castes(data_dir / "tblCaste.csv")

        # ---------------------------------------------------------
        # PHASE 2: ACADEMIC & STAFF INFRASTRUCTURE
        # ---------------------------------------------------------
        self.stdout.write("Phasing: Infrastructure & Staff...")
        self.desig_map = self.load_designations(data_dir / "tblDesignation.csv")
        self.sub_map = self.load_subjects(data_dir / "tblOptionalSub.csv")
        self.load_academic_groups_and_fees(data_dir / "tblGroup.csv")
        self.load_staff(data_dir / "tblStaff.csv")

        # ---------------------------------------------------------
        # PHASE 3: SCHOOL MAPPING
        # ---------------------------------------------------------
        self.stdout.write("Phasing: School Mapping...")
        self.load_group_subject_links(data_dir / "tblSubjectCombination.csv")
        self.load_school_classes(data_dir / "tblClass.csv")
        self.load_teacher_assignments(data_dir / "tblClassDetails.csv")

        self.stdout.write(self.style.SUCCESS("ETL Pipeline Execution Successful."))

    # -------------------------------------------------------------------------
    # LOADER METHODS
    # -------------------------------------------------------------------------

    def load_generic_lookup(self, path, model, id_col, name_col):
        """Loads simple key-value pairs into a mapping dict."""
        mapping = {}
        if not path.exists():
            return mapping
        with open(path, mode="r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                try:
                    legacy_id = self.clean_id(row[id_col])
                    name = self.clean_str(row[name_col])
                    if name:
                        obj, _ = model.objects.update_or_create(
                            name=name, defaults={"code": legacy_id}
                        )
                        mapping[legacy_id] = obj
                except Exception as e:
                    self.logger.error(f"{model.__name__} FAIL | {e}")
        return mapping

    def load_castes(self, path):
        """Links Castes to Communities."""
        mapping = {}
        if not path.exists():
            return mapping
        with open(path, mode="r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                try:
                    cid = self.clean_id(row["CasteId"])
                    comm_id = self.clean_id(row["CommunityID"])
                    obj, _ = Caste.objects.update_or_create(
                        name=self.clean_str(row["Caste"]),
                        defaults={"community": self.comm_map.get(comm_id), "code": cid},
                    )
                    mapping[cid] = obj
                except Exception as e:
                    self.logger.error(f"CASTE FAIL | {e}")
        return mapping

    def load_designations(self, path):
        """Maps staff roles and Teaching/Non-Teaching status."""
        mapping = {}
        if not path.exists():
            return mapping
        with open(path, mode="r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                try:
                    lid = self.clean_id(row["ID"])
                    obj, _ = Designation.objects.update_or_create(
                        name=self.clean_str(row["Name"]),
                        defaults={
                            "short_name": self.clean_str(row["ShortName"]),
                            "is_teaching_staff": self.clean_str(row["Type"])
                            == "Teaching",
                            "ui_priority": float(row.get("Priority") or 0.0),
                        },
                    )
                    mapping[lid] = obj
                except Exception as e:
                    self.logger.error(f"DESIG FAIL | {e}")
        return mapping

    def load_subjects(self, path):
        """Standardizes subject definitions."""
        mapping = {}
        if not path.exists():
            return mapping
        with open(path, mode="r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                try:
                    lid = self.clean_id(row["SubjectId"])
                    obj, _ = Subject.objects.update_or_create(
                        code=self.clean_str(row["ShortName"]),
                        defaults={
                            "name": self.clean_str(row["SubName"]),
                            "is_practical": self.clean_str(row["PE"]).lower() == "true",
                            "practical_max_marks": self.parse_int(row.get("EXMaxPE")),
                        },
                    )
                    mapping[lid] = obj
                except Exception as e:
                    self.logger.error(f"SUBJECT FAIL | {e}")
        return mapping

    def load_academic_groups_and_fees(self, path):
        """Loads both curriculum groups and their financial fee menus."""
        if not path.exists():
            return
        with open(path, mode="r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                try:
                    with transaction.atomic():
                        group, _ = AcademicGroup.objects.update_or_create(
                            code=self.clean_str(row["txtCode"]),
                            defaults={
                                "name": self.clean_str(row["txtGroup"]),
                                "stream": self.clean_str(row["txtStream"]),
                            },
                        )
                        FeeStructure.objects.update_or_create(
                            academic_group=group,
                            defaults={
                                "tuition_fee": self.parse_int(row.get("Fee")),
                                "tuition_concession": self.parse_int(
                                    row.get("FeeSCSTOEC")
                                ),
                                "pta_fund": self.parse_int(row.get("PTA")),
                                "other_fees": self.parse_int(row.get("Other")),
                                "library_fee": self.parse_int(row.get("Library")),
                                "uniform_boys": self.parse_int(row.get("Uniform_Boys")),
                                "uniform_girls": self.parse_int(
                                    row.get("Uniform_Girls")
                                ),
                            },
                        )
                except Exception as e:
                    self.logger.error(f"GROUP/FEE FAIL | {e}")

    def load_staff(self, path):
        """Imports the master Employee list."""
        if not path.exists():
            return
        success, fail = 0, 0
        with open(path, mode="r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                try:
                    sid = self.clean_id(row.get("StaffID"))
                    if not sid or row.get("Name") == "Julius Ceasor":
                        continue

                    with transaction.atomic():
                        Employee.objects.update_or_create(
                            staff_id=int(sid),
                            defaults={
                                "name": self.clean_str(row["Name"]),
                                "short_name": self.clean_str(row["ShortName"]),
                                "gender": self.sex_map.get(self.clean_id(row["Sex"])),
                                "designation": self.desig_map.get(
                                    self.clean_id(row["Designation"])
                                ),
                                "religion": self.rel_map.get(
                                    self.clean_id(row["Religion"])
                                ),
                                "caste": self.caste_map.get(
                                    self.clean_id(row["Caste"])
                                ),
                                "parish": self.parish_map.get(
                                    self.clean_id(row["Parish"])
                                ),
                                "status": self.stat_map.get(
                                    self.clean_id(row["Status"])
                                ),
                                "primary_subject": self.sub_map.get(
                                    self.clean_id(row["Subject"])
                                ),
                                "dob": (
                                    self.clean_str(row["DOB"]).split(" ")[0]
                                    if row["DOB"]
                                    else None
                                ),
                                "mobile_no": self.clean_str(row["MobileNo"]),
                                "address": self.clean_str(row["Address"]),
                                "basic_salary": self.parse_int(row.get("Basic")),
                                "pan_no": self.clean_str(row["PANNo"]),
                                "pen_no": self.clean_str(row["PENNo"]),
                                "election_id_no": self.clean_str(row["ElectionIDNo"]),
                            },
                        )
                    success += 1
                except Exception as e:
                    fail += 1
                    self.logger.error(f"STAFF FAIL ID {sid} | {e}")
        self.stdout.write(
            self.style.SUCCESS(f"  -> Staff: {success} loaded, {fail} failed.")
        )

    def load_group_subject_links(self, path):
        """Populates the Many-to-Many core subjects for each stream."""
        if not path.exists():
            return
        with open(path, mode="r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                try:
                    group = AcademicGroup.objects.filter(
                        code=self.clean_str(row.get("txtGroupCode") or row.get("Group"))
                    ).first()
                    subject = self.sub_map.get(self.clean_id(row["SubjectID"]))
                    if group and subject:
                        group.core_subjects.add(subject)
                except Exception as e:
                    self.logger.error(f"M2M LINK FAIL | {e}")

    def load_school_classes(self, path):
        """Builds the actual Classrooms and saves them to a memory map for the next step."""
        self.stdout.write("Loading School Classes...")
        self.class_map = {}  # We must save this map for the assignments!
        if not path.exists():
            return

        success, fail = 0, 0
        with open(path, mode="r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                try:
                    c_id = self.clean_id(row.get("ClassId") or row.get("ClassID"))
                    raw_year = self.clean_str(row.get("xYear") or row.get("nYear"))
                    acad_year = 1 if "1" in raw_year else 2

                    sc, _ = SchoolClass.objects.update_or_create(
                        name=self.clean_str(row["ClassName"]),
                        defaults={
                            "academic_year": acad_year,
                            "academic_group": AcademicGroup.objects.filter(
                                code=self.clean_str(row.get("Group"))
                            ).first(),
                            "class_teacher": Employee.objects.filter(
                                staff_id=self.parse_int(row.get("ClassTeacher"))
                            ).first(),
                            "tutor": Employee.objects.filter(
                                staff_id=self.parse_int(row.get("Tutor"))
                            ).first(),
                            "room_number": self.clean_id(row.get("RoomNo")),
                            "ui_priority": self.parse_int(row.get("nPriority")),
                        },
                    )
                    self.class_map[c_id] = sc  # Save the ID mapping (e.g., '2' -> A1)
                    success += 1
                except Exception as e:
                    fail += 1
                    self.logger.error(f"CLASS FAIL | {row.get('ClassName')} | {e}")

        self.stdout.write(
            self.style.SUCCESS(f"  -> Classes: {success} loaded, {fail} failed.")
        )

    def load_teacher_assignments(self, path):
        """The final curriculum map: Teachers + Subjects + Rooms."""
        self.stdout.write("Loading Teacher Assignments...")
        if not path.exists():
            return

        success, fail = 0, 0
        with open(path, mode="r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                try:
                    # Look up by ID, not Name!
                    c_id = self.clean_id(row.get("ClassID") or row.get("ClassId"))
                    sub_id = self.clean_id(row.get("SubjectID"))
                    t_id = self.clean_id(row.get("TeacherID") or row.get("StaffID"))

                    # Pull from the memory maps
                    t_class = getattr(self, "class_map", {}).get(c_id)
                    subject = self.sub_map.get(sub_id)
                    teacher = Employee.objects.filter(
                        staff_id=self.parse_int(t_id)
                    ).first()

                    if t_class and subject and teacher:
                        ClassTeacherAssignment.objects.update_or_create(
                            school_class=t_class, subject=subject, teacher=teacher
                        )
                        success += 1
                    else:
                        raise ValueError(
                            f"Missing Link: Class={t_class}, Sub={subject}, Teacher={teacher}"
                        )

                except Exception as e:
                    fail += 1
                    self.logger.error(f"ASSIGNMENT FAIL | {e}")

        # NOW the terminal will tell you the truth!
        if fail > 0:
            self.stdout.write(
                self.style.ERROR(
                    f"  -> Assignments: {success} loaded, {fail} FAILED. Check Logs!"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"  -> Assignments: {success} loaded, {fail} failed."
                )
            )

    def load_teacher_assignments(self, path):
        """The final curriculum map: Teachers + Subjects + Rooms."""
        self.stdout.write("Loading Teacher Assignments...")
        if not path.exists():
            return

        success, fail = 0, 0
        with open(path, mode="r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                try:
                    # Look up by ID, not Name!
                    c_id = self.clean_id(row.get("ClassID") or row.get("ClassId"))
                    sub_id = self.clean_id(row.get("SubjectID"))
                    t_id = self.clean_id(row.get("TeacherID") or row.get("StaffID"))

                    # Pull from the memory maps
                    t_class = getattr(self, "class_map", {}).get(c_id)
                    subject = self.sub_map.get(sub_id)
                    teacher = Employee.objects.filter(
                        staff_id=self.parse_int(t_id)
                    ).first()

                    if t_class and subject and teacher:
                        ClassTeacherAssignment.objects.update_or_create(
                            school_class=t_class, subject=subject, teacher=teacher
                        )
                        success += 1
                    else:
                        raise ValueError(
                            f"Missing Link: Class={t_class}, Sub={subject}, Teacher={teacher}"
                        )

                except Exception as e:
                    fail += 1
                    self.logger.error(f"ASSIGNMENT FAIL | {e}")

        # NOW the terminal will tell you the truth!
        if fail > 0:
            self.stdout.write(
                self.style.ERROR(
                    f"  -> Assignments: {success} loaded, {fail} FAILED. Check Logs!"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"  -> Assignments: {success} loaded, {fail} failed."
                )
            )
