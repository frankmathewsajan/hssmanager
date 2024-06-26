# Generated by Django 5.0.4 on 2024-04-06 15:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_name_with_branch', models.CharField(max_length=100)),
                ('ifsc_code', models.CharField(max_length=11, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='BusRoutePlace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('place', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Community',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('community', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Designation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('type', models.CharField(choices=[('Teaching', 'Teaching'), ('Non Teaching', 'Non Teaching')], max_length=20)),
                ('priority', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('district_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Quota',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quota_type', models.CharField(choices=[(1, 'Open Merit'), (2, 'Sports'), (3, 'Disabled'), (4, 'S. C.'), (5, 'S. T.'), (6, 'O. E. C.'), (7, 'O. B. C.'), (8, 'Community Merit'), (9, 'M. Q.'), (10, 'Blind'), (11, 'Special')], max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Caste',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('caste', models.CharField(max_length=100)),
                ('community', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hssm.community')),
            ],
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('agu', models.CharField(max_length=1)),
                ('district', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hssm.district')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('AdYear', models.IntegerField()),
                ('AppNum', models.IntegerField()),
                ('AdNum', models.IntegerField()),
                ('AdmDate', models.DateTimeField()),
                ('AdClass', models.IntegerField()),
                ('ClassNow', models.IntegerField()),
                ('ClassNum', models.IntegerField()),
                ('StudName', models.CharField(max_length=100)),
                ('Sex', models.CharField(max_length=10)),
                ('BirthDate', models.DateField()),
                ('IndexScore', models.FloatField()),
                ('SecStudyType', models.CharField(max_length=100)),
                ('SecRegNum', models.IntegerField()),
                ('PrevSchool', models.CharField(max_length=100)),
                ('SecMedium', models.CharField(max_length=100)),
                ('SLang', models.CharField(max_length=100)),
                ('Religion', models.CharField(max_length=100)),
                ('Catholic', models.BooleanField()),
                ('Parish', models.CharField(max_length=100)),
                ('PmtAddress1', models.TextField()),
                ('PmtAddress2', models.TextField()),
                ('PmtDist', models.CharField(max_length=100)),
                ('PmtPIN', models.IntegerField()),
                ('PmtPhone', models.CharField(max_length=15)),
                ('PstAddress1', models.TextField()),
                ('PstAddress2', models.TextField()),
                ('PstPIN', models.IntegerField()),
                ('PstPhone', models.CharField(max_length=15)),
                ('GuardianName', models.CharField(max_length=100)),
                ('FatherName', models.CharField(max_length=100)),
                ('FOccupation', models.CharField(max_length=100)),
                ('MotherName', models.CharField(max_length=100)),
                ('MOccupation', models.CharField(max_length=100)),
                ('Remarks', models.TextField()),
                ('IdentificationMark', models.TextField()),
                ('StudStatus', models.CharField(max_length=100)),
                ('PTAFundOffer', models.IntegerField()),
                ('PTAPaidAdTime', models.IntegerField()),
                ('TCDate', models.DateTimeField()),
                ('TCNum', models.IntegerField()),
                ('TCYear', models.IntegerField()),
                ('DateofLeaving', models.DateField()),
                ('ReasonforLeave', models.TextField()),
                ('PassedHSE', models.BooleanField()),
                ('HSERegNo', models.IntegerField()),
                ('HSEMonYear', models.CharField(max_length=100)),
                ('IED', models.BooleanField()),
                ('IEDRemarks', models.TextField()),
                ('AdharNo', models.CharField(max_length=12)),
                ('FullAPlus', models.BooleanField()),
                ('AdQuota', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hssm.quota')),
                ('Bank', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hssm.bank')),
                ('BusRoutePlace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hssm.busrouteplace')),
                ('Caste', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hssm.caste')),
                ('PstDist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hssm.district')),
            ],
        ),
    ]
