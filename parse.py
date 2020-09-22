# this part should recreate and fill shedule database
# in the beginning it should recreate Routes table and fill it with RouteId and RouteName
# then it should recreate Stops and TimeTable and

# каждый раз когда добавляется автобус с остановкой программа берет остановку и если такой нет добавляет ее в Stops и
# возвращает StopID, если же есть - возвращает ID существующей,
# c RouteID проще, просто искать данный маршрут в Routes и добавлять соответствующий RouteID

# it will be done every day in 0:00

import psycopg2
from psycopg2.extras import DictCursor
import config
import requests
from bs4 import BeautifulSoup

#todo: изучить FOREIGN KEY

conn = psycopg2.connect(
    host="localhost",
    database="timetable",
    user="postgres",
    password="r10t1337")

cur = conn.cursor(cursor_factory=DictCursor)



cur.close()
conn.close()

def loop():
    d = getDict()
    fillRoutes(d)
    fillTT(d)

# эта функия парсит список словарей как из main из которого все потом будут браться
def getDict():
    pass

# эта функия заполняет таблицу routes
def fillRoutes():
    pass

# заполняет таблицу TT попутно заполняя таблицу stops
def fillTT():
    pass




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
    return buses

# collective function to parse information of buses and their direction to list of dicts
def parse_main():
    html = get_html(config.URL)
    if html.status_code != 200:
        print("something is not good with parsed page")
    dict = get_content_main(html.text)
    return dict

parse_main()