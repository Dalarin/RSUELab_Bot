from django.contrib import admin

# Register your models here.


from telegram_bot.models import TelegramUser, Ban, Lesson, File, Question, Test, TestProgress, FileUser, OptionalLesson


class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'phone', 'email', 'group', 'level', 'notice', 'position', "time_message", "date_creation")
    ordering = ('id',)


admin.site.register(TelegramUser, TelegramUserAdmin)


class BanAdmin(admin.ModelAdmin):
    list_display = ('id',)


class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'status', "date_creation")


class FileAdmin(admin.ModelAdmin):
    list_display = ('id', 'lesson', 'id_message', 'id_chat')


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'answers', 'right_answer')


class TestAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_test', 'question_id')


class TestProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_test', 'id_user', 'position', 'correct_answer',
                    'incorrect_answer', "date_start", "date_end", "status")

class FileUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'level', 'id_message')


class OptionalLessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'status')





admin.site.register(Ban, BanAdmin)
admin.site.register(FileUser, FileUserAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(OptionalLesson, OptionalLessonAdmin)
admin.site.register(File, FileAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(TestProgress, TestProgressAdmin)
