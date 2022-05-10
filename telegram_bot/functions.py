import json
import re
from django.db.models import Avg
import telebot
from django.utils import timezone
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, \
    KeyboardButtonPollType
from django.conf import settings

from telegram_bot.models import Question, Lesson, File, TestProgress, Test, TelegramUser, FileUser, OptionalLesson

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)


# команды
def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"


def adminka(**kwargs):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("Создать урок", callback_data='create_course'),
                InlineKeyboardButton('Создать дополнительный урок', callback_data='create_optional_course_set'),
               InlineKeyboardButton("Сохранить файл", callback_data='save_file'),
               InlineKeyboardButton('Сохранить файл для доп.урока', callback_data='save_file_optional'),
               InlineKeyboardButton("Добавить файл в урок", callback_data='set_teo_course'),
               InlineKeyboardButton('Добавить файл в доп.урок', callback_data='set_teo_course_optional'),
               InlineKeyboardButton("Сохранить вопрос", callback_data='save_question'),
               InlineKeyboardButton("Добавить вопрос к тесту", callback_data='set_qw_test'),
               InlineKeyboardButton('Добавить вопрос к тесту доп.урока', callback_data='set_qw_test_optional'),
               InlineKeyboardButton("Изменить статус урока", callback_data='active_course'),
               InlineKeyboardButton('Инструкция', callback_data='instruction'),
               InlineKeyboardButton('Сформировать отчет', callback_data='get_report'),
               InlineKeyboardButton('Получить все презентации', callback_data='get_all_presentations'),
               InlineKeyboardButton('Получить презентацию по фамилии', callback_data='get_presentations_by_lastname'),
               InlineKeyboardButton('Получить конспект доп. урока по фамилии', callback_data='get_summary_optional_set'),
               InlineKeyboardButton('Получить конспект урока по фамилии', callback_data='get_summary_set'),
               InlineKeyboardButton('Обновить информацию', callback_data='update_info'),
               InlineKeyboardButton('Сделать объявление', callback_data='make_notification_set'),
               InlineKeyboardButton("Уведомить неактивных пользователей",
                                    callback_data='notify_users'),
               )

    bot.send_message(kwargs['id'], "Команды администратора:", reply_markup=markup)


# положения по позици

def make_notification_set(**kwargs):
    kwargs['user'].position = 9
    kwargs['user'].save()
    bot.send_message(kwargs['id'], 'Отправьте сообщение для объявления')


def make_notification(**kwargs):
    kwargs['user'].position = 4
    kwargs['user'].save()
    users = TelegramUser.objects.filter(notice=True)
    for user in users:
        bot.send_message(user.id, f'Администратор сделал объявление:\n{kwargs["message"]}')
    bot.send_message(kwargs['id'], f'Количество уведомленных пользователей: {len(users)}')

def get_summary_set(**kwargs):
    kwargs['user'].position = 8
    kwargs['user'].save()
    bot.send_message(kwargs['id'], 'Отправьте имя и фамилию пользователя и название урока в формате (Имя пользователя Фамилия пользователя;Название урока)')

def get_summary_optional_set(**kwargs):
    kwargs['user'].position = 11
    kwargs['user'].save()
    bot.send_message(kwargs['id'], 'Отправьте имя и фамилию пользователя и название урока в формате (Имя пользователя Фамилия пользователя;Название урока)')


def get_summary(**kwargs):
    try:
        kwargs['user'].position = 4
        kwargs['user'].save()
        lesson_model = Lesson.objects.get(name=kwargs['message'].split(';')[1].strip())
        user = TelegramUser.objects.get(first_name=kwargs['message'].split(';')[0].split()[0].strip(), last_name=kwargs['message'].split(';')[0].split()[1].strip())
        summary = FileUser.objects.get(user=user, level=lesson_model.id)
        bot.send_message(kwargs['id'], f'Конспект пользователя {user.last_name} {user.first_name} по уроку {lesson_model.name}')
        bot.copy_message(kwargs['id'], user.id, summary.id_message)
    except Lesson.DoesNotExist:
        bot.send_message(kwargs['id'], 'Урок с таким названием не найден')
    except TelegramUser.DoesNotExist:
        bot.send_message(kwargs['id'], 'Пользователь не найден')
    except:
        bot.send_message(kwargs['id'], 'Что то не так')

