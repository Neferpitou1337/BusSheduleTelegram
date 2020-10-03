import telebot
from telebot import types
from bs4 import BeautifulSoup
import config
import requests
import userTableWorker
import hashlib
import timeOperator

# initialization of bot
bot = telebot.TeleBot(config.TOKEN, parse_mode=None)


# handler of /start and /reset commands
@bot.message_handler(commands=['start', 'reset'])
def send_welcome(message):
    # instead of gitub.com it should open my github with this project
    bot.reply_to(message, "Добро Пожаловать в Bus Schedule Bot\nКак пользоваться:\ngithub.com",
                 disable_web_page_preview=False)

    userTableWorker.setState(message.chat.id, config.States.S_ENTER_NUMBER.value)


# get directions from table and make 2 buttons inside bot
@bot.message_handler(func=lambda message: userTableWorker.getState(message.chat.id) == config.States.S_ENTER_NUMBER.value,
                     content_types=['text'])
def numberHandler(message):
    if message.text not in config.NUMBERS_OF_BUSES:
        bot.reply_to(message, "Попытайтесь написать русскими буквами или такого автобуса не существует или Создатель не знает о его появлении")
    else:
        dirs = userTableWorker.getDirections(message.text)

        #creation of direction buttons
        markup = types.InlineKeyboardMarkup()

        #using hash to define dirs
        hash_dirs0 = hashlib.md5(dirs[0].encode())
        hash_dirs1 = hashlib.md5(dirs[1].encode())

        itembtn1 = types.InlineKeyboardButton(text=dirs[0],callback_data=hash_dirs0.hexdigest())
        itembtn2 = types.InlineKeyboardButton(text=dirs[1],callback_data=hash_dirs1.hexdigest())
        markup.add(itembtn1)
        markup.add(itembtn2)

        bot.send_message(message.chat.id, message.text + "\nВыберите направление:", reply_markup = markup)

        # updating table userdecision
        userTableWorker.setAll(message.chat.id, message.text, None, None, config.States.S_CHOOSE_DIR.value)

# handle direction button and give n Stops buttons
@bot.callback_query_handler(
    func=lambda call: userTableWorker.getState(call.message.chat.id) == config.States.S_CHOOSE_DIR.value)
def callback_inline_Directions_Handler(call):
    if call.message:
        all = userTableWorker.getAll(call.message.chat.id)

        # get dir that user chooses
        dirs = userTableWorker.getDirections(all[1])
        if hashlib.md5(dirs[0].encode()).hexdigest() == call.data:
            dir = dirs[0]
        else:
            dir = dirs[1]

        stops = userTableWorker.getStops(all[1], dir)
        markup = types.InlineKeyboardMarkup()
        for st in stops:
            markup.add(types.InlineKeyboardButton(text=st,callback_data=st))

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=all[1]+"/"+dir,reply_markup=markup)

        # updating table userdecision
        userTableWorker.setAll(call.message.chat.id, all[1], dir, None, config.States.S_CHOOSE_BUS_STOP.value)



@bot.callback_query_handler(
    func=lambda call: userTableWorker.getState(call.message.chat.id) == config.States.S_CHOOSE_BUS_STOP.value)
def callback_inline_Stops_Handler(call):
    if call.message:
        all = userTableWorker.getAll(call.message.chat.id)
        stop = call.data

        weekdayTime = userTableWorker.getTime(all[1],False,all[2],stop)[0]
        weekendTime = userTableWorker.getTime(all[1],True,all[2],stop)[0]
        closestTime = timeOperator.getTime(weekdayTime,weekendTime)

        if weekendTime == '-':
            weekendTime = "в выходные дни: маршрутов нет"

        history  = all[1] + "/" + all[2] + "/" + stop
        clos_time = "Ближайшее время: " + closestTime
        Time = weekdayTime+'\n'+weekendTime

        # to mark these messages out
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=history,reply_markup=None)
        bot.send_message(call.message.chat.id,text=clos_time)
        bot.send_message(call.message.chat.id,text=Time)

        # reset table userdecision to begining
        userTableWorker.setAll(call.message.chat.id, None, None, None, config.States.S_ENTER_NUMBER.value)


# [later] collective function to initialize scheduler of loop() in RefreshDB that will update all tables once a day URL=https://overcoder.net/q/37667/%D0%BA%D0%B0%D0%BA%D0%BE%D0%B2-%D0%BD%D0%B0%D0%B8%D0%BB%D1%83%D1%87%D1%88%D0%B8%D0%B9-%D1%81%D0%BF%D0%BE%D1%81%D0%BE%D0%B1-%D0%BF%D0%BE%D0%B2%D1%82%D0%BE%D1%80%D0%BD%D0%BE-%D0%B2%D1%8B%D0%BF%D0%BE%D0%BB%D0%BD%D1%8F%D1%82%D1%8C-%D1%84%D1%83%D0%BD%D0%BA%D1%86%D0%B8%D1%8E-%D0%BA%D0%B0%D0%B6%D0%B4%D1%8B%D0%B5-x-%D1%81%D0%B5%D0%BA%D1%83%D0%BD%D0%B4-%D0%B2-python
def RefreshDB_schedule(url):
    pass


# RUN

# print(config.States.S_ENTER_NUMBER, "\n", config.States.S_ENTER_NUMBER)
bot.polling(none_stop=True)

