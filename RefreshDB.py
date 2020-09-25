# this part should recreate and fill shedule databases
# it will happen every day in 0:00

import psycopg2
from psycopg2.extras import DictCursor
import config
import requests
from bs4 import BeautifulSoup


def loop():
    clear()
    d = parseMain()
    # filling all tables
    fillRoutes(d)
    fillStops(d)
    fillDirection(d)
    fillTT(d)


# эта функия заполняет таблицу routes
def fillRoutes(dictOfbuses):
    conn = config.conDB()
    cur = conn.cursor(cursor_factory=DictCursor)

    for d in dictOfbuses:
        cur.execute("""insert into routes(routename) values(%s)""", (d.get("number"),))
        conn.commit()

    cur.close()
    conn.close()
    print("filling Routes is ended")

# эта функия заполняет таблицу stops, я сделал ее отдельно, чтобы легче было поддерживать
def fillStops(dictOfbuses):
    conn = config.conDB()
    cur = conn.cursor(cursor_factory=DictCursor)

    for d in dictOfbuses:
        ps = parseSecondary(d.get("first_link"))

        for i in ps:
            cur.execute("""
                    SELECT stopID FROM Stops
                    WHERE StopName=%s
                    """, (i.get('stop'),))
            s = cur.fetchone()
            if s == None:
                cur.execute("""
                        INSERT INTO Stops(StopName)
                        VALUES(%s) RETURNING StopId
                        """, (i.get('stop'),))
                conn.commit()
        # заполняет недостающие остановки, которые есть в одном направлении а в другом нет
        ps = parseSecondary(d.get("last_link"))
        for i in ps:
            cur.execute("""
                    SELECT stopID FROM Stops
                    WHERE StopName=%s
                    """, (i.get('stop'),))
            s = cur.fetchone()
            if s == None:
                cur.execute("""
                        INSERT INTO Stops(StopName)
                        VALUES(%s) RETURNING StopId
                        """, (i.get('stop'),))
                conn.commit()

    cur.close()
    conn.close()
    print("filling Stops is ended")

# заполняет таблицу TT попутно заполняя таблицу stops
def fillTT(dictOfbuses):
    for d in dictOfbuses:

        conn = config.conDB()
        cur = conn.cursor(cursor_factory=DictCursor)

        # take dirId from Directions
        cur.execute("""
                SELECT dirID FROM Directions
                WHERE dir=%s
                """, (d.get('first'),))
        first = cur.fetchone()[0]

        cur.execute("""
                        SELECT dirID FROM Directions
                        WHERE dir=%s
                        """, (d.get('last'),))
        last = cur.fetchone()[0]

        cur.close()
        conn.close()

        fillDifDir(d.get("number"), first, d.get('first_link'))
        fillDifDir(d.get("number"), last, d.get('last_link'))
    print("а на этом все")


def fillDifDir(number, Direction, link):
    conn = config.conDB()
    cur = conn.cursor(cursor_factory=DictCursor)

    ps = parseSecondary(link)

    cur.execute("""
            SELECT routeID FROM Routes
            WHERE RouteName=%s
            """, (number,))
    routeid = cur.fetchone()[0]

    for i in ps:
        cur.execute("""
                SELECT stopID FROM Stops
                WHERE StopName=%s
                """, (i.get('stop'),))

        stopId = cur.fetchone()[0]
        # для функции fillTT
        cur.execute("""
                        INSERT INTO tt(RouteId, stopId, time, direction, weekend)
                        VALUES(%s, %s, %s, %s, %s)
                        """, (routeid, stopId, i.get("weekday time"), Direction, False))
        cur.execute("""
                        INSERT INTO tt(RouteId, stopId, time, direction, weekend)
                        VALUES(%s, %s, %s, %s, %s)
                        """, (routeid, stopId, i.get("weekend time"), Direction, True))
        conn.commit()
    cur.close()
    conn.close()


# function that cut string to first nums
def cutStringToFirstNum(str):
    for i in range(0, len(str)):
        if str[i].isdigit():
            ind = i
            break
    return str[ind:]


# Delete all tables to make counter again from zeros and recreate them
def clear():
    conn = config.conDB()
    cur = conn.cursor(cursor_factory=DictCursor)

    cur.execute("DROP TABLE tt CASCADE")
    cur.execute("DROP TABLE routes CASCADE")
    cur.execute("DROP TABLE stops CASCADE")
    cur.execute("DROP TABLE directions CASCADE")
    conn.commit()

    # recreating table Routes
    cur.execute("""
        CREATE TABLE Routes(
            RouteId serial primary key,
            RouteName varchar(5)
        )""")

    # recreating table Stops
    cur.execute("""
        CREATE TABLE Stops(
            StopId serial primary key,
            StopName varchar(30)
        )""")

    # recreating table Directions
    cur.execute("""
        CREATE TABLE Directions(
            dirId serial primary key,
            dir varchar(40)
        )""")

    # recreating table tt
    cur.execute("""
            CREATE TABLE tt(
                id serial primary key,
                RouteId INTEGER REFERENCES Routes(RouteId),
                StopId INTEGER REFERENCES Stops(StopId),
                Time varchar(600),
                Direction INTEGER REFERENCES directions(dirId),
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

    # marker shows us goes this route in weekends or no(1) or shedule is the same in weekdays and weekends(2)
    marker = 0
    if items[0].find_next("div", class_='').get_text(strip=True).find("выходные") == -1:
        marker = 1
    if items[0].find_next("div", class_='').get_text(strip=True).find("раб.") > 0:
        marker = 2
    if items[0].find_next("div", class_='').get_text(strip=True).find("сб.") > 0:
        marker = 3
    # Если такие автобусы как 6 появятся можно добавлять их в это условие а затем обрабатывать ниже
    if exept.find("6") > 0:
        marker = 4

    for item in items:
        wd = item.find_next("div", class_='').find_next("p").get_text(strip=True)
        we = item.find_next("div", class_='').find_next("p").find_next("p").get_text(strip=True)

        # check is this only weekday route
        if marker == 0:
            stops.append({
                'stop': item.find("a", class_='list_ost').get_text(strip=True),
                'weekday time': wd,
                'weekend time': we
            })
        elif marker == 1:
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
            if item.find("a", class_='list_ost').get_text(strip=True) == "Тельмы" or item.find("a",
                                                                                               class_='list_ost').get_text(
                strip=True) == "Московское шоссе":
                stops.append({
                    'stop': item.find("a", class_='list_ost').get_text(strip=True),
                    'weekday time': wd,
                    'weekend time': '-'
                })
            else:
                stops.append({
                    'stop': item.find("a", class_='list_ost').get_text(strip=True),
                    'weekday time': wd,
                    'weekend time': we
                })

    return stops


# get html from url using requests
def get_html(url):
    r = requests.get(url, headers=config.HEADERS)
    return r


def fillDirection(dictOfbuses):
    conn = config.conDB()
    cur = conn.cursor(cursor_factory=DictCursor)

    for d in dictOfbuses:
        cur.execute("""insert into directions(dir) values(%s)""", (d.get("first"),))
        cur.execute("""insert into directions(dir) values(%s)""", (d.get("last"),))
        conn.commit()

    cur.close()
    conn.close()
    print("filling Directions is ended")


loop()
