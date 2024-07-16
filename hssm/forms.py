import datetime
from django import forms
from .models.primary_models import Student


class EditStudentClassForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class NewStudentClassForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "IED",
            "AdYear",
            "AdDate",
            "AdNum",
            "AdBranch",
            "AdQuota",
            "IEDRemarks",
            "index",
            "PrevSchool",
            "PrevType",
            "name",
            "dob",
            "gender",
            "Religion",
            "Caste",
            "Parish",
            "Slang",
            "FeeDue",
            "FeePaid",
            "idm",
            "aadhar",
            "bankNo",
            "bankBranch",
            "FName",
            "FOccupation",
            "MName",
            "MOccupation",
            "GName",
            "GOccupation",
            "PAddress",
            "CAddress",
            "StudentPhone",
            "ParentPhone",
            "AdditionalPhone",
            "BusRoute",
            "RouteRemark",
        ]

    def clean(self):
        cleaned_data = super().clean()
        # Access cleaned data from the form
        ad_year = cleaned_data.get('AdYear')
        # Perform additional validation or processing here
        # For example, check if the admission year is in the future
        if int(ad_year.split('-')[0]) > datetime.date.today().year:
            raise forms.ValidationError('Admission year cannot be in the future.')

        # You can also perform calculations or data manipulation based on fields
        # cleaned_data['index'] = round(cleaned_data['index'], 2)  # Example: round index to 2 decimal places

        return cleaned_data
