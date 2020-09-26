# использовать эту функию против всяких оказий из-за которых все не по порядку

# Select routes.routename, directions.dir, stops.stopname, tt.time, tt.weekend
# from tt
# Inner join stops
# on stops.stopid=tt.stopid
# Inner join routes
# on routes.routeid = tt.routeid
# Inner join directions
# on directions.dirid = tt.direction
# where weekend=false and routename='11А' order by time

# todo: Когда есть номер нахожу направление:
# Select directions.dir
# from tt
# Inner join routes
# on routes.routeid = tt.routeid
# Inner join directions
# on directions.dirid = tt.direction
# where routename='11'
# group by dir

# Когда есть номе и направление нахожу остановки
# Select stops.stopname
# from tt
# Inner join stops
# on stops.stopid=tt.stopid
# Inner join routes
# on routes.routeid = tt.routeid
# Inner join directions
# on directions.dirid = tt.direction
# where routename='1'and weekend=false and dir='Газоаппарат - Бернады' order by time

# Когда есть номе и направление и остановка нахожу время и дальше работем с ним в проге
# Select time
# from tt
# Inner join stops
# on stops.stopid=tt.stopid
# Inner join routes
# on routes.routeid = tt.routeid
# Inner join directions
# on directions.dirid = tt.direction
# where routename='1'and weekend=false and dir='Газоаппарат - Бернады' and stopname='Гоголя'

import telebot
from telebot import types
from bs4 import BeautifulSoup
import config
import requests
import dbworker

# initialization of bot
bot = telebot.TeleBot(config.TOKEN, parse_mode=None)

# handler of /start and /help commands
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to Bus Schedule Bot\nInstructions can be seen here:\ngithub.com",disable_web_page_preview=False)
    dbworker.setAll(message.chat.id,"num","f","fl","l","ll",config.States.S_ENTER_NUMBER)


# todo:make some description
@bot.message_handler(func=lambda message:dbworker.getState(message.chat.id)==config.States.S_ENTER_NUMBER,content_types=['text'])
def numberHandler(message):
    if message.text not in config.NUMBERS_OF_BUSES:
        bot.reply_to(message, "This bus doesn't exist or Creator doesn't know about its emergence")
    else:
        # todo:избавиться от глобальности и заимплементить в дб
        d = parse_main(message, config.URL)
        index = config.NUMBERS_OF_BUSES.index(message.text)

        #creation of direction buttons
        markup = types.InlineKeyboardMarkup()
        itembtn1 = types.InlineKeyboardButton(text=d[index].get('first'),callback_data='direct')
        itembtn2 = types.InlineKeyboardButton(text=d[index].get('last'),callback_data='reverse')
        markup.add(itembtn1,itembtn2)

        dbworker.setAll(message.chat.id,d[index].get("number"),d[index].get("first"),d[index].get("first_link"),\
                        d[index].get("last"), d[index].get("last_link"),config.States.S_CHOOSE_DIR)
        #
        # todo:Write code here
        #
        #todo: на этот реплай повесить кнопочки и изменить значениек в базе данных на ожидает нажатия кнопочки \
        # сейвануть текущее состояние и строчку под index из листа словарей, затем после нажатия кнопки убрать кнопки
        bot.send_message(message.chat.id, "Выберите направление:", reply_markup = markup)


@bot.callback_query_handler(func=lambda call: dbworker.getState(call.message.chat.id)==config.States.S_CHOOSE_DIR)
def callback_inline(call):
    dict = dbworker.getAll(call.message.chat.id)
    if call.message:
        if call.data == 'direct':
            #todo:Поменять markup на остановочный
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=dict.get("first"),reply_markup=None)
        elif call.data == 'reverse':
            #todo:Поменять markup на остановочный
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=dict.get("last"),reply_markup=None)
        dbworker.setState(call.message.chat.id, config.States.S_CHOOSE_BUS_STOP)





# [later] collective function to initialize scheduler of loop() in RefreshDB that will update all tables once a day
def RefreshDB_schedule(url):
    pass


# RUN
bot.polling(none_stop=True)
