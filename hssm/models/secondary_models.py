from django.contrib.auth.models import User
from django.db import models


class District(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class School(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    # Aided, Unaided, Govt
    agu = models.CharField(max_length=1)

    def __str__(self):
        return f"{self.code} {self.name} "


class Quota(models.Model):
    quota = models.CharField(max_length=50)

    def __str__(self):
        return self.quota


class Gender(models.Model):
    gender = models.CharField(max_length=50)

    def __str__(self):
        return self.gender


class Designation(models.Model):
    name = models.CharField(max_length=50)

    TYPE_CHOICES = (
        ('Teaching', 'Teaching'),
        ('Non Teaching', 'Non Teaching'),
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    priority = models.IntegerField()

    def __str__(self):
        return f"{self.name}"


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


class Occupation(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Client(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='client')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client', null=True, blank=True)

    def create_admin(self):
        email = f"admin@{self.school.code}.hssm"
        new_username = f"admin@{self.school.code}"
        new_password = f"admin#{self.school.id}"
        if not User.objects.filter(username=new_username).exists():
            user = User.objects.create_user(new_username, email, new_password)
            self.user = user
            self.save(update_fields=['user'])
            print(f'Created Admin Login for {self.school.name} :=> username: {new_username}, password: {new_password}')
        else:
            print(f'Admin user for {self.school.name} already exists: username: {new_username}')

    def create_student_ids(self):
        from .primary_models import Student
        """
        Remember to change the hard coded part
        """
        students = Student.objects.filter(client=self, AdYear="2023-24")
        print(students)
        for student in students:
            yr = student.AdYear[2:4]
            group = student.AdBranch.group
            stream_code = "CSE" if group == "Computer Science" else group[0:3].upper()

            email = f"{yr}{stream_code}{student.AdNum}@{self.school.code}.hssm"
            new_username = f"{yr}{stream_code}{student.AdNum}@{self.school.code}"

            new_password = f"student#{student.id}"
            if not User.objects.filter(username=new_username).exists():
                user = User.objects.create_user(new_username, email, new_password)
                student.user = user
                student.save(update_fields=['user'])
                print(f'{student.name} :=> email: {email}, username: {new_username}, password: {new_password}')
            else:
                print(f'user for {student.name} already exists: username: {new_username}')



    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.user:
            """
            Here self.user implies that create_admin() is not run for the current client.
            """
            self.create_admin()

    def __str__(self):
        return self.school.name
