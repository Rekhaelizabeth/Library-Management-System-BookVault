# Generated by Django 5.1.3 on 2024-11-25 05:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usermanagement', '0008_memberprofile_subscription'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='status',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='gender',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='status',
            field=models.BooleanField(default=False),
        ),
    ]