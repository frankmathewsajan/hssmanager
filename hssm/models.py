from typing import Any
from django.db import models


class Quota(models.Model):
    quota = models.CharField(max_length=50)
    def __str__(self):
        return self.quota

class Gender(models.Model):
    gender = models.CharField(max_length=50)
    def __str__(self):
        return self.gender
    
class Constant(models.Model):
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class Group(models.Model):
    code = models.CharField(max_length=1, unique=True)
    group = models.CharField(max_length=50)
    stream = models.CharField(max_length=50, default="Science")
    fee = models.IntegerField(null=True, default=0)
    def __str__(self):
        return f"{self.group} {self.code}"
    
class SLang(models.Model):
    language = models.CharField(max_length=50)
    def __str__(self):
        return self.language
    
class Bank(models.Model):  
    bank_name_with_branch = models.CharField(max_length=100)
    ifsc_code = models.CharField(max_length=11, unique=True)

    def __str__(self):
        return f"{self.ifsc_code} : {self.bank_name_with_branch}" 

class BusRoutePlace(models.Model):
    place = models.CharField(max_length=100)
    def __str__(self):
        return self.place

class Status(models.Model):
    student = models.CharField(max_length=100)
    teacher = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.student} = {self.teacher}"

class Religion(models.Model):
    religion = models.CharField(max_length=100)
    def __str__(self):
        return self.religion


class Diocese(models.Model):
    diocese = models.CharField(max_length=100)
    def __str__(self):
        return self.diocese

class Parish(models.Model):
    parish = models.CharField(max_length=100)
    name = models.CharField(max_length=100, default="...")
    diocese = models.ForeignKey(Diocese, on_delete=models.CASCADE)
    def __str__(self):
        return self.parish
    
class Community(models.Model):
    community = models.CharField(max_length=50)
    def __str__(self):
        return self.community 

class Caste(models.Model):
    caste = models.CharField(max_length=100)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    def __str__(self):
        return self.caste
    

class Designation(models.Model):
    name = models.CharField(max_length=50)

    TYPE_CHOICES = (
        ('Teaching', 'Teaching'),
        ('Non Teaching', 'Non Teaching'),
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    priority = models.IntegerField()

    def __str__(self):
        return f"{self.name} ({self.short_name})"

class District(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Occupation(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name
    

class School(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    agu = models.CharField(max_length=1)
    def __str__(self):
        return f"{self.code} {self.name} "


from django.db import models

class Student(models.Model):
    AdYear = models.IntegerField()
    AppNum = models.IntegerField()
    AdNum = models.IntegerField()
    AdmDate = models.DateTimeField()
    AdQuota = models.ForeignKey(Quota, on_delete=models.CASCADE)
    AdClass = models.IntegerField()
    ClassNow = models.IntegerField()
    ClassNum = models.IntegerField()
    StudName = models.CharField(max_length=100)
    Sex = models.CharField(max_length=10)
    BirthDate = models.DateField()
    IndexScore = models.FloatField()
    SecStudyType = models.CharField(max_length=100)
    SecRegNum = models.IntegerField()
    PrevSchool = models.CharField(max_length=100)
    SecMedium = models.CharField(max_length=100)
    SLang = models.CharField(max_length=100)
    Religion = models.CharField(max_length=100)
    Catholic = models.BooleanField()
    Parish = models.CharField(max_length=100)
    Caste = models.ForeignKey(Caste, on_delete=models.CASCADE)
    PmtAddress1 = models.TextField()
    PmtAddress2 = models.TextField()
    PmtDist = models.CharField(max_length=100)
    PmtPIN = models.IntegerField()
    PmtPhone = models.CharField(max_length=15)
    PstAddress1 = models.TextField()
    PstAddress2 = models.TextField()
    PstDist = models.ForeignKey(District, on_delete=models.CASCADE)
    PstPIN = models.IntegerField()
    PstPhone = models.CharField(max_length=15)
    BusRoutePlace = models.ForeignKey(BusRoutePlace, on_delete=models.CASCADE)
    GuardianName = models.CharField(max_length=100)
    FatherName = models.CharField(max_length=100)
    FOccupation = models.CharField(max_length=100)
    MotherName = models.CharField(max_length=100)
    MOccupation = models.CharField(max_length=100)
    Remarks = models.TextField()
    IdentificationMark = models.TextField()
    StudStatus = models.CharField(max_length=100)
    PTAFundOffer = models.IntegerField()
    PTAPaidAdTime = models.IntegerField()
    TCDate = models.DateTimeField()
    TCNum = models.IntegerField()
    TCYear = models.IntegerField()
    DateofLeaving = models.DateField()
    ReasonforLeave = models.TextField()
    PassedHSE = models.BooleanField()
    HSERegNo = models.IntegerField()
    HSEMonYear = models.CharField(max_length=100)
    IED = models.BooleanField()
    IEDRemarks = models.TextField()
    AdharNo = models.CharField(max_length=12)
    Bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    FullAPlus = models.BooleanField()

    def __str__(self):
        return self.StudName



    


