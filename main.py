import traceback

import telebot
from telebot import types
from bs4 import BeautifulSoup

import RefreshDB
import config

import userTableWorker
import hashlib
import timeOperator
import time
import threading

import flask
from flask import Flask,request
import requests

# initialization of bot
app = Flask(__name__)
bot = telebot.TeleBot(config.TOKEN, parse_mode=None)



@app.route("/", methods=["HEAD","GET"])
def index():
    return ''


# steal from official github, setting the webhook to ngrock tunnel server
@app.route('/', methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


# handler of /start and /reset commands
@bot.message_handler(commands=['start', 'reset'])
def send_welcome(message):
    # instead of gitub.com it should open my github with this project
    bot.reply_to(message, "Добро Пожаловать в Bus Schedule Bot\nКак пользоваться:\ngithub.com",
                 disable_web_page_preview=False)

    userTableWorker.setState(message.chat.id, config.States.S_ENTER_NUMBER_OR_STOP.value)

# get directions from table and make 2 buttons inside bot
@bot.message_handler(func=lambda message: userTableWorker.getState(message.chat.id) == config.States.S_ENTER_NUMBER_OR_STOP.value,
                     content_types=['text'])
def numberandStopHandler(message):
    numberOfSymbolstoFindSimilar = 4
    # проверка на обновление дб
    if RefreshDB.isRefreshing():
        bot.send_message(message.chat.id,text="Подождите пару минут, идет обновление базы данных")
        return 0

    if message.text not in config.NUMBERS_OF_BUSES:
        if len(message.text)<numberOfSymbolstoFindSimilar:
            bot.reply_to(message,
                         "Попытайтесь написать русскими буквами или такой остановки нет, или такого номера автобуса не "
                         "существует, или Создатель не знает об их появлении.\n"
                         "Если же вы пытались искать по остановке, то нужно как минимум 4 символа")
        else:
            similarStops = userTableWorker.getSimilarStops(message.text)
            if similarStops == []:
                bot.reply_to(message,"Такой остановки не сущеставует")
            else:
                stopsHandler(message, similarStops)
    else:
        numberHandler(message)

def numberHandler(message):
    dirs = userTableWorker.getDirections(message.text)

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
    userTableWorker.setAll(message.chat.id, message.text, None, None, config.States.S_CHOOSE_DIR.value)

def stopsHandler(message, similarStops):
    # creation of stops buttons
    markup = types.InlineKeyboardMarkup()
    for sS in similarStops:
        markup.add(types.InlineKeyboardButton(text=sS, callback_data=sS))

    bot.send_message(message.chat.id, "\nВыберите остановку:", reply_markup=markup)

    # updating table userdecision
    userTableWorker.setAll(message.chat.id, None, None, None, config.States.S2_STOP_HANDLER.value)

@bot.callback_query_handler(func=lambda call: userTableWorker.getState(call.message.chat.id) == config.States.S2_STOP_HANDLER.value)
def callback_inline_s2_Stop_Handler(call):
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

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Выберите номер автобуса',reply_markup=markup)

        # updating table userdecision
        userTableWorker.setAll(call.message.chat.id, None, None, stop, config.States.S2_ROUTE_HANDLER.value)


@bot.callback_query_handler(func=lambda call: userTableWorker.getState(call.message.chat.id) == config.States.S2_ROUTE_HANDLER.value)
def callback_inline_routes_handler(call):
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

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Выберите направление:", reply_markup=markup)

        userTableWorker.setAll(call.message.chat.id, route, None, stop, config.States.S2_DIR_HANDLER.value)


# handle direction button and give n Stops buttons
@bot.callback_query_handler(
    func=lambda call: userTableWorker.getState(call.message.chat.id) == config.States.S_CHOOSE_DIR.value)
def callback_inline_Directions_Handler(call):
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
        userTableWorker.setAll(call.message.chat.id, all[1], dir, None, config.States.S_CHOOSE_BUS_STOP.value)


# giving a time to user and return to Entering number state
@bot.callback_query_handler(
    func=lambda call: userTableWorker.getState(call.message.chat.id) == config.States.S_CHOOSE_BUS_STOP.value)
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
        bot.send_message(call.message.chat.id,text=Time)

        # reset table userdecision to begining
        userTableWorker.setAll(call.message.chat.id, None, None, None, config.States.S_ENTER_NUMBER_OR_STOP.value)


# функция генерируящая лист из листов для использования в markup
def generateButtonList(numList,buttInRow):
    tmp = []
    ll = []
    begin = 0

    for i in range(0,len(numList),buttInRow):
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


# [later] collective function to initialize scheduler of loop() in RefreshDB that will update all tables once a day
def RefreshDB_schedule(delay, task):
    next_time = time.time() + delay
    task()
    while True:
        time.sleep(max(0, next_time - time.time()))
        try:
            task()
        except Exception:
            traceback.print_exc()

        # skip tasks if we are behind schedule:
        next_time += (time.time() - next_time) // delay * delay + delay


# RUN
# threading.Thread(target=lambda: RefreshDB_schedule(24*60*60, RefreshDB.loop)).start()

bot.remove_webhook()
time.sleep(0.1)
bot.set_webhook(config.NGROK)
app.run()
