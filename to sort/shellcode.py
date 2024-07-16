def generate_random_float(min_value=6.5, max_value=10.0, decimal_places=2):
    random_float = random.uniform(min_value, max_value)
    return round(random_float, decimal_places)


def assign_random_cgpa():
    students = Student.objects.all()
    for student in students:
        student.index = generate_random_float()
        student.save()


def reset_student():
    from hssm.importer import import_csv_to_django;
    import_csv_to_django(r'/hssm/students.csv')

    students = Student.objects.all()
    for student in students:
        student.StudyStatus = Status.objects.get(pk=0)
        student.TCDate = None
        student.TCNum = 0
        student.TCYear = None
        student.fullAPlus = False

        student.passedHSE = False

        student.LeaveReason = Status.objects.get(pk=0)
        student.TCDate = None

        student.save()


def admission_yr():
    students = Student.objects.all()
    for student in students:
        adYear = student.AdDate.year
        student.AdYear = f'{adYear}-{(adYear % 100) + 1}'
        year = student.TCDate.year
        student.TCYear = year
        student.HSEMonYear = f'March {year}'
        student.save()


def modernize_n_years(n=13):
    students = Student.objects.all()
    for student in students:
        try:
            student.AdDate = student.AdDate.replace(year=student.AdDate.year + n)
            student.dob = student.dob.replace(year=student.dob.year + n)
            student.TCDate = student.TCDate.replace(year=student.TCDate.year + n)
            student.LeavingDate = student.LeavingDate.replace(year=student.LeavingDate.year + n)
        except Exception as e:
            print(e)
        finally:
            student.save()


def import_csv(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            print(row.keys())
            # Bank.objects.create(id=row[list(row.keys())[0]], bank_name_with_branch=row['bank_name_with_branch'],
            # ifsc_code=row['ifsc_code']) Occupation.objects.create(id=row[list(row.keys())[0]], name=row['name'])
            # BusRoutePlace.objects.create(id=row[list(row.keys())[0]], place=row['name'])
            Status.objects.create(
                id=row[list(row.keys())[0]], teacher=row['teacher'], student=row['student'])
