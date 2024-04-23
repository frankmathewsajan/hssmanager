from django import forms
from django.core.validators import RegexValidator
from .models import Quota, Group, School, Occupation, Religion, Caste, Bank, Parish, SLang, BusRoutePlace, Gender, Diocese, Community, Designation, District

class NewStudentClassForm(forms.Form):
    IED = forms.CharField(max_length=3, required=False)
    AdYear = forms.CharField(validators=[RegexValidator(regex=r'^\d{4}-\d{2}$', message='Enter a valid year range')])
    AdDate = forms.DateField(input_formats=['%Y-%m-%d'])
    AdNum = forms.IntegerField(validators=[RegexValidator(regex=r'^\d{4,5}$', message='Enter a valid number between 4 and 5 digits')])
    AdBranch = forms.ModelChoiceField(queryset=Group.objects.all(), empty_label=None, to_field_name='code')
    
    AdQuota = forms.ModelChoiceField(queryset=Quota.objects.all(), empty_label=None, to_field_name='pk')
    IEDRemarks = forms.CharField(max_length=100, required=False)
    index = forms.FloatField(min_value=1, max_value=10)

    PrevSchool = forms.ModelChoiceField(queryset=School.objects.all(), empty_label=None, to_field_name='code')
    PrevType = forms.CharField(max_length=2)
    name = forms.CharField(max_length=100)
    dob = forms.DateField(input_formats=['%Y-%m-%d'])
    gender = forms.ModelChoiceField(queryset=Gender.objects.all())
    Religion = forms.ModelChoiceField(queryset=Religion.objects.all())
    Caste = forms.ModelChoiceField(queryset=Caste.objects.all())
    Parish = forms.ModelChoiceField(queryset=Parish.objects.all(), required=False)
    Slang = forms.ModelChoiceField(queryset=SLang.objects.all(), )
    FeePaid = forms.FloatField(min_value=0)
    idm = forms.CharField(max_length=100)
    aadhar = forms.IntegerField(validators=[RegexValidator(regex=r'^\d{12,15}$', message='Enter a valid Aadhar number')])

    bankNo = forms.CharField(max_length=20)
    bankBranch = forms.ModelChoiceField(queryset=Bank.objects.all())
    guardian = forms.BooleanField(required=False)

    FName = forms.CharField(max_length=100)
    FOccupation = forms.ModelChoiceField(queryset=Occupation.objects.all())
    MName = forms.CharField(max_length=100)
    MOccupation = forms.ModelChoiceField(queryset=Occupation.objects.all())
    GName = forms.CharField(max_length=100, required=False)
    GOccupation = forms.ModelChoiceField(queryset=Occupation.objects.all(), initial = 0, required=False)


    PAddress = forms.CharField(widget=forms.Textarea, required=False)
    CAddress = forms.CharField(widget=forms.Textarea, required=False)

    StudentPhone = forms.CharField(max_length=15, validators=[RegexValidator(regex=r'^\d{10,15}$')])
    ParentPhone = forms.CharField(max_length=15, validators=[RegexValidator(regex=r'^\d{10,15}$')])
    AdditionalPhone = forms.CharField(max_length=15, required=False, validators=[RegexValidator(regex=r'^\d{10,15}$')])

    BusRoute = forms.ModelChoiceField(queryset=BusRoutePlace.objects.all())
    RouteRemark = forms.CharField(max_length=100, required=False)
    

    
   

    
    