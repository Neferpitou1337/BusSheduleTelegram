import hashlib
import logging

from telebot import types

import RefreshDB
import etc
import userTableWorker
from etc import bot
# logging.basicConfig(filename="sample.log", level=logging.INFO)
"""
    Fork
"""

# get directions from table and make 2 buttons inside bot
@bot.message_handler(func=lambda message: userTableWorker.getState(message.chat.id) == etc.States.S_ENTER_NUMBER_OR_STOP.value,
                     content_types=['text'])
def numberandStopHandler(message):
    # logging.info("%s is in fork", message.chat.id)
    stopslesserthan4 = ["БТИ","ЦУМ","ЦМТ","БТК","АП","ТЭЦ","ЦГБ","ПСО","ФОК","ДСУ"]
    numberOfSymbolstoFindSimilar = 4
    # проверка на обновление дб
    if RefreshDB.isRefreshing():
        bot.send_message(message.chat.id,text="Подождите пару минут, идет обновление базы данных")
        return 0

    if message.text.upper() not in etc.NUMBERS_OF_BUSES:
        if len(message.text)<numberOfSymbolstoFindSimilar:
            if message.text.upper() not in stopslesserthan4:
                bot.reply_to(message,
                             "Попытайтесь написать русскими буквами или такой остановки нет, или такого номера автобуса не "
                             "существует, или Создатель не знает об их появлении.\n"
                             "Если же вы пытались искать по остановке, то нужно как минимум 4 символа")
            else:
                stopsHandler(message, [message.text.upper()])
        else:
            similarStops = userTableWorker.getSimilarStops(message.text)
            if similarStops == []:
                bot.reply_to(message,"Такой остановки не сущеставует")
            else:
                stopsHandler(message, similarStops)
    else:
        numberHandler(message)

def numberHandler(message):
    route = message.text.upper()
    dirs = userTableWorker.getDirections(route)

    # creation of direction buttons
    markup = types.InlineKeyboardMarkup()

    # using hash to define dirs
    hash_dirs0 = hashlib.md5(dirs[0].encode())
    hash_dirs1 = hashlib.md5(dirs[1].encode())

    itembtn1 = types.InlineKeyboardButton(text=dirs[0], callback_data=hash_dirs0.hexdigest())
    itembtn2 = types.InlineKeyboardButton(text=dirs[1], callback_data=hash_dirs1.hexdigest())
    markup.add(itembtn1)
    markup.add(itembtn2)

    bot.send_message(message.chat.id, message.text + "\nВыберите направление:", reply_markup=markup)

    # updating table userdecision
    userTableWorker.setAll(message.chat.id, route, None, None, etc.States.S_CHOOSE_DIR.value)

def stopsHandler(message, similarStops):
    # creation of stops buttons
    markup = types.InlineKeyboardMarkup()
    for sS in similarStops:
        markup.add(types.InlineKeyboardButton(text=sS, callback_data=sS))

    bot.send_message(message.chat.id, "\nВыберите остановку:", reply_markup=markup)

    # updating table userdecision
    userTableWorker.setAll(message.chat.id, None, None, None, etc.States.S2_STOP_HANDLER.value)