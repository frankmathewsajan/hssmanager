from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect,get_object_or_404

from django.db.models import Sum, Q
from .util import get_client, current_adyear, distribute_students
from ..forms import NewStudentClassForm, EditStudentClassForm
from ..models.primary_models import Quota, Group, School, Occupation, Religion, Caste, Bank, Parish, SLang, \
    BusRoutePlace, Gender, Student, Class, Constant, Message
from ..models.secondary_models import Status
from .__init__ import generate_html, staff_form



# Create your views here.

def certificate(request, c):
    certificates = ["conduct_certificate","studying_certificate","identification_certificate"]
    if c in certificates:
        return render(request, f'hssm/certificates/{c}.html',{
            "students":Student.objects.all()
        })
    else:
        request.session['message'] = "Certificate Unavailable"
        request.session['type'] = 'danger'
        return redirect('index')
def report(request, r):
    reports = ["student_list", "student_list_detailed", "student_list_ied", "student_list_practical",
               "student_list_detailed_ph", "student_address_slips", "student_list_id_card",
               "student_list_single_window", "student_list_pta", "student_list_fee_concession", "student_list_kcsl",
               "student_list_fee_detailed","admission_register","namewise_list"]

    if r in reports:

        Slang_ref = {lang_obj.language: lang_obj.language[0] for lang_obj in SLang.objects.all()}
        students = Student.objects.filter(client=get_client(request.user)).order_by("name")

        if r == 'student_list_ied': students = students.filter(IED=1)
        if r == 'student_list_kcsl': students = students.filter(Caste=Caste.objects.get(caste="RCSC"),
                                                                Religion=Religion.objects.get(religion="Christian"))
        total = {}
        if r == 'student_list_fee_detailed':
            p, q = students.aggregate(Sum('FeePaid'))['FeePaid__sum'], students.aggregate(Sum('FeeDue'))['FeeDue__sum']
            print(p,q)
            total = {
                "FeePaid": p,
                "FeeDue": q,
                "Balance": q - p,
            }

        return render(request, f'hssm/reports/{r}.html', {
            "Slang_ref": Slang_ref,
            "students": students,
            "range10": range(1, 11),
            "total":total})
    else:
        request.session['message'] = "Report Unavailable"
        request.session['type'] = 'danger'
        return redirect('index')


@login_required
def assign_classes(request):
    client = get_client(request.user)
    if request.method == 'POST':
        AdYear = request.POST.get('AdYear') or current_adyear()
        _year = int(AdYear[0:4]) + 1
        if Class.objects.filter(year=_year, client=client).exists():
            return JsonResponse({"message": "Classes already assigned for this year"}, status=400)
        students = Student.objects.filter(AdYear=AdYear, client=client)
        groups = Group.objects.filter(client=client)
        SeatsPerClass = int(Constant.objects.get(name='SeatsPerClass', client=client).value)
        next_code = 'A'

        for group in groups:
            group_students = students.filter(AdBranch=group).order_by('-index')
            no_of_classes = int((group.seats) / SeatsPerClass)
            if no_of_classes > 1:
                next_code = distribute_students(group_students, group, no_of_classes, next_code, client=client,
                                                year=_year)
            else:
                new_class = Class.objects.create(code=next_code, year=_year, group=group, client=client)
                for student in group_students:
                    student.AdClassNow = new_class
                    student.save()
                next_code = chr(ord(next_code) + 1)

        return redirect('index')



