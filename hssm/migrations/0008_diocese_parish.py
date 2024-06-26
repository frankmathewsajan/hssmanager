# Generated by Django 5.0.4 on 2024-04-20 16:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hssm', '0007_religion'),
    ]

    operations = [
        migrations.CreateModel(
            name='Diocese',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('diocese', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Parish',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parish', models.CharField(max_length=100)),
                ('diocese', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hssm.diocese')),
            ],
        ),
    ]
