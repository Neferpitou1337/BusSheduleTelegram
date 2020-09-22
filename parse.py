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

# todo: изучить FOREIGN KEY

# conn = psycopg2.connect(
#     host="localhost",
#     database="timetable",
#     user="postgres",
#     password="r10t1337")
#
# cur = conn.cursor(cursor_factory=DictCursor)
#
# cur.close()
# conn.close()


def loop():
    clear()
    d = getDict()
    fillRoutes(d)
    # fillTT(d)


# эта функия заполняет таблицу routes
def fillRoutes(dict):
    conn = psycopg2.connect(
        host="localhost",
        database="timetable",
        user="postgres",
        password="r10t1337")
    cur = conn.cursor(cursor_factory=DictCursor)

    for d in dict:
        cur.execute("""insert into routes(routename) values(%s)""",(d.get("number"),))
        conn.commit()

    cur.close()
    conn.close()


# заполняет таблицу TT попутно заполняя таблицу stops
def fillTT(d):
    pass

# Delete all tables to make counter again from zeros and recreate them
def clear():
    conn = psycopg2.connect(
        host="localhost",
        database="timetable",
        user="postgres",
        password="r10t1337")
    cur = conn.cursor(cursor_factory=DictCursor)

    cur.execute("DROP TABLE tt CASCADE")
    cur.execute("DROP TABLE routes CASCADE")
    cur.execute("DROP TABLE stops CASCADE")
    conn.commit()

    cur.execute("""
    CREATE TABLE Routes(
        RouteId serial primary key,
        RouteName varchar(5)
    )
    """)
    cur.execute("""
        CREATE TABLE Stops(
            StopId serial primary key,
            StopName varchar(15)
        )
        """)

    cur.execute("""
            CREATE TABLE tt(
                RouteId INTEGER REFERENCES Routes(RouteId),
                StopId serial REFERENCES Stops(StopId),
                Time varchar(255),
                Direction varchar(30),
                Weekend bool
            )
            """)
    conn.commit()
    cur.close()
    conn.close()

# collective function to parse information of buses and their direction to list of dicts
def getDict():
    html = get_html(config.URL)
    if html.status_code != 200:
        print("something is not good with parsed page")

    # parse content from http://ap1.brest.by/shelude/
    soup = BeautifulSoup(html.text, 'html.parser')
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
    print('\n\n')
    return buses


def get_html(url):
    r = requests.get(url, headers=config.HEADERS)
    return r

loop()
# # parse content from http://ap1.brest.by/shelude/
# def get_content_main(html):
#     soup = BeautifulSoup(html, 'html.parser')
#     items = soup.find_all('div', class_="collapse fade")
#     buses = []
#     i = 0
#     for item in items:
#         buses.append({
#             'number': config.NUMBERS_OF_BUSES[i],
#             'first': item.find_next("div", class_='first').get_text(strip=True),
#             'first_link': 'http://ap1.brest.by' + item.find("a").get('href'),
#             'last': item.find_next("div", class_='last').get_text(strip=True),
#             'last_link': 'http://ap1.brest.by' + item.find_next("div", class_='last').find("a").get('href')
#
#         })
#         i += 1
#     return buses


# print(getDict())
