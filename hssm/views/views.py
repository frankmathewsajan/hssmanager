from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Sum

from ..models import Quota, Group, School, Occupation, Religion, Constant, Caste, Bank, Parish, SLang, BusRoutePlace, Status, Gender, Student
from ..forms import NewStudentClassForm

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



def admission(_, adNum):
    return JsonResponse({"taken": True if Student.objects.get(AdNum=adNum) else False}) 

def view(request, adNum, of):
    return render(request, "hssm/view.html", {"student": Student.objects.get(AdNum=adNum)})
    if of == 'student':
        student = Student.objects.get(AdNum=adNum)
        return render(request, "hssm/view.html", {"student": student})



def all(request, of):
    if of == 'students':
        students = Student.objects.all()
        return render(request, "hssm/all.html", {"students": students})



def edit(request, adNum, of):
    if of == 'student':
        student = Student.objects.get(AdNum=adNum)
        now = datetime.now().year
        context = {
                "new": False,
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
                "gender": Gender.objects.all(),
                "student": student
        }
        return render(request, "hssm/data.html", context)    
        

def new(request, of):

    # import_csv(r"C:\Users\MagnumOpus\OneDrive\Documents\Projects\HSSManagerWeb\data.json\status.csv")
    if of == 'student':
        now = datetime.now().year
        context = {
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
        }
        if request.method == 'POST':
            form = NewStudentClassForm(request.POST)
            if form.is_valid():
                g = form.cleaned_data['GOccupation']
                try:
                    student = Student(
                    IED=form.cleaned_data['IED'],
                    AdYear=form.cleaned_data['AdYear'],
                    AdDate=form.cleaned_data['AdDate'],
                    AdNum=form.cleaned_data['AdNum'],
                    AdBranch=form.cleaned_data['AdBranch'],
                    AdQuota=form.cleaned_data['AdQuota'],
                    IEDRemarks=form.cleaned_data['IEDRemarks'],
                    index=form.cleaned_data['index'],
                    PrevSchool=form.cleaned_data['PrevSchool'],
                    PrevType=form.cleaned_data['PrevType'],
                    name=form.cleaned_data['name'],
                    dob=form.cleaned_data['dob'],
                    gender=form.cleaned_data['gender'],
                    Religion=form.cleaned_data['Religion'],
                    Caste=form.cleaned_data['Caste'],
                    Parish=form.cleaned_data['Parish'],
                    Slang=form.cleaned_data['Slang'],
                    FeePaid=form.cleaned_data['FeePaid'],
                    idm=form.cleaned_data['idm'],
                    aadhar=form.cleaned_data['aadhar'],
                    bankNo=form.cleaned_data['bankNo'],
                    bankBranch=form.cleaned_data['bankBranch'],
                    guardian=form.cleaned_data['guardian'],
                    FName=form.cleaned_data['FName'],
                    FOccupation=form.cleaned_data['FOccupation'],
                    MName=form.cleaned_data['MName'],
                    MOccupation=form.cleaned_data['MOccupation'],
                    GName=form.cleaned_data['GName'],
                    GOccupation=g if g != '...' else Occupation.objects.get(pk=0),
                    PAddress=form.cleaned_data['PAddress'],
                    CAddress=form.cleaned_data['CAddress'],
                    StudentPhone=form.cleaned_data['StudentPhone'],
                    ParentPhone=form.cleaned_data['ParentPhone'],
                    AdditionalPhone=form.cleaned_data['AdditionalPhone'],
                    BusRoute=form.cleaned_data['BusRoute'],
                    RouteRemark=form.cleaned_data['RouteRemark'],
                )
                    student.save()
                    context['message'] = "Student added successfully"
                    context['type'] = 'success'
                except Exception as e:
                    context['message'] = e
                    context['type'] = 'danger'
                
                
                
            else:
                context['message'] = form.errors
                context['type'] = 'danger'
            
        return render(request, "hssm/data.html", context)    
        
