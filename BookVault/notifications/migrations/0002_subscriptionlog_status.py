# Generated by Django 5.1.3 on 2024-11-24 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptionlog',
            name='status',
            field=models.BooleanField(default=False),
        ),
    ]
