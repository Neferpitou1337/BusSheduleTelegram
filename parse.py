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
    d = parseMain()
    fillRoutes(d)
    # fillTT(d)


# эта функия заполняет таблицу routes
def fillRoutes(dictOfbuses):
    conn = psycopg2.connect(
        host="localhost",
        database="timetable",
        user="postgres",
        password="r10t1337")
    cur = conn.cursor(cursor_factory=DictCursor)

    for d in dictOfbuses:
        cur.execute("""insert into routes(routename) values(%s)""",(d.get("number"),))
        conn.commit()

    cur.close()
    conn.close()

def fillStops(url):
    pass

# заполняет таблицу TT попутно заполняя таблицу stops
def fillTT(dictOfbuses):
    pass

# function that cut string to first nums
def cutStringToFirstNum(str):
    for i in range(0, len(str)):
        if str[i].isdigit():
            ind = i
            break
    return str[ind:]

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
        )""")

    cur.execute("""
        CREATE TABLE Stops(
            StopId serial primary key,
            StopName varchar(30)
        )""")

    cur.execute("""
            CREATE TABLE tt(
                RouteId INTEGER REFERENCES Routes(RouteId),
                StopId serial REFERENCES Stops(StopId),
                Time varchar(600),
                Direction varchar(40),
                Weekend bool
            )""")
    conn.commit()
    cur.close()
    conn.close()

# collective function to parse information of buses and their direction to list of dicts
def parseMain():
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

# parse content of stops and times of bus by url
def parseSecondary(url):
    html = get_html(url)
    if html.status_code != 200:
        print("something is not good with parsed page")

    # parse content from http://ap1.brest.by/shelude/avtobus-number/direction
    soup = BeautifulSoup(html.text, 'html.parser')
    # bus 6 is the exeption and we should process this exeption properly in marker == 4
    exept = soup.find_all('div', class_="content-category")[0].find("h1").get_text(strip=True)
    items = soup.find_all('div', class_="cat_item_page")
    stops = []


    #marker shows us goes this route in weekends or no(1) or shedule is the same in weekdays and weekends(2)
    marker = 0
    if items[0].find_next("div", class_= '').get_text(strip = True).find("выходные") == -1:
        marker = 1
    if items[0].find_next("div", class_= '').get_text(strip = True).find("раб.") > 0:
        marker = 2
    if items[0].find_next("div", class_= '').get_text(strip = True).find("сб.") > 0:
        marker = 3
    # Если такие автобусы как 6 появятся можно добавлять их в это условие а затем обрабатывать ниже
    if exept.find("6")>0:
        marker = 4

    for item in items:
        wd = item.find_next("div", class_= '').find_next("p").get_text(strip=True)
        we = item.find_next("div", class_= '').find_next("p").find_next("p").get_text(strip=True)

        # check is this only weekday route
        if marker == 0:
            stops.append({
                'stop': item.find("a", class_= 'list_ost').get_text(strip=True),
                'weekday time': wd,
                'weekend time': we
            })
        elif marker == 1 :
            stops.append({
                'stop': item.find("a", class_='list_ost').get_text(strip=True),
                'weekday time': wd,
                'weekend time': '-'
            })
        elif marker == 2:
            tmp = cutStringToFirstNum(wd)
            stops.append({
                'stop': item.find("a", class_='list_ost').get_text(strip=True),
                'weekday time': 'в рабочие дни:' + tmp,
                'weekend time': 'в выходные дни:' + tmp
            })
        elif marker == 3:
            tmp = cutStringToFirstNum(wd)
            stops.append({
                'stop': item.find("a", class_='list_ost').get_text(strip=True),
                'weekday time': 'в рабочие дни:' + tmp,
                'weekend time': 'в субботу:' + tmp
            })
        # обраюотка исключения автобуса №6
        else:
            if item.find("a", class_= 'list_ost').get_text(strip=True) == "Тельмы" or item.find("a", class_= 'list_ost').get_text(strip=True) == "Московское шоссе":
                stops.append({
                    'stop': item.find("a", class_='list_ost').get_text(strip=True),
                    'weekday time': wd,
                    'weekend time': '-'
                })
            else:
                stops.append({
                    'stop': item.find("a", class_= 'list_ost').get_text(strip=True),
                    'weekday time': wd,
                    'weekend time': we
                })

    return stops



def get_html(url):
    r = requests.get(url, headers=config.HEADERS)
    return r

# loop()
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

