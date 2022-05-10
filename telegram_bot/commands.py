from telegram_bot import functions

command_payload = {
    'setName': functions.change_name,
    'setEmail': functions.change_email,
    'setPhone': functions.change_phone,
    'setGroup': functions.change_group,
    'setNotifications': functions.change_notifications,
    'getBack': functions.get_back,
    'save_file': functions.save_file,
    'save_file_optional': functions.save_file_optional,
    'save_question': functions.save_question,
    'get_old_courses_number': functions.get_old_courses_info,
    'setPresentation': functions.set_presentation,
    'getPresentation': functions.get_my_presentation,
    'get_all_presentations': functions.get_all_presentations,
    'get_presentations_by_lastname': functions.get_presentations_by_lastname,
    'update_info': functions.update_info_set,
    'get_summary_set': functions.get_summary_set,
    'get_summary_optional_set': functions.get_summary_optional_set,
    'make_notification_set': functions.make_notification_set,
    'get_report': functions.report,
    'get_optional_courses': functions.get_optional_tests_info,
    'create_optional_course_set': functions.create_optional_course_set,
    'set_qw_test_optional': functions.set_qw_test_optional,
    'create_course': functions.create_course,
    'active_course': functions.active_course,
    'set_teo_course': functions.set_teo_course,
    'set_teo_course_optional': functions.set_teo_course_optional,
    'set_qw_test': functions.set_qw_test,
    'notify_users': functions.notification_old,
    'instruction': functions.get_instruction,
}

command = {
    '/help': functions.get_help,
    '/помощь': functions.get_help,
    '/профиль': functions.get_profile,
    '/инфо': functions.get_info,
    '/настройки': functions.get_setting,
    '/уроки': functions.get_courses,

    '/пройденные уроки': functions.get_courses_old,
    '/текущий урок': functions.get_courses_now,
    '/назад': functions.get_back,
    '/пройти тест': functions.pass_test,
   # '/пройти дополнительный тест': functions.pass_optional_test,
    '/дополнительные задания': functions.get_optional_tests,


    '/клавиатура': functions.get_key,
    '/админка': functions.adminka,

    '/delete_profile': functions.delete_profile,
}

command_pos = {
    -20: functions.add_summary_optional,
    -19: functions.get_qw_test_optional,
    -18: functions.get_teo_course_optional,
    -17: functions.add_summary,
    -16: functions.get_qw_test,
    -15: functions.get_teo_course,
    -14: functions.get_active_course,
    -13: functions.get_create_course,
    -12: functions.get_question,
    -11: functions.get_id_message,
    # -10: mydef.get_id_message,  # для адина, почему -10? потому что автор идиот
    -4: functions.set_change_group,
    -3: functions.set_change_phone,
    -2: functions.set_change_email,
    -1: functions.set_change_name,
    0: functions.set_fn_user,
    1: functions.set_email_user,
    2: functions.set_tel_user,
    3: functions.set_group_user,
    5: functions.get_presentation,
    6: functions.get_presentation_family,
    7: functions.set_info,
    8: functions.get_summary,
    9: functions.make_notification,
    10: functions.create_optional_lesson,
    11: functions.get_summary_optional,
}