def get_summary_optional(**kwargs):
    try:
        kwargs['user'].position = 4
        kwargs['user'].save()
        lesson_model = OptionalLesson.objects.get(name=kwargs['message'].split(';')[1].strip())
        user = TelegramUser.objects.get(first_name=kwargs['message'].split(';')[0].split()[0].strip(), last_name=kwargs['message'].split(';')[0].split()[1].strip())
        summary = FileUser.objects.get(user=user, level=-100-lesson_model.id_lesson)
        bot.send_message(kwargs['id'], f'Конспект пользователя {user.last_name} {user.first_name} по уроку {lesson_model.name}')
        bot.copy_message(kwargs['id'], user.id, summary.id_message)
    except OptionalLesson.DoesNotExist:
        bot.send_message(kwargs['id'], 'Такого урока не существует')
    except TelegramUser.DoesNotExist:
        bot.send_message(kwargs['id'], 'Такого пользователя не существует')
    except Exception as e:
        bot.send_message(kwargs['id'], 'Что то не так')



def get_back(**kwargs):
    if kwargs['user'].position < 0 or kwargs['user'].position == 4:
        kwargs['user'].position = 4
        kwargs['user'].save()
        bot.send_message(kwargs['id'], 'Вы вернулись в основное меню', reply_markup=menu_keyboard(kwargs['user']))


def pass_test(**kwargs):
    test = Test.objects.filter(id_test=kwargs['user'].level)

    if TestProgress.objects.filter(id_test=test[0].id_test, id_user=kwargs['user'], status=False).exists():
        a = TestProgress.objects.filter(id_test=test[0].id_test, id_user=kwargs['user'], status=False)
        for i in a:
            if i.date_end > timezone.now() - timezone.timedelta(1):
                bot.send_message(kwargs['id'], 'Еще не прошли сутки с того момента как вы завалили тест')
                return None
    if not FileUser.objects.filter(user=kwargs['user'], level=kwargs['user'].level).exists():
        bot.send_message(kwargs['id'], 'Вы не прикрепили конспект к уроку, пройти тест невозможно')
        return None
    if not TestProgress.objects.filter(id_test=test[0].id_test, id_user=kwargs['user'], status=True).exists():
        TestProgress(id_user=kwargs['user'], id_test=test[0].id_test, date_start=timezone.now()).save()
    progress = TestProgress.objects.get(id_test=test[0].id_test, id_user=kwargs['user'], status=True)
    if progress.position < test.count():
        questions = test[progress.position].question_id
        bot.send_poll(kwargs['id'], questions.question, json.loads(questions.answers), type='quiz',
                      correct_option_id=questions.right_answer, is_anonymous=False, protect_content=False)
    else:
        progress.date_end = timezone.now()
        progress.status = False
        progress.save()

        if progress.correct_answer / test.count() >= 0.5:
            kwargs['user'].level += 1
            kwargs['user'].save()
            bot.send_message(kwargs['id'],
                             f'Тест завершен.\nКоличество правильных ответов: {progress.correct_answer}\nПроцент прохождения теста: {toFixed((progress.correct_answer / test.count()) * 100, 2)} %',
                             reply_markup=menu_keyboard(kwargs['user']))
            if kwargs['user'].level - 1 == 7:
                bot.send_message(kwargs['id'], 'Вы дошли до контрольной точки. Проверьте и обновите свою презентацию')
        else:
            bot.send_message(kwargs['id'], 'Пороговое значение не набрано. Тест провален.',
                             reply_markup=menu_keyboard(kwargs['user']))


def check_answer(**kwargs):
    test = Test.objects.filter(id_test=kwargs['user'].level)
    progress = TestProgress.objects.get(id_test=test[0].id_test, id_user=kwargs['user'], status=True)
    questions = test[progress.position].question_id
    if questions.right_answer == kwargs['d']['poll_answer']['option_ids'][0]:
        progress.correct_answer += 1
    else:
        progress.incorrect_answer += 1
    progress.save()
    if progress.position < Test.objects.filter(id_test=kwargs['user'].level).count():
        progress.position += 1
        progress.save()
        pass_test(id=kwargs['id'], user=kwargs['user'], d=kwargs['d'])


def get_id_message(**kwargs):
    if 'message' in kwargs['d']:
        kwargs['user'].position = 4
        kwargs['user'].save()
        bot.send_message(kwargs['id'],
                         f"Номер сообщения {kwargs['d']['message']['message_id']}, id автора {kwargs['id']} сохраните эту информацию для привязки к уроку")
    else:
        bot.send_message(kwargs['id'], 'Это не сообщение', reply_markup=INLINE_KEYBOARD_BACK)


def get_all_presentations(**kwargs):
    presentations = FileUser.objects.filter(level=-1)
    for i in presentations:
        bot.send_message(kwargs['id'], f'Презентация пользователя {i.user.first_name} {i.user.last_name}')
        bot.copy_message(kwargs['id'], i.user.id, i.id_message)
    bot.send_message(kwargs['id'], f'Количество презентаций: {len(presentations)}')


