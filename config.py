from enum import Enum

import psycopg2

URL = 'http://ap1.brest.by/shelude'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0','accept':'*/*'}
TOKEN = '1267389438:AAHZH3YY33nveMK2VM8qsCMLYORYp6mqOXg'
db_file = 'database.vdb'
NUMBERS_OF_BUSES = \
        ['1',
         '1А',
         '2',
         '2А',
         '3',
         '5',
         '6',
         '7',
         '8',
         '9',
         '10',
         '11',
         '11А',
         '12',
         '12А',
         '13',
         '13А',
         '14',
         '15А',
         '15Б',
         '15B',
         '16',
         '17',
         '18',
         '19',
         '20',
         '21',
         '21А',
         '21Б',
         '22',
         '23',
         '23А',
         '23Б',
         '24',
         '25',
         '26',
         '27',
         '27А',
         '29',
         '30',
         '30А',
         '31',
         '32',
         '33',
         '34',
         '35',
         '36',
         '37',
         '37А',
         '38',
         '39',
         '39А',
         '39Б',
         '40',
         '41',
         '42',
         '43',
         '44',
         '44А',
         '45',
         '46',
         '47']


def conDB():
 return psycopg2.connect(
  host="localhost",
  database="timetable",
  user="postgres",
  password="r10t1337")

class States(Enum):
  S_START = "0"  # Начало нового диалога
  S_ENTER_NUMBER = "1"
  S_CHOOSE_DIR = "2"
  S_CHOOSE_BUS_STOP = "3"