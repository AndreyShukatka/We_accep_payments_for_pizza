# Generated by Django 4.1.7 on 2023-03-21 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_bot', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='moltintoken',
            name='token_creation_time',
            field=models.DateTimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='moltintoken',
            name='token_end_time',
            field=models.DateTimeField(blank=True),
        ),
    ]