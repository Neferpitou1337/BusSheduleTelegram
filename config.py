import psycopg2

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0',
           'accept': '*/*'}
TOKEN = '1267389438:AAHZH3YY33nveMK2VM8qsCMLYORYp6mqOXg'
NGROK = 'https://5de5ba403a5f.ngrok.io'

def conDB():
    return psycopg2.connect(
        host="localhost",
        database="timetable",
        user="postgres",
        password="r10t1337")