def get_question(**kwargs):
    if kwargs['user'].user:
        if 'message' in kwargs['d']:
            if 'poll' in kwargs['d']['message']:
                answers = []
                correct_id = kwargs['d']['message']['poll']['correct_option_id']
                options = kwargs['d']['message']['poll']['options']
                question = kwargs['d']['message']['poll']['question']
                for i in options:
                    answers.append(i['text'])
                question = Question(question=question, answers=json.dumps(answers),
                                    right_answer=correct_id)
                question.save()
                kwargs['user'].position = 4
                kwargs['user'].save()
                bot.send_message(kwargs['id'], f'Вопрос сохранен. Номер вопроса: {question.id}',
                                 reply_markup=menu_keyboard(kwargs['user']))
            else:
                bot.send_message(kwargs['id'], 'Poll not in message', reply_markup=INLINE_KEYBOARD_BACK)
        else:
            bot.send_message(kwargs['id'], 'Message not in JSON', reply_markup=INLINE_KEYBOARD_BACK)
    else:
        bot.send_message(kwargs['id'], 'You are not admin', reply_markup=INLINE_KEYBOARD_BACK)



def get_presentations_by_lastname(**kwargs):
    kwargs['user'].position = 6
    kwargs['user'].save()
    bot.send_message(kwargs['id'], 'Введите фамилию и имя пользователя для получения презентации')

def get_create_course(**kwargs):
    try:
        kwargs['user'].position = 4
        kwargs['user'].save()
        name = kwargs['message'][:kwargs['message'].find('\n')]
        description = kwargs['message'][kwargs['message'].find('\n') + 1:]
        course = Lesson(id=Lesson.objects.filter().count(), name=name, description=description, status=False)
        course.save()
        bot.send_message(kwargs['id'], f'Добавлен новый урок номер {course.id}')
    except Lesson.DoesNotExist:
        bot.send_message(kwargs['id'], 'Такого урока не существует')
    except:
        bot.send_message(kwargs['id'], f'Что-то не так')


def get_create_course(**kwargs):
    try:
        kwargs['user'].position = 4
        kwargs['user'].save()
        name = kwargs['message'][:kwargs['message'].find('\n')]
        description = kwargs['message'][kwargs['message'].find('\n') + 1:]
        course = Lesson(id=Lesson.objects.filter().count(), name=name, description=description, status=False)
        course.save()
        bot.send_message(kwargs['id'], f'Добавлен новый урок номер {course.id}')
    except:
        bot.send_message(kwargs['id'], f'Что-то не так', reply_markup=INLINE_KEYBOARD_BACK)


def get_active_course(**kwargs):
    try:
        kwargs['user'].position = 4
        kwargs['user'].save()
        try:
            course = Lesson.objects.get(name=kwargs['message'])
            course.status = not course.status
            if course.status:
                course.date_creation = timezone.now()
            course.save()
            bot.send_message(kwargs['id'], 'урок активирован' if course.status else 'урок деактивирован')
        except Lesson.DoesNotExist:
            bot.send_message(kwargs['id'], 'Не знаю такого урока, возможно вы не учли регистр',
                             reply_markup=INLINE_KEYBOARD_BACK)
    except:
        bot.send_message(kwargs['id'], f'Что-то не так', reply_markup=INLINE_KEYBOARD_BACK)


def update_info_set(**kwargs):
    kwargs['user'].position = 7
    kwargs['user'].save()
    bot.send_message(kwargs['id'], 'Отправьте текстовое сообщение с новой информацией')


def set_info(**kwargs):
    if kwargs['user'].user:
        with open('info.txt', 'w') as f:
            f.write(kwargs['message'])
        global INFO_MESSAGE
        INFO_MESSAGE = kwargs['message']
        kwargs['user'].position = 4
        kwargs['user'].save()
        bot.send_message(kwargs['id'], 'Информация успешно обновлена')


def get_teo_course(**kwargs):
    try:
        kwargs['user'].position = 4
        kwargs['user'].save()
        inf = kwargs['message'].split(';')
        try:
            file = File(lesson=Lesson.objects.get(name=inf[0]), id_message=int(inf[1].strip()),
                        id_chat=int(inf[2].strip()))
            file.save()
            bot.send_message(kwargs['id'], 'Файл добавлен')
        except Lesson.DoesNotExist:
            bot.send_message(kwargs['id'], 'Не знаю такого урока, возможно вы не учли регистр',
                             reply_markup=INLINE_KEYBOARD_BACK)
    except:
        bot.send_message(kwargs['id'], f'Что-то не так', reply_markup=INLINE_KEYBOARD_BACK)


