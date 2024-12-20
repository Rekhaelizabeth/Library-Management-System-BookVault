# Generated by Django 5.1.3 on 2024-11-28 18:28

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usermanagement', '0016_alter_bookissuetransaction_due_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookissuetransaction',
            name='due_date',
            field=models.DateField(default=datetime.datetime(2024, 12, 12, 18, 28, 5, 409742, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='bookissuetransaction',
            name='status',
            field=models.CharField(choices=[('ISSUED', 'Issued'), ('RETURNED', 'Returned'), ('LOST', 'Issued'), ('DAMAGED', 'Damaged'), ('REQUESTED', 'Requested')], default='ISSUED', max_length=10),
        ),
    ]
