import telebot
from bs4 import BeautifulSoup
bot = telebot.TeleBot("1267389438:AAHZH3YY33nveMK2VM8qsCMLYORYp6mqOXg", parse_mode=None)
import requests
URL = 'http://ap1.brest.by/shelude'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0','accept':'*/*'}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Hello, with my help u can see Buses' shedule of Brest(not now)")


@bot.message_handler(content_types=['text'])
def numberHandler(message):
    pass


def get_html(url):
    r = requests.get(url,headers = HEADERS)
    return r

def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_="first")
    buses = []
    for item in items:
        buses.append({
            'number': item.find_next("div").get_text()
        })
    print(buses)

def parse(url):
    html = get_html(URL)
    if html.status_code !=200:
        bot.send_message("Error, try to rewrite parser")
    get_content(html.text)



#RUN
parse(URL)
bot.polling(none_stop=True)
