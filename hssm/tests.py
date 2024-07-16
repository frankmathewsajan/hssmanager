from django.test import TestCase
from .models.primary_models import Group, District

for i in range(2015, 2099):
    print(str(i) + "-" + str(int(str(i)[-2:]) + 1))

import csv
from hssm.models.primary_models import School, Religion  # Import your School model


def import_csv(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            #code,name,district,agu
            School.objects.create(name=row['name'], district=row['district'], agu=row['agu'], code=row['code'])


def import_csv(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file, delimiter="\t")
        for row in reader:
            print(row.keys())
            Religion.objects.create(pk=row['pk'], religion=row['religion'])


import_csv(r"C:\Users\MagnumOpus\OneDrive\Documents\Projects\HSSManagerWeb\data.json\religion.csv")
# Replace 'file_path' with the path to your CSV file
import_csv('path/to/your/csv/file.csv')

import_csv(School, r"C:\Users\MagnumOpus\OneDrive\Documents\Projects\HSSManagerWeb\data.json\schools.csv")


def import_csv(obj, file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Get the district object corresponding to the district code
            o = int(row['district']) if int(row['district']) <= 14 else 0
            district_obj = District.objects.get(id=o)
            print(district_obj, row, list(row.keys()))
            # Create the School object using the district object as foreign key
            obj.objects.create(code=row['code'], name=row[list(row.keys())[0]], district=district_obj, agu=row['agu'])
