# Generated by Django 5.1.7 on 2025-04-13 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_app', '0006_quizresult_answers'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='avatar_url',
            field=models.URLField(blank=True, max_length=500),
        ),
    ]
