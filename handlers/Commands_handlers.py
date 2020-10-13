import logging

import telebot


import etc
import userTableWorker
from handlers.All_relatedTo_Favorites import GetFavoritesMarkup

from etc import bot

# handler of /start and /reset commands
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # logging.info("%s is in start command",message.chat.id )
    # instead of gitub.com it should open my github with this project
    bot.reply_to(message, "Добро Пожаловать в Bus Schedule Bot\nКак пользоваться:\nhttps://clck.ru/RMJMW",
                 disable_web_page_preview=False,reply_markup=GetFavoritesMarkup(message))
    userTableWorker.setState(message.chat.id, etc.States.S_ENTER_NUMBER_OR_STOP.value)