def get_qw_test(**kwargs):
    try:
        kwargs['user'].position = 4
        kwargs['user'].save()
        inf = kwargs['message'].split(';')
        try:
            test = Test(id_test=Lesson.objects.get(name=inf[0]).id, question_id=Question.objects.get(id=int(inf[1])))
            test.save()
            bot.send_message(kwargs['id'], 'Вопрос добавлен')
        except Lesson.DoesNotExist:
            bot.send_message(kwargs['id'], 'Не знаю такого урока, возможно вы не учли регистр',
                             reply_markup=INLINE_KEYBOARD_BACK)
        except Question.DoesNotExist:
            bot.send_message(kwargs['id'], 'Не знаю такого вопроса', reply_markup=INLINE_KEYBOARD_BACK)
    except:
        bot.send_message(kwargs['id'], f'Что-то не так', reply_markup=INLINE_KEYBOARD_BACK)


# пейлоады


def change_name(**kwargs):
    bot.send_message(kwargs['id'], "Введите ваше фамилию и имя\nПример ввода: Иванов Иван",
                     reply_markup=INLINE_KEYBOARD_BACK)
    kwargs['user'].position = -1
    kwargs['user'].save()


def change_email(**kwargs):
    bot.send_message(kwargs['id'], "Введите новую почту", reply_markup=INLINE_KEYBOARD_BACK)
    kwargs['user'].position = -2
    kwargs['user'].save()


def change_phone(**kwargs):
    bot.send_message(kwargs['id'], "Введите новый номер телефона", reply_markup=INLINE_KEYBOARD_BACK)
    kwargs['user'].position = -3
    kwargs['user'].save()


def change_group(**kwargs):
    bot.send_message(kwargs['id'], "Введите новую группу", reply_markup=INLINE_KEYBOARD_BACK)
    kwargs['user'].position = -4
    kwargs['user'].save()


def change_notifications(**kwargs):
    kwargs['user'].notice = not kwargs['user'].notice
    kwargs['user'].save()
    bot.send_message(kwargs['id'], f'Уведомления {"включены" if kwargs["user"].notice else "отключены"}')


def save_file(**kwargs):
    if kwargs['user'].user:
        kwargs['user'].position = -11
        kwargs['user'].save()
        bot.send_message(kwargs['id'], 'Пришлите сообщение с файлом! (По 1 файлу)')
    else:
        bot.send_message(kwargs['id'], 'Тебе здесь не рады')

def save_file_optional(**kwargs):
    if kwargs['user'].user:
        kwargs['user'].position = -11
        kwargs['user'].save()
        bot.send_message(kwargs['id'], 'Пришлите сообщение с файлом! (По 1 файлу)')
    else:
        bot.send_message(kwargs['id'], 'Тебе здесь не рады')





def save_question(**kwargs):
    if kwargs['user'].user:
        markup = ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton("Создать вопрос", request_poll=KeyboardButtonPollType('quiz')))
        kwargs['user'].position = -12
        kwargs['user'].save()
        bot.send_message(kwargs['id'], 'Создайте вопрос', reply_markup=markup)


def get_old_courses_info(**kwargs):
    id_lesson = kwargs['d']['callback_query']['data'].split()[1]
    try:
        les = Lesson.objects.get(id=int(id_lesson), status=True)
        if les.id < kwargs['user'].level:
            bot.send_message(kwargs['id'], f"{les.name}\n\n{les.description}")
            for i in File.objects.filter(lesson=les):
                bot.copy_message(kwargs['id'], i.id_chat, i.id_message)
        else:
            bot.send_message(kwargs['id'], 'А че как')
    except Lesson.DoesNotExist:
        bot.send_message(kwargs['id'], 'В душе не знаю какой урок ты выбрал')

def set_presentation(**kwargs):
    kwargs['user'].position = 5
    kwargs['user'].save()
    bot.send_message(kwargs['id'], 'Отправьте обновленную презентацию')

def create_course(**kwargs):
    if kwargs['user'].user:
        kwargs['user'].position = -13
        kwargs['user'].save()
        bot.send_message(kwargs['id'], "Пришлите название и описание урока в формате:\nНазвание урока\nОписание урока")


def active_course(**kwargs):
    if kwargs['user'].user:
        kwargs['user'].position = -14
        kwargs['user'].save()
        bot.send_message(kwargs['id'], "Введите название урока у которого нужно изменить статус")


def set_teo_course(**kwargs):
    if kwargs['user'].user:
        kwargs['user'].position = -15
        kwargs['user'].save()
        bot.send_message(kwargs['id'], "Введите название урока, номер файла, и id создателя через ;")







def set_qw_test(**kwargs):
    if kwargs['user'].user:
        kwargs['user'].position = -16
        kwargs['user'].save()
        bot.send_message(kwargs['id'], "Введите название урока и номер вопроса через ;")


