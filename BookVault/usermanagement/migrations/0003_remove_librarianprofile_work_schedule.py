# Generated by Django 5.1.3 on 2024-11-20 18:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usermanagement', '0002_user_groups_user_is_staff_user_is_superuser_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='librarianprofile',
            name='work_schedule',
        ),
    ]
