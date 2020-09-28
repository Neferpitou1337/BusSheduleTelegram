import telebot
from telebot import types
from bs4 import BeautifulSoup
import config
import requests
import userTableWorker

# initialization of bot
bot = telebot.TeleBot(config.TOKEN, parse_mode=None)


# handler of /start and /reset commands
@bot.message_handler(commands=['start', 'reset'])
def send_welcome(message):
    # instead of gitub.com it should open my github with this project
    bot.reply_to(message, "Welcome to Bus Schedule Bot\nInstructions can be seen here:\ngithub.com",
                 disable_web_page_preview=False)
    userTableWorker.setAll(message.chat.id, "num", "f", "fl", "l", "ll", config.States.S_ENTER_NUMBER)


# todo:make some description
@bot.message_handler(func=lambda message: userTableWorker.getState(message.chat.id) == config.States.S_ENTER_NUMBER,
                     content_types=['text'])
def numberHandler(message):
    # if message.text not in config.NUMBERS_OF_BUSES:
    #     bot.reply_to(message, "This bus doesn't exist or Creator doesn't know about its emergence")
    # else:
    #     # todo:избавиться от глобальности и заимплементить в дб
    #
    #     #creation of direction buttons
    #     markup = types.InlineKeyboardMarkup()
    #     itembtn1 = types.InlineKeyboardButton(text=d[index].get('first'),callback_data='direct')
    #     itembtn2 = types.InlineKeyboardButton(text=d[index].get('last'),callback_data='reverse')
    #     markup.add(itembtn1,itembtn2)
    #
    #     userWorker.setAll(message.chat.id, d[index].get("number"), d[index].get("first"), d[index].get("first_link"), \
    #                       d[index].get("last"), d[index].get("last_link"), config.States.S_CHOOSE_DIR)
    #     #
    #     # todo:Write code here
    #     #
    #     #todo: на этот реплай повесить кнопочки и изменить значениек в базе данных на ожидает нажатия кнопочки \
    #     # сейвануть текущее состояние и строчку под index из листа словарей, затем после нажатия кнопки убрать кнопки
    #     bot.send_message(message.chat.id, "Выберите направление:", reply_markup = markup)
    pass


@bot.callback_query_handler(
    func=lambda call: userTableWorker.getState(call.message.chat.id) == config.States.S_CHOOSE_DIR)
def callback_inline(call):
    # dict = userWorker.getAll(call.message.chat.id)
    # if call.message:
    #     if call.data == 'direct':
    #         #todo:Поменять markup на остановочный
    #         bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=dict.get("first"),reply_markup=None)
    #     elif call.data == 'reverse':
    #         #todo:Поменять markup на остановочный
    #         bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=dict.get("last"),reply_markup=None)
    #     userWorker.setState(call.message.chat.id, config.States.S_CHOOSE_BUS_STOP)
    pass


# [later] collective function to initialize scheduler of loop() in RefreshDB that will update all tables once a day URL=https://overcoder.net/q/37667/%D0%BA%D0%B0%D0%BA%D0%BE%D0%B2-%D0%BD%D0%B0%D0%B8%D0%BB%D1%83%D1%87%D1%88%D0%B8%D0%B9-%D1%81%D0%BF%D0%BE%D1%81%D0%BE%D0%B1-%D0%BF%D0%BE%D0%B2%D1%82%D0%BE%D1%80%D0%BD%D0%BE-%D0%B2%D1%8B%D0%BF%D0%BE%D0%BB%D0%BD%D1%8F%D1%82%D1%8C-%D1%84%D1%83%D0%BD%D0%BA%D1%86%D0%B8%D1%8E-%D0%BA%D0%B0%D0%B6%D0%B4%D1%8B%D0%B5-x-%D1%81%D0%B5%D0%BA%D1%83%D0%BD%D0%B4-%D0%B2-python
def RefreshDB_schedule(url):
    pass


# RUN
bot.polling(none_stop=True)
