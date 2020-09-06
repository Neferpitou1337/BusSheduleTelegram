import pymysql

con = pymysql.connect(
    host = 'localhost',
    user = 'root',
    password ='1L0v3t0L3@rnSQL',
    port=3306
)


cursor = con.cursor()

cursor.execute("""CREATE DATABASE IF NOT EXISTS BOT""")
cursor.execute("SHOW DATABASES")
print(cursor.fetchall())

cursor.execute("USE BOT")
cursor.execute("SHOW tables")
print(cursor.fetchall())

cursor.execute("Desc employee")
print(cursor.fetchall())


cursor.execute("DROP table IF EXISTS employee")
cursor.execute("""CREATE TABLE employee(
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNIQUE NOT NULL,
    number VARCHAR(5) NOT NULL,
    first VARCHAR(30) NOT NULL,
    first_link VARCHAR(30) NOT NULL,
    last VARCHAR(30) NOT NULL,
    last_link VARCHAR(30) NOT NULL,
    state VARCHAR(5) NOT NULL
    
    )""")



con.close()
