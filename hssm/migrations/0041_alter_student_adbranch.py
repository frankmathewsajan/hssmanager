# Generated by Django 5.0.4 on 2024-05-23 12:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hssm', '0040_alter_student_index'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='AdBranch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='students', to='hssm.group'),
        ),
    ]
