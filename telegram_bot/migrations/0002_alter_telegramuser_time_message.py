# Generated by Django 4.0.3 on 2022-03-28 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_bot', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telegramuser',
            name='time_message',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Время сообщения'),
        ),
    ]