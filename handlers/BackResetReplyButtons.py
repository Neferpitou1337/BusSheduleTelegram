from telebot import types

import etc
import userTableWorker
from etc import bot
from handlers.All_relatedTo_Favorites import GetFavoritesMarkup


def GetBackResetMarkup():
    markup = types.ReplyKeyboardMarkup(row_width=2,resize_keyboard=1,one_time_keyboard=1)
    markup.row(types.KeyboardButton("/back"), types.KeyboardButton("/reset"))
    return markup

@bot.message_handler(commands=['back'])
def back_handler(message):
    # bot.edit_message_text("лол",message.chat.id, message.message_id-1)
    pass


@bot.message_handler(commands=['reset'])
def reset_handler(message):
    print(userTableWorker.getState(message.chat.id))
    if userTableWorker.getState(message.chat.id) == etc.States.S_ENTER_NUMBER_OR_STOP.value:
        return 0
    else:
        bot.delete_message(message.chat.id,message.message_id-1)
        bot.send_message(message.chat.id,text="Введите номер автобуса или остановку",reply_markup=GetFavoritesMarkup(message))
        userTableWorker.setAll(message.chat.id, None, None, None, etc.States.S_ENTER_NUMBER_OR_STOP.value)