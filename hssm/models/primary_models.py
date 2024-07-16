from django.contrib.auth.models import User
from django.db import models
from django.db.models import UniqueConstraint, Q

from .secondary_models import Gender, Religion, Occupation, Quota, Caste, Bank, Parish, SLang, BusRoutePlace, Status, \
    Client, School


class Constant(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Subject(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Group(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, default=1)
    group = models.CharField(max_length=50)
    stream = models.CharField(max_length=50, default="Science")
    fee = models.IntegerField(null=True, default=0)
    seats = models.IntegerField(default=0, null=True, blank=True)
    subjects = models.ManyToManyField(Subject, related_name='group')

    def __str__(self):
        return f"{self.group}"


class Teacher(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=100)
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)


class Class(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, default=1)
    code = models.CharField(max_length=2)
    year = models.IntegerField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='classes')
    home_teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='home_teachers', null=True,
                                     blank=True)

    #subject_teachers = models.ManyToManyField(Teacher, related_name='classes')

    def __str__(self):
        return f"{self.code} {self.group} {self.year}"


class Student(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, default=1)
    IED = models.IntegerField(default=0, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    AdYear = models.CharField(max_length=7)
    AdDate = models.DateField()
    AdNum = models.IntegerField(unique=False)
    AdBranch = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, related_name='students')
    AdQuota = models.ForeignKey(Quota, on_delete=models.CASCADE)

    IEDRemarks = models.CharField(max_length=100, blank=True)
    index = models.FloatField(default=1, null=True, blank=True)
    PrevSchool = models.ForeignKey(School, on_delete=models.CASCADE, related_name='prev_school', blank=True, null=True)
    PrevType = models.CharField(max_length=2)
    name = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    Religion = models.ForeignKey(Religion, on_delete=models.CASCADE)
    Caste = models.ForeignKey(Caste, on_delete=models.CASCADE)
    Parish = models.ForeignKey(Parish, on_delete=models.CASCADE, blank=True, null=True)
    Slang = models.ForeignKey(SLang, on_delete=models.CASCADE)
    FeeDue = models.FloatField(null=True, blank=True)
    FeePaid = models.FloatField(default=0, null=True, blank=True)
    idm = models.CharField(max_length=100)
    aadhar = models.BigIntegerField(default=999999999999, null=True, blank=True)
    bankNo = models.CharField(max_length=20)
    bankBranch = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='bank_branch', null=True, blank=True)

    FName = models.CharField(max_length=100)
    FOccupation = models.ForeignKey(Occupation, on_delete=models.CASCADE, related_name='father_occupation', null=True,
                                    blank=True)
    MName = models.CharField(max_length=100)
    MOccupation = models.ForeignKey(Occupation, on_delete=models.CASCADE, related_name='mother_occupation', null=True,
                                    blank=True)
    GName = models.CharField(max_length=100, blank=True, null=True)
    GOccupation = models.ForeignKey(Occupation, on_delete=models.CASCADE, related_name='guardian_occupation',
                                    blank=True, null=True)
    PAddress = models.TextField(blank=True)
    CAddress = models.TextField(blank=True)
    StudentPhone = models.CharField(max_length=15)
    ParentPhone = models.CharField(max_length=15)
    AdditionalPhone = models.CharField(max_length=15, blank=True)
    BusRoute = models.ForeignKey(BusRoutePlace, on_delete=models.CASCADE, related_name='bus_route', null=True)
    RouteRemark = models.CharField(max_length=100, blank=True)

    AdClassNow = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='students', null=True, blank=True)
    fullAPlus = models.IntegerField(default=0, null=True, blank=True)
    TCDate = models.DateField(null=True, blank=True)
    TCNum = models.IntegerField(null=True, blank=True)
    TCYear = models.IntegerField(null=True, blank=True)
    LeavingDate = models.DateField(null=True, blank=True)
    CGPA = models.FloatField(null=True, blank=True)
    LeaveReason = models.ForeignKey(Status, on_delete=models.CASCADE, related_name='reason_for_leaving', null=True,
                                    blank=True)
    StudyStatus = models.ForeignKey(Status, on_delete=models.CASCADE, related_name='study_status', null=True,
                                    blank=True)
    HSEReg = models.CharField(max_length=20, null=True, blank=True)
    HSEMonYear = models.CharField(max_length=20, null=True, blank=True)
    passedHSE = models.IntegerField(default=0, null=True, blank=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                name='unique_adnum_per_client',
                condition=Q(client_id=models.F('client_id')),
                fields=['client', 'AdNum'],
            )
        ]

    def get_year(self):
        ad_year = int(self.AdYear[:4])
        current_year = 2023
        return current_year - ad_year + 1

    def calculate_fees(self):
        fields = ('PTA Fund', "Library", 'Other')
        uniform_field = 'Uniform Boys' if self.gender.gender == 'Male' else 'Uniform Girls'

        constants = {constant.name: int(constant.value) for constant in
                     Constant.objects.filter(name__in=fields + (uniform_field,))}
        e = self.Caste.community.community

        total_fees = sum(constants.values())
        if e not in ('S. C.', 'S. T.', 'O. E. C.'):
            total_fees += self.AdBranch.fee
        self.FeeDue = total_fees

    def save(self, *args, **kwargs):
        self.calculate_fees()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
