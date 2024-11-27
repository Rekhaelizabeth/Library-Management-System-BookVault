# Generated by Django 5.1.3 on 2024-11-27 08:25

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0005_book_available_copies_book_reserved_copies_and_more'),
        ('usermanagement', '0012_alter_bookissuetransaction_due_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookissuetransaction',
            name='due_date',
            field=models.DateField(default=datetime.datetime(2024, 12, 11, 8, 25, 36, 339448, tzinfo=datetime.timezone.utc)),
        ),
        migrations.CreateModel(
            name='Reviews',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField()),
                ('review_text', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='book.book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]