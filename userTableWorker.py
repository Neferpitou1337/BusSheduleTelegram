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

def getStops():
    pass

def getTime():
    pass
