# Generated by Django 5.0.4 on 2024-04-20 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hssm', '0006_rename_district_name_district_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Religion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('religion', models.CharField(max_length=100)),
            ],
        ),
    ]
