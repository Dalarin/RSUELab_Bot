# Generated by Django 3.2.3 on 2022-04-11 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_bot', '0006_auto_20220411_1830'),
    ]

    operations = [
        migrations.AddField(
            model_name='optionallesson',
            name='id_lesson',
            field=models.IntegerField(default=1, verbose_name='ID урока'),
            preserve_default=False,
        ),
    ]
