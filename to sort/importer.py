# import_csv.py

import csv
import os
import django
import re
from datetime import datetime
from hssm.models.primary_models import Student, Group
from hssm.models.secondary_models import Quota, Gender, SLang, Religion, Caste, District, Status

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()


def parse_date_a(date_str):
    return datetime.strptime(date_str, '%m/%d/%Y').date() if date_str.strip() != '' else parse_date_a('3/5/2003')


def parse_date(date_str):
    return datetime.strptime(date_str, '%d-%b-%y').date() if date_str.strip() != '' else parse_date('01-Jan-01')


def parse_date_with_suffix(date_str):
    """
    Parse a date string in the format '31st March 2012' to a datetime.date object.
    """
    # Remove the suffix from the day
    day_with_suffix = date_str.split(' ')[0]
    day = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', day_with_suffix)

    # Reconstruct the date string without the suffix
    date_str_without_suffix = date_str.replace(day_with_suffix, day)

    # Parse the date string to a datetime.date object
    return datetime.strptime(date_str_without_suffix, '%d %B %Y').date() if date_str.strip() != '' else parse_date_with_suffix('31st March 2012')


def import_csv_to_django(filepath):
    with open(filepath, mode='r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        for i, row in enumerate(reader):
            row = dict(row)
            c = str(row['AdClass'].strip())[0] if str(row['AdClass'].strip())[0] != 'C' else 'B'
            try:
                s = Student(
                    AdNum=int(row['AdNum']),
                    AdDate=parse_date(row['AdDate']),
                    AdQuota=Quota.objects.get(pk=1),
                    AdBranch=Group.objects.get(code=c),
                    name=row['name'].strip(),
                    gender=Gender.objects.get(pk=int(float(row['Sex']))),
                    dob=parse_date_a(row['BirthDate']),
                    Slang=SLang.objects.get(language=row['SLang'].strip()),
                    Religion=Religion.objects.get(religion=row['Religion'].strip()),
                    Caste=Caste.objects.get(caste=row['Caste'].strip()),
                    CAddress=row['PmtAddress1'].strip(),
                    PAddress=row['PmtAddress2'].strip(),

                    FName=row['FatherName'].strip(),
                    GName=row['GuardianName'].strip(),
                    StudyStatus=Status.objects.get(pk=1),
                    TCDate=parse_date(row['TCDate']),
                    TCNum=int(row['TCNum']) if row['TCNum'].strip() != '' else 0,
                    TCYear=(int(row['TCYear'][0:4]) + 1) if row['TCYear'].strip() != '' else 2011,
                    LeavingDate=parse_date_with_suffix(row['DateofLeaving'].strip()),
                    LeaveReason=Status.objects.get(pk=1),
                    passedHSE=True if 'TRUE' == row['PassedHSE'].strip() else False,
                    HSEReg=int(row['HSERegNo']) if row['HSERegNo'].strip() != '' else 0,
                    HSEMonYear=row['HSEMonYear'].strip(),
                    IED=True if 'TRUE' == row['IED'].strip() else False,
                    fullAPlus=True if 'TRUE' == row['FullAPlus'].strip() else False

                )
                s.save()
            except Exception as e:
                if str(e) not in 'UNIQUE':
                    print(f"Error at row {i + 1}: {e}")


