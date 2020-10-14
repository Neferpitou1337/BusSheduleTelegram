import logging

from telebot import types

import etc
import favoritesdb
import userTableWorker

from etc import bot

"""
    Configure Favorites Reply Markup and Get Favorites Reply Markup
"""



def GetFavoritesMarkup(message):
    favs = favoritesdb.getFavorites(message.chat.id)

    markup = types.ReplyKeyboardMarkup(row_width=3,resize_keyboard=1,one_time_keyboard=True)
    if favs == []:
        markup.row(types.KeyboardButton("не сущ."), types.KeyboardButton("не сущ."),types.KeyboardButton("не сущ."))
        markup.row(types.KeyboardButton("/config"))
    else:
        markup.row(types.KeyboardButton(favs[0]),types.KeyboardButton(favs[1]),types.KeyboardButton(favs[2]))
        markup.row(types.KeyboardButton("/config"))
    return markup


@bot.message_handler(commands=['config'])
def configure(message):
    # logging.info("%s is in favorite handler", message.chat.id)
    bot.send_message(message.chat.id, "Введите 3 своих приоритетных автобуса через пробел", reply_markup=types.ReplyKeyboardRemove(selective=False))
    userTableWorker.setState(message.chat.id, etc.States.ENTER_FAV.value)

@bot.message_handler(func=lambda message: userTableWorker.getState(message.chat.id) == etc.States.ENTER_FAV.value,
                     content_types=['text'])
def favorites(message):
    count = 0
    # запрос удаляя при этом старую reply клавиатуру
    list_of_fav_buses = message.text.upper().split(' ')
    for bus in list_of_fav_buses:
        if bus in etc.NUMBERS_OF_BUSES:
            count+=1

    if count >= 3:
        favoritesdb.setFavorites(message.chat.id, *list_of_fav_buses)

        bot.send_message(message.chat.id, "Конфигурация приоритетных автобусов закончена",
                         reply_markup=GetFavoritesMarkup(message))
        userTableWorker.setState(message.chat.id, etc.States.S_ENTER_NUMBER_OR_STOP.value)
    else:
        bot.send_message(message.chat.id, "Ошибка. Введите 3 своих приоритетных автобуса через пробел")

