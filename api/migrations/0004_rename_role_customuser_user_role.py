# Generated by Django 5.0.4 on 2024-04-27 14:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_remove_customuser_driver_accepted_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='role',
            new_name='user_role',
        ),
    ]
