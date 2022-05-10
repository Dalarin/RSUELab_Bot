from django.urls import path
from telegram_bot import views
urlpatterns = [
    path('', views.TelegramView.as_view())
]