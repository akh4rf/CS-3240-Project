# Generated by Django 3.1.7 on 2021-03-28 06:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hoosactive', '0003_auto_20210328_0236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2021, 3, 28, 2, 43, 22, 739338)),
        ),
    ]
