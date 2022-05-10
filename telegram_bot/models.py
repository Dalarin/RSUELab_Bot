from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class TelegramUser(models.Model):
    first_name = models.CharField("Имя", max_length=35)
    last_name = models.CharField("Фамилия", max_length=35)
    email = models.EmailField("Email", max_length=50)
    phone = models.CharField("Телефон", max_length=12)
    group = models.CharField("Группа", max_length=10)
    level = models.IntegerField("Уровень", default=0)
    notice = models.BooleanField("Уведомление", default=True)
    position = models.IntegerField("Позиция", default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    time_message = models.DateTimeField("Время сообщения", blank=True, null=True)
    date_creation = models.DateTimeField("Дата создания", blank=True, null=True)
    # presentation = models.IntegerField("Номер сообщения с презентацией")


class Ban(models.Model):
    id = models.IntegerField(primary_key=True)


class Lesson(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField("Название", max_length=40)
    description = models.TextField("Описание")
    status = models.BooleanField("Статус", default=True)
    date_creation = models.DateTimeField("Дата создания", blank=True, null=True)

class OptionalLesson(models.Model):
    id = models.IntegerField(primary_key=True)
    id_lesson = models.IntegerField('ID урока')
    name = models.CharField("Название", max_length=40)
    description = models.TextField("Описание")
    status = models.BooleanField("Статус", default=True)



class File(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    id_message = models.IntegerField("Номер сообщения с файлом")
    id_chat = models.IntegerField("Номер чата сообщения с файлом")


class Question(models.Model):
    question = models.CharField("Вопрос", max_length=100)
    answers = models.TextField("Ответы")
    right_answer = models.IntegerField("Правильный ответ")


class Test(models.Model):
    id_test = models.IntegerField("Номер теста")  # номер теста
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE)


class FileUser(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    level = models.IntegerField("Номер урока")
    id_message = models.IntegerField("Номер сообщения")


class TestProgress(models.Model):
    id_test = models.IntegerField("ID теста")
    id_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    position = models.IntegerField("Текущий уровень", default=0)
    correct_answer = models.IntegerField("Правильные ответы", default=0)
    incorrect_answer = models.IntegerField("Неправильные ответы", default=0)
    date_start = models.DateTimeField("Время начала")
    date_end = models.DateTimeField("Время конца", blank=True, null=True)
    status = models.BooleanField("Статус", default=True)