def notification_old(**kwargs):
    users = TelegramUser.objects.filter(notice=True, time_message__lte=(timezone.now() - timezone.timedelta(days=3)))
    for i in users:
        try:
            bot.send_message(i.id, "Вы давно не проявляли активность")
        except:
            bot.send_message(kwargs['id'], f"Не получилось отправить сообщение пользователю {i.id}")
    bot.send_message(kwargs['id'], f'Сообщение отправлено {len(users)} пользователям')


def get_optional_tests(**kwargs):
    optional_lessons = OptionalLesson.objects.filter(id_lesson=kwargs['user'].level)
    keyboard_optional_courses = InlineKeyboardMarkup(row_width=2)
    for course in optional_lessons:
        keyboard_optional_courses.add(InlineKeyboardButton(course.name, callback_data=f'get_optional_courses {course.id}'))
    if len(optional_lessons) > 0:
        bot.send_message(kwargs['id'], 'Дополнительные уроки', reply_markup=keyboard_optional_courses)
    else:
        bot.send_message(kwargs['id'], 'Дополнительные уроки отсутствуют')



def get_optional_tests_info(**kwargs):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
    markup.add(KeyboardButton("/пройти дополнительный тест"),
                  KeyboardButton("/назад"))
    id_lesson = kwargs['d']['callback_query']['data'].split()[1]
    try:
        kwargs['user'].position = -20
        kwargs['user'].save()
        optional_lessons = OptionalLesson.objects.get(id=id_lesson)
        bot.send_message(kwargs['id'], f"{optional_lessons.name}\n\n{optional_lessons.description}")
        for i in FileUser.objects.filter(level=-100-int(id_lesson)): # тут придется что то делать
            bot.copy_message(kwargs['id'], i.user.id, i.id_message)
        bot.send_message(kwargs['id'], 'Для прохождения теста к уроку прикрепите конспект одним файлом', reply_markup=INLINE_KEYBOARD_BACK)

    except OptionalLesson.DoesNotExist:
        bot.send_message(kwargs['id'], 'В душе не знаю какой урок ты выбрал')



def create_optional_course_set(**kwargs):
    kwargs['user'].position = 10
    kwargs['user'].save()
    bot.send_message(kwargs['id'], 'Отправьте название урока, к которому вы привязываете дополнительный урок, название самого урока и его описание с новой строки')


def create_optional_lesson(**kwargs):
    try:
        temp = kwargs['message'].find('\n')
        lesson = kwargs['message'][:temp]
        temp1 = kwargs['message'].find('\n', temp+1)
        name = kwargs['message'][temp + 1:temp1]
        description = kwargs['message'][temp1 + 1:]
        les = Lesson.objects.get(name=lesson)
        OptionalLesson(id_lesson=les.id, name=name, description=description).save()
        kwargs['user'].position = 4
        kwargs['user'].save()
        bot.send_message(kwargs['id'], 'Дополнительный урок успешно создан')
    except Lesson.DoesNotExist:
        bot.send_message(kwargs['id'], 'Такого урока не существует')
    except:
        bot.send_message(kwargs['id'], 'Что-то произошло не так')

def set_teo_course_optional(**kwargs):
    if kwargs['user'].user:
        kwargs['user'].position = -18
        kwargs['user'].save()
        bot.send_message(kwargs['id'], "Введите название дополнительного урока и номер файла")

def get_teo_course_optional(**kwargs):
    try:
        kwargs['user'].position = 4
        kwargs['user'].save()
        inf = kwargs['message'].split(';')
        lesson = OptionalLesson.objects.get(name=inf[0])
        try:
            file = FileUser(user=kwargs['user'], level=-100-lesson.id, id_message=inf[1].strip())
            file.save()
            bot.send_message(kwargs['id'], 'Файл добавлен')
        except OptionalLesson.DoesNotExist:
            bot.send_message(kwargs['id'], 'Не знаю такого дополнительного урока, возможно вы не учли регистр',
                             reply_markup=INLINE_KEYBOARD_BACK)
    except:
        bot.send_message(kwargs['id'], f'Что-то не так', reply_markup=INLINE_KEYBOARD_BACK)

def set_qw_test_optional(**kwargs):
    if kwargs['user'].user:
        kwargs['user'].position = -18
        kwargs['user'].save()
        bot.send_message(kwargs['id'], "Введите название урока и номер вопроса через ;")


def get_qw_test_optional(**kwargs):
    try:
        kwargs['user'].position = 4
        kwargs['user'].save()
        inf = kwargs['message'].split(';')
        try:
            test = Test(id_test=OptionalLesson.objects.get(name=inf[0]).id, question_id=Question.objects.get(id=int(inf[1])))
            test.save()
            bot.send_message(kwargs['id'], 'Вопрос добавлен')
        except Lesson.DoesNotExist:
            bot.send_message(kwargs['id'], 'Не знаю такого урока, возможно вы не учли регистр',
                             reply_markup=INLINE_KEYBOARD_BACK)
        except Question.DoesNotExist:
            bot.send_message(kwargs['id'], 'Не знаю такого вопроса', reply_markup=INLINE_KEYBOARD_BACK)
    except:
        bot.send_message(kwargs['id'], f'Что-то не так', reply_markup=INLINE_KEYBOARD_BACK)


