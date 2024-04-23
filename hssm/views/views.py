from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Sum

from ..models import Quota, Group, School, Occupation, Religion, Constant, Caste, Bank, Parish, SLang, BusRoutePlace, Status, Gender


from datetime import datetime
import csv
# Create your views here.


def index(request):
    return render(request, "hssm/index.html") if request.user.is_authenticated else render(request, "hssm/welcome.html")


def profile(request): return render(request, "hssm/index.html")


def settings(request): return render(request, "hssm/settings.html")


def import_csv(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            print(row.keys())
            # Bank.objects.create(id=row[list(row.keys())[0]], bank_name_with_branch=row['bank_name_with_branch'], ifsc_code=row['ifsc_code'])
            # Occupation.objects.create(id=row[list(row.keys())[0]], name=row['name'])
            # BusRoutePlace.objects.create(id=row[list(row.keys())[0]], place=row['name'])
            Status.objects.create(
                id=row[list(row.keys())[0]], teacher=row['teacher'], student=row['student'])


@csrf_exempt
def fees(request, special=0):
    categories = ['PTA Fund', 'Library',
                  'Other', 'Uniform Boys', 'Uniform Girls']
    category_constants = {constant['name']: int(constant['value']) for constant in Constant.objects.filter(
        name__in=categories).values('name', 'value')}

    boys_constant = int(category_constants['Uniform Boys'])
    girls_constant = int(category_constants['Uniform Girls'])
    common_constant = sum(
        value for name, value in category_constants.items() if name in categories[:3])

    fees = {"boys": {}, "girls": {}}
    for group in Group.objects.all():

        group_fee = 0 if special == 1 else group.fee
        fees["boys"][group.code] = group_fee + common_constant + boys_constant
        fees["girls"][group.code] = group_fee + \
            common_constant + girls_constant
    return JsonResponse(fees, status=200)


def data(request):

    # import_csv(r"C:\Users\MagnumOpus\OneDrive\Documents\Projects\HSSManagerWeb\data.json\status.csv")

    now = datetime.now().year
    return render(request, "hssm/data.html", {
        "new": True,
        "quotas": Quota.objects.all(),
        "AdYears": [f"{i}-{(i % 100) + 1}" for i in range(now-5, now+5)],
        "branches": Group.objects.all(),
        "schools": School.objects.all(),
        "religions": Religion.objects.all(),
        "castes": Caste.objects.all(),
        "parishes": Parish.objects.all(),
        "slang": SLang.objects.all(),
        "banks": Bank.objects.all(),
        "occupations": Occupation.objects.all(),
        "routes": BusRoutePlace.objects.all(),
        "statuses": Status.objects.all(),
        "gender": Gender.objects.all()
    })
