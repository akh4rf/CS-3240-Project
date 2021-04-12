# Generated by Django 3.1.5 on 2021-04-12 01:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hoosactive', '0017_profile_friends'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='city',
            field=models.CharField(default='Charlottesville', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='entry',
            name='username',
            field=models.CharField(default='', max_length=150),
        ),
    ]
