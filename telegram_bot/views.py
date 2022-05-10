import json
import logging

from django.http import HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from telegram_bot import functions
from telegram_bot.commands import command_payload, command_pos, command
from telegram_bot.models import TelegramUser, Ban

bot = functions.bot
logger = logging.getLogger(__name__)


# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class TelegramView(View):
    @staticmethod
    def post(request):
        try:
            d = json.loads(request.body.decode('utf-8'))
            id = functions.get_id(d)
            print(d)
            logger.info(str(d))
            """
            bot.send_poll(id, questions.question, json.loads(questions.answers), type='quiz',
                          correct_option_id=questions.right_answer, is_anonymous=False)
            """
            if Ban.objects.filter(id=id).exists():
                bot.send_message(id, 'К сожалению, вы находитесь в бане, поэтому не можете пользоваться ботом')
            else:
                message = ""
                if 'message' in d:
                    if 'text' in d['message']:
                        message = d['message']['text']
                payload = ""
                if 'callback_query' in d:
                    if 'data' in d['callback_query']:
                        payload = d['callback_query']['data']
                try:
                    user = TelegramUser.objects.get(id=id)
                    user.time_message = timezone.now()
                    if payload != "":
                        print(payload.split()[0])
                        if payload.split()[0] in command_payload:
                            command_payload[payload.split()[0]](id=id, user=user, d=d)
                    elif 'poll_answer' in d:
                        functions.check_answer(id=id, user=user, d=d)
                    elif user.position in command_pos:
                        command_pos[user.position](id=id, message=message, user=user, d=d)
                    else:
                        if message in command:
                            command[message](id=id, user=user)
                        else:
                            bot.send_message(id, 'Не понимаю тебя, введите /помощь или /help если хотите узнать комнды')
                except TelegramUser.DoesNotExist:
                    bot.send_message(id, 'Добрый день, ваш аккаунт не зарегистрирован. Введите ваше фамилию и имя')

                    # тут показывать кнопку на клавиатуре: РЕГИСТРАЦИЯ
                    TelegramUser(id=id, time_message=timezone.now()).save()
                #  bot.send_message(d['message']['from']['id'], d['message']['text'])
        except Exception as e:
            print(f'Какая то ошибка {e}')
        return HttpResponse('ok')
