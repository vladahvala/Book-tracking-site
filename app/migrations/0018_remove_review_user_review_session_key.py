# Generated by Django 5.2 on 2025-04-12 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_review'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='user',
        ),
        migrations.AddField(
            model_name='review',
            name='session_key',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]
