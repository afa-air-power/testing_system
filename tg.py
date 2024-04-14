import json
import logging
import time
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.callback_data import CallbackData

import testing_sistem_API

with open("config.json") as f:
    config = json.load(f)
API_TOKEN = config["tg_api"]
chanele_with_result = config["tg-chanel"]
admin = config["admin"]
vip_users = config["vip_users"]
logging.basicConfig(level=logging.INFO)
user_mode = {}
user2test_id = {}
users_core_test = {}
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
user_mes = {}
user_2_index_test = {}
with open("tests.json") as file:
    tests = json.load(file)
with open("users_information.json") as f:
    user_information = json.load(f)
user_id2test = {}


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    if str(message.chat.id) not in user_information:
        user_information[str(message.chat.id)] = {"level": 0, "premium": False,
                                                  "name": message.from_user.first_name + ' ' + message.from_user.last_name}
        with open("users_information.json", 'w') as f:
            f.write(json.dumps(user_information, indent=4))

    await message.reply(config["first_message"])


@dp.message_handler(commands=['game'])
async def send_welcome(message: types.Message):
    await message.reply(" это режим бесконечной генерации заданий он в разработке")


@dp.message_handler(commands=['creat_test'])
async def send_welcome(message: types.Message):
    if str(message.chat.id) not in vip_users:
        await message.reply("это доступно только VIP пользователям ")
        return
    user_mode[str(message.chat.id)] = "creat_test"
    await message.reply("отправьте тест ")


@dp.message_handler(commands=['profile'])
async def send_welcome(message: types.Message):
    answer_to_user_about_information = 'Вся информация о вас в данной системе\n'
    answer_to_user_about_information += '\tИмя пользователя: ' + user_information[str(message.chat.id)]["name"] + '\n'
    answer_to_user_about_information += '\tномер телефона: неизвестен\n'
    answer_to_user_about_information += '\t личный уровень: ' + str(user_information[str(message.chat.id)]["level"])

    call_back_info = CallbackData('i', "id", "com", "test_id")
    inlaine_keyboard = InlineKeyboardMarkup()
    kb_1 = InlineKeyboardButton(text="изменить имя пользователя",
                                callback_data=call_back_info.new(id=0,
                                                                 com="edit_mame", test_id=0))
    kb_2= InlineKeyboardButton(url=config["information link"],text="криптословарь")
    inlaine_keyboard.row(kb_1)
    inlaine_keyboard.row(kb_2)

    await message.reply(answer_to_user_about_information, reply_markup=inlaine_keyboard)


@dp.message_handler(commands=['test'])
async def send_welcome(message: types.Message):
    if str(message.chat.id) not in user_information:
        user_information[str(message.chat.id)] = {"level": 0}
    if "username" not in str(message.chat):
        await message.reply("выберете себе username в настройках телеграмм")
        return 0
    mas = testing_sistem_API.get_names_category()
    call_back_info = CallbackData('i', "id", "com", "test_id")
    inlaine_keyboard = InlineKeyboardMarkup()
    for i in range(len(mas)):
        kb_1 = InlineKeyboardButton(text=mas[i],
                                    callback_data=call_back_info.new(id=0, com="chouse_category", test_id=str(i)))
        inlaine_keyboard.row(kb_1)
    await message.answer("Выберете курс дальнейшего выбора теста ", reply_markup=inlaine_keyboard)
    await message.delete()


