import hashlib
import logging

from telebot import types

import RefreshDB
import etc
import timeOperator
import userTableWorker
from handlers.All_relatedTo_Favorites import GetFavoritesMarkup
from etc import bot


"""
    Branch where our initial point is some number or reply button with number
"""


# logging.basicConfig(filename="sample.log", level=logging.INFO)

# handle direction button and give n Stops buttons
@bot.callback_query_handler(
    func=lambda call: userTableWorker.getState(call.message.chat.id) == etc.States.S_CHOOSE_DIR.value)
def callback_inline_Directions_Handler(call):
    # logging.info("%s is in from number branch",call.message.chat.id )
    # проверка на обновление дб
    if RefreshDB.isRefreshing():
        bot.send_message(call.message.chat.id,text="Подождите пару минут, идет обновление базы данных")
        return 0

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
        userTableWorker.setAll(call.message.chat.id, all[1], dir, None, etc.States.S_CHOOSE_BUS_STOP.value)


# giving a time to user and return to Entering number state
@bot.callback_query_handler(
    func=lambda call: userTableWorker.getState(call.message.chat.id) == etc.States.S_CHOOSE_BUS_STOP.value)
def callback_inline_Stops_Handler(call):
    # проверка на обновление дб
    if RefreshDB.isRefreshing():
        bot.send_message(call.message.chat.id,text="Подождите пару минут, идет обновление базы данных")
        return 0

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
        bot.send_message(call.message.chat.id,text=Time, reply_markup=GetFavoritesMarkup(call.message))

        # reset table userdecision to begining
        userTableWorker.setAll(call.message.chat.id, None, None, None, etc.States.S_ENTER_NUMBER_OR_STOP.value)