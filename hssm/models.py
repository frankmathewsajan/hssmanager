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


class Student(models.Model):
    IED = models.CharField(max_length=3, blank=True)
    AdYear = models.CharField(max_length=7)
    AdDate = models.DateField()
    AdNum = models.IntegerField(unique=True)
    AdBranch = models.CharField(max_length=1, null=True) 
    AdQuota = models.ForeignKey(Quota, on_delete=models.CASCADE)
    IEDRemarks = models.CharField(max_length=100, blank=True)
    index = models.FloatField()
    PrevSchool = models.ForeignKey(School, on_delete=models.CASCADE, related_name='prev_school')
    PrevType = models.CharField(max_length=2)
    name = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    Religion = models.ForeignKey(Religion, on_delete=models.CASCADE)
    Caste = models.ForeignKey(Caste, on_delete=models.CASCADE)
    Parish = models.ForeignKey(Parish, on_delete=models.CASCADE, blank=True, null=True)
    Slang = models.ForeignKey(SLang, on_delete=models.CASCADE)
    FeePaid = models.FloatField()
    idm = models.CharField(max_length=100)
    aadhar = models.BigIntegerField()
    bankNo = models.CharField(max_length=20)
    bankBranch = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='bank_branch')
    guardian = models.BooleanField()
    FName = models.CharField(max_length=100)
    FOccupation = models.ForeignKey(Occupation, on_delete=models.CASCADE, related_name='father_occupation')
    MName = models.CharField(max_length=100)
    MOccupation = models.ForeignKey(Occupation, on_delete=models.CASCADE, related_name='mother_occupation')
    GName = models.CharField(max_length=100, blank=True)
    GOccupation = models.ForeignKey(Occupation, on_delete=models.CASCADE, related_name='guardian_occupation', blank=True, null=True)
    PAddress = models.TextField(blank=True)
    CAddress = models.TextField(blank=True)
    StudentPhone = models.CharField(max_length=15)
    ParentPhone = models.CharField(max_length=15)
    AdditionalPhone = models.CharField(max_length=15, blank=True)
    BusRoute = models.ForeignKey(BusRoutePlace, on_delete=models.CASCADE, related_name='bus_route', null=True)
    RouteRemark = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name




    


