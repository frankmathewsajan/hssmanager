from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass


class StudentStatus(models.Model):
    status = models.CharField(max_length=64)
    teacher_status = models.CharField(max_length=64)

class Bank(models.Model):
    name = models.CharField(max_length=64)
    ifsc = models.CharField(max_length=12)


class Address(models.Model):
    street = models.CharField(max_length=128)
    city = models.CharField(max_length=64)
    state = models.CharField(max_length=64)
    zip_code = models.CharField(max_length=10)

class BusRoute(models.Model): route = models.CharField(max_length=64, unique=True, null=True)
class District(models.Model): district = models.CharField(max_length=64, unique=True, null=True)
class Community(models.Model): community = models.CharField(max_length=64, unique=True, null=True)
class Religion(models.Model): religion = models.CharField(max_length=64, unique=True, null=True)
class DesignationType(models.Model): type = models.CharField(max_length=64)
class AdmissionQuota(models.Model): type = models.CharField(max_length=64, unique=True, null=True)
class Gender(models.Model): gender = models.CharField(max_length=64, unique=True, null=True)
class Medium(models.Model): medium = models.CharField(max_length=64, unique=True, null=True)
class StudyType(models.Model): type = models.CharField(max_length=10, unique=True, null=True)
class Language(models.Model): type = models.CharField(max_length=10, unique=True, null=True)
class Caste(models.Model): caste = models.CharField(max_length=64)
class Occupation(models.Model): caste = models.CharField(max_length=64)


class Designation(models.Model):
    name = models.CharField(max_length=64)
    short_name = models.CharField(max_length=64)
    type = models.ForeignKey(DesignationType, on_delete=models.CASCADE, related_name='designations')

class School(models.Model): 
    name = models.CharField(max_length=64)
    code = models.IntegerField(null=True)
    place = models.CharField(max_length=64)
    phone = models.IntegerField(null=True)
    pin = models.IntegerField(null=True)
    address = models.TextField(null=True)

class Class(models.Model):
    pass

class Student(models.Model):
    ad_num = models.PositiveIntegerField(unique=True, null=True)
    ad_date = models.DateField(null=True)
    ad_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='prev_students', null=True)
    current_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='students', null=True)
    quota = models.ForeignKey(AdmissionQuota, on_delete=models.CASCADE, related_name='students', null=True) 
    app_number = models.PositiveIntegerField(unique=True, null=True)

    name = models.CharField(max_length=50, null=True)
    sex = models.ForeignKey(Gender, on_delete=models.CASCADE, related_name = 'students', null=True)
    dob = models.DateField(null=True)
    index = models.FloatField(null=True)

    prev_study_type = models.ForeignKey(StudyType, on_delete=models.CASCADE, related_name = 'students', null=True)
    prev_medium= models.ForeignKey(Medium, on_delete=models.CASCADE, related_name = 'students', null=True)

    prev_reg_no = models.IntegerField(null=True)
    prev_school = models.ForeignKey(School, on_delete=models.CASCADE, related_name = 'prev_students', null=True)

    second_lang = models.ForeignKey(Language, on_delete=models.CASCADE, related_name = 'students', null=True)
    religion = models.ForeignKey(Religion, on_delete=models.CASCADE, related_name = 'students', null=True)

    caste = models.ForeignKey(Caste, related_name= 'students', on_delete=models.CASCADE, null=True)
    community = models.ForeignKey(Community, related_name= 'students', on_delete=models.CASCADE, null=True)

    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True)
    district = models.ForeignKey(District, related_name = 'students', on_delete=models.CASCADE, null=True)

    pin = models.IntegerField(null=True)
    phone = models.IntegerField(null=True)
    phone_secondary = models.IntegerField(null=True)
    phone_tertiary = models.IntegerField(null=True)

    bus_route = models.ForeignKey(BusRoute, related_name = 'students', on_delete=models.CASCADE, null=True)

    guardian = models.CharField(max_length=50, null=True)
    father = models.CharField(max_length=50, null=True)
    father_occupation = models.ForeignKey(Occupation, on_delete=models.CASCADE, related_name='f_student', null=True)

    mother = models.CharField(max_length=50, null=True)
    mother_occupation = models.ForeignKey(Occupation, on_delete=models.CASCADE, related_name='m_student', null=True)

    remark = models.TextField(null=True)
    identification_mark = models.CharField(max_length=50, null=True)

    status = models.ForeignKey(StudentStatus, related_name = 'students', on_delete=models.CASCADE, null=True)

    pta_offer = models.IntegerField(null=True)
    ad_pta_recieved = models.IntegerField(null=True)

    tc = models.DateField(null=True)
    tc_num = models.IntegerField(null=True)


    leave = models.DateField(null=True)
    leave_remarks = models.TextField(null=True)

    passed_hse = models.BooleanField(null=True)
    hse_reg_no = models.IntegerField(null=True)

    ied = models.BooleanField(null=True)
    ied_remarks = models.TextField(null=True)

    aadhar_no = models.PositiveBigIntegerField(unique = True, null=True)
    acc_no = models.PositiveBigIntegerField(unique = True, null=True)
    bank = models.ForeignKey(Bank, related_name = 'students', on_delete=models.CASCADE, null=True)

    full_a_plus = models.BooleanField(null=True)





