# Generated by Django 5.0.4 on 2024-04-25 19:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hssm', '0024_student_studystatus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='AdBranch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hssm.group'),
        ),
    ]