# перебрать потом
# - - - - - - - -
global INFO_MESSAGE
with open('info.txt') as f:
    INFO_MESSAGE = f.read()

import pandas as pd

def report(**kwargs):
    if kwargs['user'].user:
        tests = TestProgress.objects.exclude(date_end__isnull=True)
        info = []
        if len(tests)>0:
            for test in tests:
                info.append([f"{test.id_user.first_name} {test.id_user.last_name}", test.id_test+1, test.correct_answer, test.incorrect_answer])
            info = [*zip(*info)]

            df = pd.DataFrame({'Пользователь': info[0],
                           'Урок': info[1],
                           'Правильных': info[2],
                           'Неправильных': info[3],
                           })

            df.to_excel('report.xlsx', index=False)

            with open("report.xlsx", "rb") as f:
                bot.send_document(kwargs['id'], f)
        else:
            bot.send_message(kwargs['id'], 'Нечего отправлять')



# имя и фамилия юзера в БД

regex_name = re.compile(r'^[A-ЯЁ][а-яё]+\s[A-ЯЁ][а-яё]+$')
regex_email = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9-]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
regex_tel = re.compile(r'(\+)?[7-8]\d{10}')
regex_group = re.compile(r'([А-Я]+)-(\d+)')

KEYBOARD_MENU = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
KEYBOARD_MENU.add(KeyboardButton("/профиль"),
                  KeyboardButton("/уроки"),
                  KeyboardButton("/инфо"),
                  KeyboardButton("/настройки"),
                  )

KEYBOARD_MENU_ADMIN = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
KEYBOARD_MENU_ADMIN.add(KeyboardButton("/профиль"),
                        KeyboardButton("/уроки"),
                        KeyboardButton("/инфо"),
                        KeyboardButton("/настройки"),
                        KeyboardButton("/админка"),
                        )

INLINE_KEYBOARD_BACK = InlineKeyboardMarkup().add(InlineKeyboardButton("Назад", callback_data='getBack'))


def set_fn_user(id, message, user, d):
    if re.fullmatch(regex_name, message):
        message = message.split(" ")
        user.last_name = message[0]
        user.first_name = message[1]
        user.position += 1
        user.save()
        bot.send_message(id, f'Приятно познакомиться {user.first_name}\nВведите ваш email')
        return None
    bot.send_message(id, 'Некоректный ввод имени и фамилии. Пример ввода: Иван Иванов')


def set_email_user(id, message, user, d):
    if re.fullmatch(regex_email, message):
        user.email = message
        user.position += 1
        user.save()
        bot.send_message(id, 'Ок, идем дальше, введите ваш телефон')
        return None
    bot.send_message(id, 'Некоректный ввод email')


def set_tel_user(id, message, user, d):
    if re.fullmatch(regex_tel, message):
        user.phone = message
        user.position += 1
        user.save()
        bot.send_message(id, 'Хорошо, введите вашу группу')
        return None
    bot.send_message(id, 'Некоректный ввод телефона. Пример ввода: +79998887766')


def set_group_user(id, message, user, d):
    if re.fullmatch(regex_group, message.upper()):
        user.group = message.upper()
        user.position += 1
        user.date_creation = timezone.now()
        user.save()
        bot.send_message(id, 'Все, ты успешно зарегистрировался', reply_markup=menu_keyboard(user))
        return None
    bot.send_message(id, 'Некоректный ввод группы. Пример ввода: АВС-321')


def get_presentation(id, message, user, d):
    if FileUser.objects.filter(user=user, level=-1).exists():
        FileUser.objects.get(user=user, level=-1).delete()
    bot.send_message(id, 'Презентация успешно прикреплена')
    user.position = 4
    user.save()
    FileUser(user=user, level=-1, id_message=d['message']['message_id']).save()


def get_my_presentation(**kwargs):
    try:
        presentation = FileUser.objects.get(user=kwargs['user'], level=-1)
        bot.copy_message(kwargs['id'], kwargs['id'], presentation.id_message)
    except FileUser.DoesNotExist:
        bot.send_message(kwargs['user'], 'Презентация отсутствует')



