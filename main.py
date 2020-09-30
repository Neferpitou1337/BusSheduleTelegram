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

    userTableWorker.setState(message.chat.id, config.States.S_ENTER_NUMBER.value)


# get directions from table and make 2 buttons inside bot
@bot.message_handler(func=lambda message: userTableWorker.getState(message.chat.id) == config.States.S_ENTER_NUMBER.value,
                     content_types=['text'])
def numberHandler(message):
    if message.text not in config.NUMBERS_OF_BUSES:
        bot.reply_to(message, "Try to write with help of Russian Letters ot this bus doesn't exist and Creator doesn't know about its emergence")
    else:
        dirs = userTableWorker.getDirections(message.text)

        #creation of direction buttons
        markup = types.InlineKeyboardMarkup()
        itembtn1 = types.InlineKeyboardButton(text=dirs[0],callback_data=dirs[0])
        itembtn2 = types.InlineKeyboardButton(text=dirs[1],callback_data=dirs[1])
        markup.add(itembtn1,itembtn2)

        # updating table userdecision
        userTableWorker.setAll(message.chat.id, message.text, None, None, config.States.S_CHOOSE_DIR.value)

        bot.send_message(message.chat.id, "Выберите направление:", reply_markup = markup)


# handle direction button and give n Stops buttons
@bot.callback_query_handler(
    func=lambda call: userTableWorker.getState(call.message.chat.id) == config.States.S_CHOOSE_DIR.value)
def callback_inline_Directions_Handler(call):
    if call.message:
        all = userTableWorker.getAll(call.message.chat.id)
        dir = call.data

        stops = userTableWorker.getStops(all[1], dir)
        markup = types.InlineKeyboardMarkup()
        for st in stops:
            markup.add(types.InlineKeyboardButton(text=st,callback_data=st))

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=dir,reply_markup=markup)

        # updating table userdecision
        userTableWorker.setAll(call.message.chat.id, all[1], call.data, None, config.States.S_CHOOSE_BUS_STOP.value)




# [later] collective function to initialize scheduler of loop() in RefreshDB that will update all tables once a day URL=https://overcoder.net/q/37667/%D0%BA%D0%B0%D0%BA%D0%BE%D0%B2-%D0%BD%D0%B0%D0%B8%D0%BB%D1%83%D1%87%D1%88%D0%B8%D0%B9-%D1%81%D0%BF%D0%BE%D1%81%D0%BE%D0%B1-%D0%BF%D0%BE%D0%B2%D1%82%D0%BE%D1%80%D0%BD%D0%BE-%D0%B2%D1%8B%D0%BF%D0%BE%D0%BB%D0%BD%D1%8F%D1%82%D1%8C-%D1%84%D1%83%D0%BD%D0%BA%D1%86%D0%B8%D1%8E-%D0%BA%D0%B0%D0%B6%D0%B4%D1%8B%D0%B5-x-%D1%81%D0%B5%D0%BA%D1%83%D0%BD%D0%B4-%D0%B2-python
def RefreshDB_schedule(url):
    pass


# RUN

# print(config.States.S_ENTER_NUMBER, "\n", config.States.S_ENTER_NUMBER)
bot.polling(none_stop=True)

