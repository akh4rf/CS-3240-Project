# Generated by Django 3.1.6 on 2021-04-28 18:29

import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('hoosactive', '0031_auto_20210421_1424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='age',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(4), django.core.validators.MaxValueValidator(125)]),
        ),
        migrations.AlterField(
            model_name='profile',
            name='height_feet',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)]),
        ),
        migrations.AlterField(
            model_name='profile',
            name='height_inches',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(11)]),
        ),
        migrations.AlterField(
            model_name='profile',
            name='weight_lbs',
            field=models.DecimalField(decimal_places=1, max_digits=4, validators=[django.core.validators.MinValueValidator(0.1), django.core.validators.MaxValueValidator(999.9)]),
        ),
        migrations.AlterField(
            model_name='workout',
            name='date',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='workout',
            name='desc',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