def get_profile(**kwargs):
    if FileUser.objects.filter(user=kwargs['user'], level=-1).exists():
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('Скачать текущую презентацию', callback_data='getPresentation'))
        bot.send_message(kwargs['id'],
                     f"{kwargs['user'].first_name} {kwargs['user'].last_name}"
                     f"\n{kwargs['user'].email}\n{kwargs['user'].phone}"
                     f"\n{kwargs['user'].group}"
                     f"\nКоличество пройденных уроков: {kwargs['user'].level}", reply_markup=markup)
    else:
        bot.send_message(kwargs['id'],
                    f"{kwargs['user'].first_name} {kwargs['user'].last_name}"
                    f"\n{kwargs['user'].email}\n{kwargs['user'].phone}"
                    f"\n{kwargs['user'].group}"
                    f"\nКоличество пройденных уроков: {kwargs['user'].level}")



def get_help(**kwargs):
    bot.send_message(kwargs['id'],
                     'Бот предназначен для ..............'
                     '\nЕсли клавиатура отсутствует, вы можете воспользоваться командой /клавиатура')


def get_info(**kwargs):
    bot.send_message(kwargs['id'], INFO_MESSAGE)


def get_setting(**kwargs):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton("Имя", callback_data='setName'),
               InlineKeyboardButton("Почта", callback_data='setEmail'),
               InlineKeyboardButton("Телефон", callback_data='setPhone'),
               InlineKeyboardButton("Группа", callback_data='setGroup'),
               InlineKeyboardButton("Уведомления", callback_data='setNotifications'),
               InlineKeyboardButton('Презентация', callback_data='setPresentation'))
    bot.send_message(kwargs['id'], "Выберите, что вы хотите изменить", reply_markup=markup)


def get_key(**kwargs):
    bot.send_message(kwargs['id'], 'Клавиатура обновлена', reply_markup=menu_keyboard(kwargs['user']))


def delete_profile(**kwargs):
    kwargs['user'].delete()
    bot.send_message(kwargs['id'], 'Профиль удален')


def set_change_name(id, message, user, d):
    if re.fullmatch(regex_name, message):
        message = message.split(" ")
        user.last_name = message[0]
        user.first_name = message[1]
        user.position = 4
        user.save()
        bot.send_message(id, f'Приятно познакомиться {user.first_name}')
        return None
    bot.send_message(id, 'Некоректный ввод имени и фамилии.\nПример ввода: Иванов Иван',
                     reply_markup=INLINE_KEYBOARD_BACK)


def set_change_phone(id, message, user, d):
    if re.fullmatch(regex_tel, message):
        user.phone = message
        user.position = 4
        user.save()
        bot.send_message(id, 'Номер телефона изменен')
        return None
    bot.send_message(id, 'Некоректный ввод телефона. Пример ввода: +79998887766', reply_markup=INLINE_KEYBOARD_BACK)


def set_change_group(id, message, user, d):
    if re.fullmatch(regex_group, message):
        user.group = message
        user.position = 4
        user.save()
        bot.send_message(id, 'Группа изменена')
        return None
    bot.send_message(id, 'Некоректный ввод группы. Пример ввода: АВС-321', reply_markup=INLINE_KEYBOARD_BACK)


def set_change_email(id, message, user, d):
    if re.fullmatch(regex_email, message):
        user.email = message
        user.position = 4
        user.save()
        bot.send_message(id, 'Email сохранен')
        return None
    bot.send_message(id, 'Некоректный ввод Email', reply_markup=INLINE_KEYBOARD_BACK)


def get_courses(**kwargs):
    KEYBOARD_COURSES = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
    KEYBOARD_COURSES.add(KeyboardButton("/пройденные уроки"),
                         KeyboardButton("/текущий урок"),
                         KeyboardButton('/дополнительные задания'),
                         KeyboardButton("/назад"),
                         )
    bot.send_message(kwargs['id'], 'Что вам необходимо', reply_markup=KEYBOARD_COURSES)


def get_courses_old(**kwargs):
    if kwargs['user'].level > 0:
        KEYBOARD_COURSES_OLD = InlineKeyboardMarkup(row_width=3)
        names = list(Lesson.objects.values_list('name', flat=True)[:kwargs['user'].level])
        counter = 0
        for i in names:
            KEYBOARD_COURSES_OLD.add(InlineKeyboardButton(i, callback_data=f'get_old_courses_number {counter}'))
            counter += 1
        bot.send_message(kwargs['id'], 'Ваши уроки', reply_markup=KEYBOARD_COURSES_OLD)
    else:
        bot.send_message(kwargs['id'], 'Вы еще не прошли ни одного урока')


def get_presentation_family(**kwargs):
    try:
        kwargs['user'].position = 4
        kwargs['user'].save()
        try:
            user = TelegramUser.objects.get(first_name=kwargs['message'].split()[1], last_name=kwargs['message'].split()[0])
            presentation = FileUser.objects.get(user=user, level=-1)
            bot.send_message(kwargs['id'], f'Презентация пользователя {user.first_name} {user.last_name}')
            bot.copy_message(kwargs['id'], user.id, presentation.id_message)
        except TelegramUser.DoesNotExist:
            bot.send_message(kwargs['id'], 'Не знаю такого пользователя',)
        except FileUser.DoesNotExist:
            bot.send_message(kwargs['id'], 'Пользователь не прикрепил презентацию')
    except:
        bot.send_message(kwargs['id'], f'Что-то не так')






