# Generated by Django 5.0.4 on 2024-05-23 09:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hssm', '0036_alter_student_feepaid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='guardian',
        ),
    ]
