# Generated by Django 5.0.4 on 2024-05-02 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hssm', '0025_alter_student_adbranch'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='GName',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
