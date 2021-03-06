from enum import Enum

import telebot

from config import TOKEN

URL = 'http://ap1.brest.by/shelude'
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
     '15В',
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

class States(Enum):
    S_START = "0"  # Начало нового диалога
    S_ENTER_NUMBER_OR_STOP = "1"
    S_CHOOSE_DIR = "2"
    S_CHOOSE_BUS_STOP = "3"
    S2_STOP_HANDLER = "4"
    S2_ROUTE_HANDLER = "5"
    S2_DIR_HANDLER = "6"
    ENTER_FAV = "F"


bot = telebot.TeleBot(TOKEN, parse_mode=None)