import psycopg2
import config
from psycopg2.extras import DictCursor

# Working with tables trough functions

def getState(user_id):
    conn = config.conDB()
    cur = conn.cursor(cursor_factory=DictCursor)

    cur.execute("""
        SELECT status
        From userdecision
        Where userid=%s
    """,(user_id,))

    try:
        status = cur.fetchone()[0]
    except:
        print("Ошибка в getState()")
        status = 0

    cur.close()
    conn.close()
    print("getState()")
    return status


def setState(user_id, state):
    conn = config.conDB()
    cur = conn.cursor(cursor_factory=DictCursor)

    cur.execute("""
            INSERT INTO 
            userdecision(userid,status)
            VALUES(%s,%s)
            ON CONFLICT(userid) DO UPDATE
            SET status=%s
        """, (user_id,state,state,))

    conn.commit()
    cur.close()
    conn.close()
    print("setState()")


def getAll(user_id):
    conn = config.conDB()
    cur = conn.cursor(cursor_factory=DictCursor)

    cur.execute("""
                SELECT * FROM 
                userdecision
                WHERE userid=%s
            """, (user_id,))
    row = cur.fetchone()

    cur.close()
    conn.close()
    print("setState()")
    return row


def setAll(user_id, route, dir, stop, status):
    conn = config.conDB()
    cur = conn.cursor(cursor_factory=DictCursor)

    cur.execute("""
            INSERT INTO 
            userdecision(userid, route, direction, stop ,status)
            VALUES(%s, %s, %s, %s, %s)
            ON CONFLICT(userid) DO UPDATE
            SET route=%s, direction=%s, stop=%s, status=%s
        """, (user_id, route, dir, stop, status,
                            route, dir, stop, status,))
    conn.commit()

    cur.close()
    conn.close()
    print("setAll()")

# изначально по номеру
def getDirections(routenumber):
    conn = config.conDB()
    cur = conn.cursor(cursor_factory=DictCursor)

    cur.execute("""
            SELECT directions.dir
            FROM tt
            INNER JOIN routes
            ON routes.routeid = tt.routeid
            INNER JOIN directions
            ON directions.dirid = tt.direction
            WHERE routename=%s
            GROUP BY dir
        """, (routenumber,))

    tmpdirs = []

    dirs = cur.fetchall()
    for d in dirs:
        tmpdirs.append(''.join(d))

    cur.close()
    conn.close()
    return tmpdirs

def getStops(routenumber, direction):
    conn = config.conDB()
    cur = conn.cursor(cursor_factory=DictCursor)

    cur.execute("""
            Select stops.stopname
            from tt
            Inner join stops
            on stops.stopid=tt.stopid
            Inner join routes
            on routes.routeid = tt.routeid
            Inner join directions
            on directions.dirid = tt.direction
            where routename=%s and weekend=false and dir=%s
            """, (routenumber, direction,))

    tmpdirs = []
    stops = cur.fetchall()

    if stops[0][0] == direction[:direction.find('-')].strip(' ') or stops[-1][0] == direction[direction.find('-'):].strip(' '):
        for s in stops:
            tmpdirs.append(''.join(s))
        cur.close()
        conn.close()
        return tmpdirs
    else:
        cur.execute("""
                Select stops.stopname
                from tt
                Inner join stops
                on stops.stopid=tt.stopid
                Inner join routes
                on routes.routeid = tt.routeid
                Inner join directions
                on directions.dirid = tt.direction
                where routename=%s and weekend=false and dir=%s
                order by time
                """, (routenumber, direction,))

        stops = cur.fetchall()
        for s in stops:
            tmpdirs.append(''.join(s))
        cur.close()
        conn.close()
        return tmpdirs

def getTime(routenumber, weekend, direction, stop):
    conn = config.conDB()
    cur = conn.cursor(cursor_factory=DictCursor)

    cur.execute("""
            SELECT time
            FROM tt
            INNER JOIN stops
            ON stops.stopid = tt.stopid
            INNER JOIN routes
            ON routes.routeid = tt.routeid
            INNER JOIN directions
            ON directions.dirid = tt.direction
            WHERE routename = %s and dir = %s and stopname = %s and weekend = %s
    """,(routenumber, direction, stop, weekend,))
    time = cur.fetchall()[0]

    cur.close()
    conn.close()
    return time

# изначально по остановке
def getSimilarStops(str):
    conn = config.conDB()
    cur = conn.cursor(cursor_factory=DictCursor)

    cur.execute("""
        SELECT stopname FROM stops WHERE lower(stopname) LIKE lower(%s)
    """,('%'+str+'%',))
    similarStops = cur.fetchall()
    similarStopslist = []
    for stop in similarStops:
        similarStopslist.append(stop[0])

    cur.close()
    conn.close()
    return similarStopslist

def getRouteNumbers(stop):
    conn = config.conDB()
    cur = conn.cursor(cursor_factory=DictCursor)

    cur.execute("""
            SELECT DISTINCT ON (routes.routename) routes.routename FROM tt
            INNER JOIN routes
            ON routes.routeid = tt.routeid
            INNER JOIN stops
            ON stops.stopid=tt.stopid
            INNER JOIN directions
            ON directions.dirid = tt.direction
            WHERE stopname = %s
            ORDER BY routes.routename
    """,(stop,))

    routeNumbersLL = cur.fetchall()

    routeNumbers = []
    for rn in routeNumbersLL:
        routeNumbers.append(rn[0])
    cur.close()
    conn.close()
    return routeNumbers

def getS2Directions(routenumber, stop):
    conn = config.conDB()
    cur = conn.cursor(cursor_factory=DictCursor)

    cur.execute("""
            SELECT DISTINCT ON (directions.dir)directions.dir FROM tt
            INNER JOIN routes
            ON routes.routeid = tt.routeid
            INNER JOIN stops
            ON stops.stopid=tt.stopid
            INNER JOIN directions
            ON directions.dirid = tt.direction
            WHERE stopname = %s and routename=%s
    """,(stop, routenumber,))

    dirsList = cur.fetchall()
    dirs = []
    for d in dirsList:
        dirs.append(d[0])

    cur.close()
    conn.close()
    return dirs