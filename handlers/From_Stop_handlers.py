import hashlib
import logging
from telebot import types

import RefreshDB
import etc
import timeOperator
import userTableWorker
from etc import bot
from handlers.All_relatedTo_Favorites import GetFavoritesMarkup

"""
    Branch where our initial point is some stop
"""


@bot.callback_query_handler(func=lambda call: userTableWorker.getState(call.message.chat.id) == etc.States.S2_STOP_HANDLER.value)
def callback_inline_s2_Stop_Handler(call):
    # logging.info("%s is in from stop branch",call.message.chat.id )
    # проверка на обновление дб
    if RefreshDB.isRefreshing():
        bot.send_message(call.message.chat.id,text="Подождите пару минут, идет обновление базы данных")
        return 0

    if call.message:
        stop = call.data
        markup = types.InlineKeyboardMarkup()
        # get all routes that coming trouth this stop
        routes = userTableWorker.getRouteNumbers(stop)

        buttons = generateButtonList(routes,buttInRow=5)

        for b in buttons:
            markup.row(*b)

        history = stop + '\nВыберите номер автобуса:'
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=history,reply_markup=markup)

        # updating table userdecision
        userTableWorker.setAll(call.message.chat.id, None, None, stop, etc.States.S2_ROUTE_HANDLER.value)


@bot.callback_query_handler(func=lambda call: userTableWorker.getState(call.message.chat.id) == etc.States.S2_ROUTE_HANDLER.value)
def callback_inline_s2_routes_handler(call):
    # проверка на обновление дб
    if RefreshDB.isRefreshing():
        bot.send_message(call.message.chat.id,text="Подождите пару минут, идет обновление базы данных")
        return 0

    if call.message:
        stop = userTableWorker.getAll(call.message.chat.id)[3]
        route = call.data
        dirs = userTableWorker.getS2Directions(route,stop)

        markup = types.InlineKeyboardMarkup()
        for d in dirs:
            markup.add(types.InlineKeyboardButton(text=d,callback_data=hashlib.md5(d.encode()).hexdigest()))

        history = stop + '/' + route + "\nВыберите направление:"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=history, reply_markup=markup)

        userTableWorker.setAll(call.message.chat.id, route, None, stop, etc.States.S2_DIR_HANDLER.value)


@bot.callback_query_handler(func=lambda call: userTableWorker.getState(call.message.chat.id) == etc.States.S2_DIR_HANDLER.value)
def callback_inline_s2_dir_handler(call):
    # проверка на обновление дб
    if RefreshDB.isRefreshing():
        bot.send_message(call.message.chat.id,text="Подождите пару минут, идет обновление базы данных")
        return 0

    if call.message:
        route = userTableWorker.getAll(call.message.chat.id)[1]
        stop = userTableWorker.getAll(call.message.chat.id)[3]
        dirs = userTableWorker.getS2Directions(route,stop)

        # get choosen direction
        for d in dirs:
            if hashlib.md5(d.encode()).hexdigest() == call.data:
                dir = d
                break

        weekdayTime = userTableWorker.getTime(route,False,dir,stop)[0]
        weekendTime = userTableWorker.getTime(route,True,dir,stop)[0]
        closestTime = timeOperator.getTime(weekdayTime,weekendTime)

        if weekendTime == '-':
            weekendTime = "в выходные дни: маршрутов нет"

        history = stop + '/' + route + '/' + dir
        clos_time = "Ближайшее время: " + closestTime
        Time = weekdayTime+'\n'+weekendTime

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=history,reply_markup=None)
        bot.send_message(call.message.chat.id,text=clos_time)
        bot.send_message(call.message.chat.id,text=Time,reply_markup=GetFavoritesMarkup(call.message))

        # reset table userdecision to begining
        userTableWorker.setAll(call.message.chat.id, None, None, None, etc.States.S_ENTER_NUMBER_OR_STOP.value)


# функция генерируящая лист из листов для использования в markup
def generateButtonList(numList,buttInRow):
    tmp = []
    ll = []
    begin = 0

    for i in range(0,len(numList)+1,buttInRow):
        if i == 0:
            continue
        else:
            for j in range(0, buttInRow):
                tmp.append(types.InlineKeyboardButton(text=numList[begin+j], callback_data=numList[begin+j]))
            ll.append(tmp)
            tmp = []
            begin = i

    # counting remaining count
    numofrem = len(numList)%buttInRow
    # add remaining numbers list
    for j in range(0, numofrem):
        tmp.append(types.InlineKeyboardButton(text=numList[begin + j], callback_data=numList[begin + j]))
    ll.append(tmp)

    return ll