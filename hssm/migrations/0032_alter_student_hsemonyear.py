# Generated by Django 5.0.4 on 2024-05-22 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hssm', '0031_alter_student_ied'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='HSEMonYear',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
