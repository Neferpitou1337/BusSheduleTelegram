import pymysql


# con = pymysql.connect(
#         host='localhost',
#         user='root',
#         password='1L0v3t0L3@rnSQL',
#         port=3306,
#         cursorclass=pymysql.cursors.DictCursor
#     )
# cursor = con.cursor()
#
# # 1 use creation of bot program
# cursor.execute("""CREATE DATABASE IF NOT EXISTS BOT""")
# cursor.execute("SHOW DATABASES")
# print(cursor.fetchall())
#
# cursor.execute("USE BOT")
# cursor.execute("SHOW tables")
# print(cursor.fetchall())
#
# cursor.execute("Desc direction")
# print(cursor.fetchall())
#
#
# cursor.execute("DROP table IF EXISTS employee")
# cursor.execute("""CREATE TABLE IF NOT EXISTS direction(
#     id INT PRIMARY KEY AUTO_INCREMENT,
#     user_id INT UNIQUE NOT NULL,
#     number VARCHAR(5) NOT NULL,
#     first VARCHAR(30) NOT NULL,
#     first_link VARCHAR(100) NOT NULL,
#     last VARCHAR(30) NOT NULL,
#     last_link VARCHAR(100) NOT NULL,
#     state VARCHAR(5) NOT NULL
#
#     )""")
# con.close()

def connec():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='1L0v3t0L3@rnSQL',
        port=3306,
        cursorclass=pymysql.cursors.DictCursor
    )

def getState(user_id):
    con = connec()
    cursor = con.cursor()
    cursor.execute("USE BOT")
    cursor.execute("SELECT state FROM direction WHERE user_id=%s", user_id)
    print(cursor.fetchone())
    con.close()

def setState(user_id, state):
    con = connec()
    cursor = con.cursor()
    cursor.execute("USE BOT")
    cursor.execute("""UPDATE direction SET state=%s where user_id=%s
        """, (state,user_id,))
    con.commit()
    con.close()


def getAll(user_id):
    con = connec()
    cursor = con.cursor()
    cursor.execute("USE BOT")
    cursor.execute("SELECT * FROM direction WHERE user_id=%s", user_id)
    row = cursor.fetchone()
    con.close()
    return row


def setAll(user_id, number, first, first_link, last, last_link, state):
    con = connec()
    cursor = con.cursor()
    cursor.execute("USE BOT")
    cursor.execute("""REPLACE INTO direction (user_id, number, first, first_link, last, last_link, state) VALUES((%s), (%s), (%s), (%s), (%s), (%s),(%s))
    """, (user_id, number, first, first_link, last, last_link, state,))
    con.commit()
    con.close()


setAll(122,"12","pee-shit","url1","shit-pee","url2","2")
setAll(133,"13","peasdae-shit","uddsrl1","shissdt-pee","url3","3")
setAll(122,"12","pee-131t","url3","s3131ee","url3","3")
setAll(133,"12","pee-131t","url3","s3131ee","url3","3")
getState(122)
setState(122,"4")
getState(122)
getAll(122)
con = pymysql.connect(
        host='localhost',
        user='root',
        password='1L0v3t0L3@rnSQL',
        port=3306,
        cursorclass=pymysql.cursors.DictCursor
    )
cursor = con.cursor()
cursor.execute("USE bot")
cursor.execute("SELECT * FROM direction")
print(cursor.fetchall())

cursor.execute("Desc direction")
print(cursor.fetchall())