def chat(request):
    # Get the current user (student)
    # Get the current user (assumed to be a student)
    current_user = request.user
    current_student = Student.objects.get(user=current_user)

    # Get the selected student from the GET request, default to None if not selected
    selected_student_id = request.GET.get('student_id')
    selected_student = None
    messages = []

    if selected_student_id:
        try:
            # Fetch the selected student using the ID
            selected_student = get_object_or_404(Student, id=selected_student_id)

            # Fetch the messages exchanged between the current student and the selected student
            messages = Message.objects.filter(
                (Q(sender=current_student) & Q(receiver=selected_student)) |
                (Q(sender=selected_student) & Q(receiver=current_student))
            ).order_by('timestamp')

        except Student.DoesNotExist:
            # Handle case where selected student does not exist
            selected_student = None
            messages = []

    # Get the list of all students except the current one
    students = Student.objects.exclude(id=current_student.id)

    # Render the chat template, passing in the list of students, selected student, and messages
    return render(request, 'hssm/features/chat.html', {
        'students': students,
        'selected_student': selected_student,
        'messages': messages
    })
def index(request):
    if request.user.is_authenticated:
        if request.user.students.first():
            print("Student")
            return render(request, "hssm/student/index.html")
        else:
            context = {
                "ad_years": current_adyear(True),
                "this_year": current_adyear(),
            }
            if 'message' in request.session:
                context['message'] = request.session.pop('message')
            if 'type' in request.session:
                context['type'] = request.session.pop('type')
            return render(request, "hssm/staff/index.html", context)
    else:
        return render(request, "hssm/welcome.html")


@login_required
def profile(request): return render(request, "hssm/staff/index.html")


@login_required
def settings(request):
    client = get_client(request.user)
    return render(request, "hssm/../../to sort/settings.html", {
        "AdYears": Student.objects.values_list('AdYear', flat=True).distinct().order_by('-AdYear')
        ,
        "n": current_adyear(),
        "school": get_client(request.user).school,
        "constants": Constant.objects.filter(client__id__in=[client.id, '99999']),
        "classes": Class.objects.filter(client=client),
        "branches": Group.objects.filter(client=client)

    })


@login_required
def view(request, adNum, of):
    if of == 'student':
        student = Student.objects.get(AdNum=adNum, client=get_client(request.user))
        return render(request, "hssm/student/view.html", {"student": student})


@login_required
def all(request, of):
    if of == 'students':
        AdYear = request.POST.get('AdYear') or current_adyear()
        order = request.GET.get('order') or 'desc'
        target = request.GET.get('target') or 'AdNum'
        order_by = target if order == 'asc' else f'-{target}'
        branch = request.GET.get('branch')
        if branch:
            students = Student.objects.filter(AdYear=AdYear, client=get_client(request.user),
                                              AdBranch=Group.objects.get(group=branch)).order_by(order_by)
        else:
            students = Student.objects.filter(AdYear=AdYear, client=get_client(request.user)).order_by(order_by)

        print(target, order, order_by, students)
        paginator = Paginator(students, 50)
        page_no = (request.GET.get('page')) or 1

        student_page = paginator.get_page(page_no)
        return render(request, "hssm/student/all.html", {
            "students": student_page,
            "range": paginator.page_range,
            "page_no": int(page_no),
            "AdYears": Student.objects.values_list('AdYear', flat=True).distinct().order_by('-AdYear'),
            "order": 'asc' if order == 'desc' else 'desc',
            "branches": Student.objects.values_list('AdBranch__group', flat=True).distinct().order_by('-AdBranch'),
            "branch": branch
        })


@login_required
def edit(request, adNum, of):
    if of == 'student' and request.method == 'POST':
        return new(request, of, edit=True, adNum=adNum)
    if of == 'student':
        student = Student.objects.get(AdNum=adNum, client=get_client(request.user))
        context = {
            "new": False,
            "quotas": Quota.objects.all(),
            "AdYears": current_adyear(get_list=True),
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
            "student": student,
            "message": "User Info Updated",
            "type": "info"
        }
        return render(request, "hssm/student/data.html", context)


