from django.shortcuts import render

from ..models import Quota, Group, School, Occupation, Religion, Community, Caste, Bank, Parish, SLang, BusRoutePlace, Status


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
                #Bank.objects.create(id=row[list(row.keys())[0]], bank_name_with_branch=row['bank_name_with_branch'], ifsc_code=row['ifsc_code'])
                #Occupation.objects.create(id=row[list(row.keys())[0]], name=row['name'])
                #BusRoutePlace.objects.create(id=row[list(row.keys())[0]], place=row['name'])
                Status.objects.create(id=row[list(row.keys())[0]], teacher=row['teacher'], student=row['student'])

def data(request, name):
   
    #import_csv(r"C:\Users\MagnumOpus\OneDrive\Documents\Projects\HSSManagerWeb\data.json\status.csv")

    now = datetime.now().year
    return render(request, "hssm/data.html", {
        "name": name,
        "quotas": Quota.objects.all(),
        "AdYears":[f"{i}-{(i % 100) + 1}" for i in range(now-5, now+5)],
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
    })