@dp.callback_query_handler()
async def process_buttons_press(callback: CallbackQuery):
    print(callback.data.split(":"))
    if "chouse_category" == callback.data.split(":")[2]:
        mas = testing_sistem_API.category_index2names_test(int(callback.data.split(":")[3]))
        call_back_info = CallbackData('i', "id", "com", "test_id")
        inlaine_keyboard = InlineKeyboardMarkup()
        for i in range(len(mas)):
            kb_1 = InlineKeyboardButton(text=mas[i],
                                        callback_data=call_back_info.new(id=callback.data.split(":")[3],
                                                                         com="start_testing_f", test_id=str(i)))
            inlaine_keyboard.row(kb_1)
        await callback.message.edit_text("Выберете тест ", reply_markup=inlaine_keyboard)


    elif callback.data.split(":")[2] == "edit_mame":
        user_mode[str(callback.message.chat.id)] = "edit_mame"
        await callback.message.answer("отправьте новое имя пользователя")

    elif "start_testing_f" == callback.data.split(":")[2]:
        call_back_info = CallbackData('i', "id", "com", "test_id")
        inlaine_keyboard = InlineKeyboardMarkup()
        kb_1 = InlineKeyboardButton(text="продолжить",
                                    callback_data=call_back_info.new(id=callback.data.split(":")[1],
                                                                     com="start_testing",
                                                                     test_id=callback.data.split(":")[3]))
        inlaine_keyboard.row(kb_1)
        await callback.message.edit_text(text=testing_sistem_API.test(test_id=int(callback.data.split(":")[3]),
                                                                      test_category_index=int(
                                                                          callback.data.split(":")[1])).first_message,
                                         reply_markup=inlaine_keyboard)
    elif "start_testing" == callback.data.split(":")[2]:

        user_id2test[str(callback.message.chat.id)] = testing_sistem_API.test(test_id=int(callback.data.split(":")[3]),
                                                                              test_category_index=int(
                                                                                  callback.data.split(":")[1]))

        call_back_info = CallbackData('i', "id", "com", "test_id")
        inlaine_keyboard = InlineKeyboardMarkup()
        question = user_id2test[str(callback.message.chat.id)].questions[
            user_id2test[str(callback.message.chat.id)].question_id]

        for i in range(len(question.answers)):
            kb_1 = InlineKeyboardButton(text=question.answers[i],
                                        callback_data=call_back_info.new(id=0, com="testing", test_id=i))
            inlaine_keyboard.row(kb_1)
        await callback.message.answer(question.text, reply_markup=inlaine_keyboard)
        await callback.message.delete()
    elif "testing" == callback.data.split(":")[2]:
        test = user_id2test[str(callback.message.chat.id)]
        question = test.questions[user_id2test[str(callback.message.chat.id)].question_id]
        user_id2test[
            str(callback.message.chat.id)].user_score += question.difficulty_level if question.correct_answer == int(
            callback.data.split(":")[3]) else 0
        await callback.answer("Верно" if question.correct_answer == int(callback.data.split(":")[3]) else "неверно")
        user_id2test[str(callback.message.chat.id)].question_id += question.difficulty_level


        test = user_id2test[str(callback.message.chat.id)]
        if len(test.questions) == test.question_id:
            # отправка результатов теста
            await callback.message.answer("вы ответили правильно на " + str(test.user_score) + " из " + str(
                len(test.questions)) + " вопрсов в тесте под названием " + test.name + ".")
            await callback.message.answer(
                test.message_if_win if test.user_score / len(test.questions) > 0.75 else test.message_if_lose)
            user_information[str(callback.message.chat.id)]["level"] += 1
            messege_for_avtor_and_admin = "#" + callback.message.chat.username + " ответил/а правильно на " + str(
                test.user_score) + " из " + str(
                len(test.questions)) + " вопрсов в тесте под названием " + test.name + "."
            await bot.send_message(test.avtor, messege_for_avtor_and_admin)
            await bot.send_message(chanele_with_result, messege_for_avtor_and_admin)
            await callback.message.delete()

            return
        call_back_info = CallbackData('i', "id", "com", "test_id")
        inlaine_keyboard = InlineKeyboardMarkup()
        question = user_id2test[str(callback.message.chat.id)].questions[
            user_id2test[str(callback.message.chat.id)].question_id]
        if len(test.questions) == test.question_id:
            await callback.message.answer(
                "вы ответели правильно на " + str(test.user_score) + " из " + str(len(test.questions)) + "вопрсов ")
            return
        for i in range(len(question.answers)):
            kb_1 = InlineKeyboardButton(text=question.answers[i],
                                        callback_data=call_back_info.new(id=0, com="testing", test_id=i))
            inlaine_keyboard.row(kb_1)
        await callback.message.edit_text(question.text, reply_markup=inlaine_keyboard)


@dp.message_handler(content_types=['photo'])
async def handle_docs_photo(message):
    name = str(message.chat.id) + '_____' + str(int(time.time())) + '.jpg'
    await message.photo[-1].download(name)

    import main
    answer = main.checkking(name)
    to_user = 'отчет автоматической проверки \n'
    col_corect = sum([a[0] == a[1] for a in answer])
    for i in range(len(answer)):
        to_user += ' пример номер ' + str(i) + ' левая часть = ' + str(answer[i][0]) + ' правая часть = ' + str(
            answer[i][1]) + '\n\t'
    to_user += ' верно решено ' + str(col_corect) + 'из ' + str(len(answer)) + ' = ' + str(
        int(col_corect / len(answer) * 100)) + '%'

    await message.reply(to_user)


@dp.message_handler(content_types=['text'])
async def contat(message):
    global tests
    if str(message.chat.id) not in user_mode:
        await message.answer(
            "я не способен вас понять (\n\n\n напишите @afa_air_power если вы думаете что я ошибаюсь или перезапустите меня командой старт /start")
        return
    elif user_mode[str(message.chat.id)] == "creat_test":
        if testing_sistem_API.user_message2test(text=message.text, id_user=message.chat.id):
            await message.answer("тест сохранен в систему")
        else:
            await message.answer("произошла ошибка")
    elif user_mode[str(message.chat.id)] == "edit_mame":
        user_information[str(message.chat.id)]['name'] = message.text[:15]
        await message.answer("ваше имя успешно изменнено на " + user_information[str(message.chat.id)]['name'])


    else:
        await message.answer(
            "я не способен вас понять (\n\n\n напишите @afa_air_power если вы думаете что я ошибаюсь или перезапустите меня командой старт /start")


if __name__ == '__main__':
    executor.start_polling(dp)
