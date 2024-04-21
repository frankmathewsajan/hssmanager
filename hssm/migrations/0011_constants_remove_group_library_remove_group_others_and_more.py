# Generated by Django 5.0.4 on 2024-04-20 19:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hssm', '0010_slang'),
    ]

    operations = [
        migrations.CreateModel(
            name='Constants',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('value', models.CharField(max_length=50)),
            ],
        ),
        migrations.RemoveField(
            model_name='group',
            name='library',
        ),
        migrations.RemoveField(
            model_name='group',
            name='others',
        ),
        migrations.RemoveField(
            model_name='group',
            name='pta_fund',
        ),
        migrations.RemoveField(
            model_name='group',
            name='uniform_boys',
        ),
        migrations.RemoveField(
            model_name='group',
            name='uniform_girls',
        ),
    ]
