import psycopg2
import config
from psycopg2.extras import DictCursor

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

#
# def getAll(user_id):
#     con = connec()
#     cursor = con.cursor()
#     cursor.execute("USE BOT")
#     cursor.execute("SELECT * FROM direction WHERE user_id=%s", user_id)
#     row = cursor.fetchone()
#     con.close()
#     print(cursor.fetchone() )
#     print("GET_all")
#     return row
#
#
# def setAll(user_id, number, first, first_link, last, last_link, state):
#     con = connec()
#     cursor = con.cursor()
#     cursor.execute("USE BOT")
#     cursor.execute("""REPLACE INTO direction (user_id, number, first, first_link, last, last_link, state) VALUES((%s), (%s), (%s), (%s), (%s), (%s),(%s))
#     """, (user_id, number, first, first_link, last, last_link, state,))
#     con.commit()
#     print("sET ALL")
#     con.close()
