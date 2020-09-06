import telebot
from telebot import types
from bs4 import BeautifulSoup
import config
import requests

# initialization of bot
bot = telebot.TeleBot(config.TOKEN, parse_mode=None)
#global dictionary and index
d = []
index = 0

# handler of /start and /help commands
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hello, with my help u can see Buses' shedule of Brest(not now)")


# todo:make some description
@bot.message_handler(content_types=['text'])
def numberHandler(message):
    if message.text not in config.NUMBERS_OF_BUSES:
        bot.reply_to(message, "This bus doesn't exist or Creator doesn't know about its emergence")
    else:
        global d,index
        d = parse_main(message, config.URL)
        index = config.NUMBERS_OF_BUSES.index(message.text)
        markup = types.InlineKeyboardMarkup()
        itembtn1 = types.InlineKeyboardButton(text=d[index].get('first'),callback_data='direct')
        itembtn2 = types.InlineKeyboardButton(text=d[index].get('last'),callback_data='reverse')
        markup.add(itembtn1,itembtn2)
        #
        # todo:Write code here
        #
        #todo: на этот реплай повесить кнопочки и изменить значениек в базе данных на ожидает нажатия кнопочки \
        # сейвануть текущее состояние и строчку под index из листа словарей, затем после нажатия кнопки убрать кнопки
        bot.send_message(message.chat.id, "Выберите направление:", reply_markup = markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == 'direct':
            #todo:Поменять markup на остановочный
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=d[index].get("first"),reply_markup=None)
        elif call.data == 'reverse':
            #todo:Поменять markup на остановочный
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=d[index].get("last"),reply_markup=None)

# getting html for future processing with help of requests library
def get_html(url):
    r = requests.get(url, headers=config.HEADERS)
    return r


# parse content from http://ap1.brest.by/shelude/
def get_content_main(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_="collapse fade")
    buses = []
    i = 0
    for item in items:
        buses.append({
            'number': config.NUMBERS_OF_BUSES[i],
            'first': item.find_next("div", class_='first').get_text(strip=True),
            'first_link': 'http://ap1.brest.by' + item.find("a").get('href'),
            'last': item.find_next("div", class_='last').get_text(strip=True),
            'last_link': 'http://ap1.brest.by' + item.find_next("div", class_='last').find("a").get('href')

        })
        i += 1
    print(buses)
    return buses


# parse content from shedule page of every single bus
def get_content_shedule(html):
    pass


# collective function to parse information of buses and their direction to list of dicts
def parse_main(url, message):
    html = get_html(config.URL)
    if html.status_code != 200:
        bot.send_message(message.user.id,"Error, tell to Creator to to rewrite parser")
    dict = get_content_main(html.text)
    return dict


# collective function to parse information of shedule on every bus stop to 'list of dicts'
def parse_shedule(url):
    pass


# RUN
bot.polling(none_stop=True)
