# Generated by Django 3.1.5 on 2021-04-23 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hoosactive', '0032_profile_receive_notifications'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='email_confirmed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='reset_password',
            field=models.BooleanField(default=False),
        ),
    ]
