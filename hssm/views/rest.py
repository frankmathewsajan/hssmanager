from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from hssm.models.primary_models import Student, Constant, Group
from hssm.views.util import get_client


def admission(request, ad_num):
    return JsonResponse({
        "taken": True if Student.objects.filter(AdNum=ad_num, client=get_client(request.user)) else False
    })


@login_required()
def classes(request):
    class_id = request.GET.get('class')
    return JsonResponse({
        'id': class_id
    }, status=200)

@login_required()
def branches(request):
    class_id = request.GET.get('branch')
    return JsonResponse({
        'id': class_id
    }, status=200)


@csrf_exempt
def fees(request, special=0):
    categories = ['PTA Fund', 'Library', 'Other', 'Uniform Boys', 'Uniform Girls']
    category_constants = {constant['name']: int(constant['value']) for constant in
                          Constant.objects.filter(name__in=categories, client=get_client(request.user)).values('name',
                                                                                                               'value')}

    boys_constant = int(category_constants['Uniform Boys'])
    girls_constant = int(category_constants['Uniform Girls'])
    common_constant = sum(
        value for name, value in category_constants.items() if name in categories[:3])

    fees_dict = {"boys": {}, "girls": {}}
    for group in Group.objects.all():
        group_fee = 0 if special == 1 else group.fee
        fees_dict["boys"][group.id] = group_fee + common_constant + boys_constant
        fees_dict["girls"][group.id] = group_fee + \
                                       common_constant + girls_constant
    return JsonResponse(fees_dict, status=200)
