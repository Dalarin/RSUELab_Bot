# Generated by Django 4.0.3 on 2022-03-28 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_bot', '0002_alter_telegramuser_time_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testprogress',
            name='date_end',
            field=models.DateTimeField(null=True, verbose_name='Время конца'),
        ),
    ]