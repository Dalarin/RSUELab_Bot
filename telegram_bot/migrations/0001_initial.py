# Generated by Django 4.0.3 on 2022-03-28 12:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ban',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=40, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Описание')),
                ('status', models.BooleanField(default=True, verbose_name='Статус')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=100, verbose_name='Вопрос')),
                ('answers', models.TextField(verbose_name='Ответы')),
                ('right_answer', models.IntegerField(verbose_name='Правильный ответ')),
            ],
        ),
        migrations.CreateModel(
            name='TelegramUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=35, verbose_name='Фамилия')),
                ('last_name', models.CharField(max_length=35, verbose_name='Имя')),
                ('email', models.EmailField(max_length=50, verbose_name='Email')),
                ('phone', models.CharField(max_length=12, verbose_name='Телефон')),
                ('group', models.CharField(max_length=10, verbose_name='Группа')),
                ('level', models.IntegerField(default=0, verbose_name='Уровень')),
                ('notice', models.BooleanField(default=True, verbose_name='Уведомление')),
                ('position', models.IntegerField(default=0, verbose_name='Позиция')),
                ('time_message', models.DateTimeField(verbose_name='Время сообщения')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TestProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_test', models.IntegerField(verbose_name='ID теста')),
                ('position', models.IntegerField(default=0, verbose_name='Текущий уровень')),
                ('correct_answer', models.IntegerField(default=0, verbose_name='Правильные ответы')),
                ('incorrect_answer', models.IntegerField(default=0, verbose_name='Неправильные ответы')),
                ('date_start', models.DateTimeField(verbose_name='Время начала')),
                ('date_end', models.DateTimeField(verbose_name='Время конца')),
                ('status', models.BooleanField(default=True, verbose_name='Статус')),
                ('time_end', models.DateTimeField(blank=True, null=True, verbose_name='Время окончания')),
                ('id_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='telegram_bot.telegramuser')),
            ],
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_test', models.IntegerField(verbose_name='Номер теста')),
                ('question_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='telegram_bot.question')),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_message', models.IntegerField(verbose_name='Номер сообщения с файлом')),
                ('id_chat', models.IntegerField(verbose_name='Номер чата сообщения с файлом')),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='telegram_bot.lesson')),
            ],
        ),
    ]