# Generated by Django 5.1.3 on 2024-11-25 05:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0003_remove_genre_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='status',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='book',
            name='status',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='genre',
            name='status',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tag',
            name='status',
            field=models.BooleanField(default=False),
        ),
    ]