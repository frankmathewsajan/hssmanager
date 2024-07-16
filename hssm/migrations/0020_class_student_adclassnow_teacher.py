# Generated by Django 5.0.4 on 2024-04-24 05:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hssm', '0019_alter_student_prevschool'),
    ]

    operations = [
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=2)),
                ('year', models.IntegerField()),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classes', to='hssm.group')),
            ],
        ),
        migrations.AddField(
            model_name='student',
            name='AdClassNow',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='students', to='hssm.class'),
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('subject', models.CharField(max_length=100)),
                ('designation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hssm.designation')),
                ('gender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hssm.gender')),
                ('religion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hssm.religion')),
            ],
        ),
    ]