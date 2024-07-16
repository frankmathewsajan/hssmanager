# Generated by Django 5.0.4 on 2024-05-25 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hssm', '0045_client_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='AdNum',
            field=models.IntegerField(),
        ),
        migrations.AddConstraint(
            model_name='student',
            constraint=models.UniqueConstraint(condition=models.Q(('client_id', models.F('client_id'))), fields=('client', 'AdNum'), name='unique_adnum_per_client'),
        ),
    ]