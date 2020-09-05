import telebot
from bs4 import BeautifulSoup
from const import TOKEN, URL, NUMBERS_OF_BUSES, HEADERS
import requests

# initialization of bot
bot = telebot.TeleBot(TOKEN, parse_mode=None)


# handler of /start and /help commands
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hello, with my help u can see Buses' shedule of Brest(not now)")


# todo:make some description
@bot.message_handler(content_types=['text'])
def numberHandler(message):
    if message.text not in NUMBERS_OF_BUSES:
        bot.reply_to(message, "This bus doesn't exist or Creator doesn't know about its emergence")
    else:
        d = parse_main(URL)
        index = NUMBERS_OF_BUSES.index(message.text)

        print(d[index])

        #
        # todo:Write code here
        #
        #
        bot.reply_to(message, "YAY")


# getting html for future processing with help of requests library
def get_html(url):
    r = requests.get(url, headers=HEADERS)
    return r


# parse content from http://ap1.brest.by/shelude/
def get_content_main(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_="collapse fade")
    buses = []
    i = 0
    for item in items:
        buses.append({
            'number': NUMBERS_OF_BUSES[i],
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
def parse_main(url):
    html = get_html(URL)
    if html.status_code != 200:
        bot.send_message("Error, tell to Creator to to rewrite parser")
    dict = get_content_main(html.text)
    return dict


# collective function to parse information of shedule on every bus stop to 'list of dicts'
def parse_shedule(url):
    pass


# RUN
bot.polling(none_stop=True)
