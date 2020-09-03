import telebot
from bs4 import BeautifulSoup
bot = telebot.TeleBot("1267389438:AAHZH3YY33nveMK2VM8qsCMLYORYp6mqOXg", parse_mode=None)
import requests


URL = 'http://ap1.brest.by/shelude'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0','accept':'*/*'}
NUMBERS_OF_BUSES = \
        ['1',
         '1А',
         '2',
         '2А',
         '3',
         '5',
         '6',
         '7',
         '8',
         '9',
         '10',
         '11',
         '11А',
         '12',
         '12А',
         '13',
         '13А',
         '14',
         '15A',
         '15Б',
         '15B',
         '16',
         '17',
         '18',
         '19',
         '20',
         '21',
         '21A',
         '21Б',
         '22',
         '23',
         '23А',
         '23Б',
         '24',
         '25',
         '26',
         '27',
         '27А',
         '29',
         '30',
         '30А',
         '31',
         '32',
         '33',
         '34',
         '35',
         '36',
         '37',
         '37A',
         '38',
         '39',
         '39А',
         '39Б',
         '40',
         '41',
         '42',
         '43',
         '44',
         '44А',
         '45',
         '46',
         '47']

#handler of /start and /help commands
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Hello, with my help u can see Buses' shedule of Brest(not now)")

#todo:make some description
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

#getting html for future processing with help of requests library
def get_html(url):
    r = requests.get(url,headers = HEADERS)
    return r

#parse content from http://ap1.brest.by/shelude/
def get_content_main(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_="collapse fade")
    buses = []
    i = 0
    for item in items:
        buses.append({
            'number': NUMBERS_OF_BUSES[i],
            'first': item.find_next("div", class_='first').get_text(strip = True),
            'first_link': 'http://ap1.brest.by' + item.find("a").get('href'),
            'last': item.find_next("div", class_='last').get_text(strip = True),
            'last_link': 'http://ap1.brest.by' + item.find_next("div", class_='last').find("a").get('href')

        })
        i+=1
    print(buses)
    return buses

#parse content from shedule page of every single bus
def get_content_shedule(html):
    pass

#collective function to parse information of buses and their direction to list of dicts
def parse_main(url):
    html = get_html(URL)
    if html.status_code !=200:
        bot.send_message("Error, tell to Creator to to rewrite parser")
    dict = get_content_main(html.text)
    return dict

#collective function to parse information of shedule on every bus stop to 'list of dicts'
def parse_shedule(url):
    pass




#RUN
bot.polling(none_stop=True)