@login_required
def new(request, of, edit=False, adNum=0):
    # import_csv(r"C:\Users\MagnumOpus\OneDrive\Documents\Projects\HSSManagerWeb\data.json\status.csv")
    if of == 'student':
        context = {
            "new": True,
            "quotas": Quota.objects.all(),
            "AdYears": current_adyear(get_list=True),
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

            form = NewStudentClassForm(request.POST) if not edit else EditStudentClassForm(request.POST)
            if form.is_valid() or edit:
                print(form.cleaned_data)
                g = form.cleaned_data['GOccupation']
                if not edit:
                    student = Student(AdNum=form.cleaned_data['AdNum'])
                    context['message'] = "Student added successfully"
                    context['type'] = 'success'

                else:
                    student = Student.objects.get(
                        AdNum=adNum)
                    context['message'] = "Student details updated successfully"
                    context['type'] = 'success'
                try:
                    student.client = get_client(request.user)
                    student.IED = form.cleaned_data['IED']
                    student.AdYear = form.cleaned_data['AdYear']
                    student.AdDate = form.cleaned_data['AdDate']
                    student.AdNum = form.cleaned_data['AdNum'] if not edit else adNum
                    student.AdBranch = form.cleaned_data['AdBranch']
                    student.AdQuota = form.cleaned_data['AdQuota']
                    student.IEDRemarks = form.cleaned_data['IEDRemarks']
                    student.index = form.cleaned_data['index']
                    student.PrevSchool = form.cleaned_data['PrevSchool']
                    student.PrevType = form.cleaned_data['PrevType']
                    student.name = form.cleaned_data['name']
                    student.dob = form.cleaned_data['dob']
                    student.gender = form.cleaned_data['gender']
                    student.Religion = form.cleaned_data['Religion']
                    student.Caste = form.cleaned_data['Caste']
                    student.Parish = form.cleaned_data['Parish']
                    student.Slang = form.cleaned_data['Slang']
                    student.FeeDue = form.cleaned_data['FeeDue']
                    student.FeePaid = form.cleaned_data['FeePaid']
                    student.idm = form.cleaned_data['idm']
                    student.aadhar = form.cleaned_data['aadhar']
                    student.bankNo = form.cleaned_data['bankNo']
                    student.bankBranch = form.cleaned_data['bankBranch']

                    student.FName = form.cleaned_data['FName']
                    student.FOccupation = form.cleaned_data['FOccupation']
                    student.MName = form.cleaned_data['MName']
                    student.MOccupation = form.cleaned_data['MOccupation']
                    student.GName = form.cleaned_data['GName']
                    student.GOccupation = g if g != '...' else Occupation.objects.get(
                        pk=0)
                    student.PAddress = form.cleaned_data['PAddress']
                    student.CAddress = form.cleaned_data['CAddress']
                    student.StudentPhone = form.cleaned_data['StudentPhone']
                    student.ParentPhone = form.cleaned_data['ParentPhone']
                    student.AdditionalPhone = form.cleaned_data['AdditionalPhone']
                    student.BusRoute = form.cleaned_data['BusRoute']
                    student.RouteRemark = form.cleaned_data['RouteRemark']
                    if edit:
                        student.fullAPlus = form.cleaned_data['fullAPlus']
                        student.passedHSE = form.cleaned_data['passedHSE']
                        student.TCDate = form.cleaned_data['TCDate']
                        student.TCNum = form.cleaned_data['TCNum']

                        student.TCYear = form.cleaned_data['TCYear']
                        student.LeavingDate = form.cleaned_data['LeavingDate']
                        student.LeaveReason = form.cleaned_data['LeaveReason']
                        student.CGPA = form.cleaned_data['CGPA']
                        student.StudyStatus = form.cleaned_data['StudyStatus']
                        student.HSEReg = form.cleaned_data['HSEReg']
                        student.HSEMonYear = form.cleaned_data['HSEMonYear']

                    student.save()
                except Exception as e:
                    context['message'] = e
                    context['type'] = 'danger'

            else:
                context['message'] = form.errors
                context['type'] = 'danger'

        if edit:
            return redirect('edit', of=of, adNum=adNum)
        return render(request, "hssm/student/data.html", context)
    elif of == 'staff':
        return render(request, "hssm/staff/data.html",
                      {
                          'body': generate_html(staff_form)
                      })