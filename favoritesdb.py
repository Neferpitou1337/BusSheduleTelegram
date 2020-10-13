import config
import etc
from psycopg2.extras import DictCursor

def setFavorites(userid,*arg):
    conn = config.conDB()
    cur = conn.cursor(cursor_factory=DictCursor)

    routeids = []
    for a in arg:
        cur.execute("""
                SELECT routeid
                FROM routes
                WHERE routename=%s
        """,(a,))
        routeids.append(cur.fetchone()[0])

    cur.execute("""
                DELETE FROM favorites
                WHERE userid=%s
            """, (userid,))

    for id in routeids:
        cur.execute("""
                INSERT INTO
                favorites(userid,routeid)
                VALUES(%s,%s)
            """, (userid, id,))

    conn.commit()
    cur.close()
    conn.close()

def getFavorites(userid):
    conn = config.conDB()
    cur = conn.cursor(cursor_factory=DictCursor)

    cur.execute("""
            SELECT routes.routename
            FROM favorites
            INNER JOIN routes
            ON favorites.routeid = routes.routeid
            WHERE userid=%s
        """, (userid,))

    llrts = cur.fetchall()
    rts = []
    for r in llrts:
        rts.append(r[0])

    cur.close()
    conn.close()
    return rts