def get_instruction(**kwargs):
    if kwargs['user'].user:
        bot.send_message(kwargs['id'],
                         'Создание урока:\nНажимаем создать урок, на первой строке вводим название урока, переходим на новую строку и пишем описание урока'
                         '\n\n'
                         '\nДобавление файла в урок:\nНажимаем сохранить файл, присылаем боту любой файл, бот присылает ID сообщения и ID автора\n'
                         'Нажимаем: добавить файл в урок, вводим название урока, ID сообщения и ID автора через ; (пример: <Название урока>;<ID сообщения>;<ID автора>)'
                         '\n\nДобавление вопроса в тест к уроку:\nНажимаем сохранить вопрос, на нижней панели появляется кнопка: создать урок, вводим необходимый вопрос и ответы, отправляем сообщение боту и получаем номер вопроса. На панели администратора жмем добавить викторину к тесту, после чего вводим Название урока и номер вопроса через ;(пример: <Название урока>;<Номер вопроса>'
                         '\n\nАктивация теста: после настройки урока, его необходимо активировать кнопкой Изменить статус урока'
                         '\n\nВ случае недостатка команд, вы можете воспользоваться админ-панелью базы данных по ссылке: http://rsublab.pythonanywhere.com/admin/'
                         '\nЛогин: root\nПароль: toor')


def get_courses_now(**kwargs):
    try:
        les = Lesson.objects.get(id=kwargs['user'].level, status=True)

        if kwargs['user'].date_creation < les.date_creation:
            if kwargs['user'].level > 0:
                test = Test.objects.filter(id_test=kwargs['user'].level - 1)
                if TestProgress.objects.filter(id_test=test[0].id_test, id_user=kwargs['user'], status=False).exists():
                    a = TestProgress.objects.filter(id_test=test[0].id_test, id_user=kwargs['user'], status=False)
                    for i in a:
                        days =7
                        if i.date_end > timezone.now() - timezone.timedelta(days):
                            bot.send_message(kwargs['id'], f'Урок будет открыт через {days} дня(ей), после завершения прошлого урока')
                            return None

        kwargs['user'].position = -17
        kwargs['user'].save()
        bot.send_message(kwargs['id'], f"{les.name}\n\n{les.description}")
        for i in File.objects.filter(lesson=les):
            bot.copy_message(kwargs['id'], i.id_chat, i.id_message)
        bot.send_message(kwargs['id'], 'Для прохождения теста к уроку прикрепите конспект одним файлом', reply_markup=INLINE_KEYBOARD_BACK)
    except Lesson.DoesNotExist:
        bot.send_message(kwargs['id'], 'На текущий момент нет нового урока')


def add_summary(**kwargs):
    if FileUser.objects.filter(user=kwargs['user'], level=kwargs['user'].level).exists():
        FileUser.objects.get(user=kwargs['user'], level=kwargs['user'].level).delete()
    FileUser(user=kwargs['user'], level=kwargs['user'].level, id_message=kwargs['d']['message']['message_id']).save()
    kwargs['user'].position = 4
    kwargs['user'].save()
    KEYBOARD_COURSES_NOW = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
    KEYBOARD_COURSES_NOW.add(
            KeyboardButton("/пройти тест"),
            KeyboardButton("/назад"))
    bot.send_message(kwargs['id'], "Вы успешно прикрепили файл", reply_markup=KEYBOARD_COURSES_NOW)


def add_summary_optional(**kwargs):
    try:
        if FileUser.objects.filter(user=kwargs['user'], level=-100-kwargs['user'].level).exists():
            FileUser.objects.get(user=kwargs['user'], level=-100-kwargs['user'].level).delete()
        FileUser(user=kwargs['user'], level=-100-kwargs['user'].level, id_message=kwargs['d']['message']['message_id']).save()
        kwargs['user'].position = 4
        kwargs['user'].save()
        bot.send_message(kwargs['id'], "Вы успешно прикрепили файл")
    except:
        bot.send_message(kwargs['id'], 'Что-то не так')


def menu_keyboard(user):
    if user.user:
        return KEYBOARD_MENU_ADMIN
    return KEYBOARD_MENU


def get_id(json):
    if 'callback_query' in json:
        id = json['callback_query']['from']['id']
    elif 'poll_answer' in json:
        id = json['poll_answer']['user']['id']
    else:
        id = json['message']['from']['id']
    return id
# - - - - - - - -
