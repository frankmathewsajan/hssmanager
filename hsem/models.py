from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass


class StudentStatus(models.Model):
    status = models.CharField(max_length=64)
    teacher_status = models.CharField(max_length=64)
    def __str__(self):
        return f'{self.status} - {self.teacher_status}'
    
