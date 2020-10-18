from telebot import types

import RefreshDB
import etc
import userTableWorker
from etc import bot
from handlers import Fork_of_Stops_or_Numbers, From_Stop_handlers
from handlers.All_relatedTo_Favorites import GetFavoritesMarkup




@bot.message_handler(commands=['back'])
def back_handler(message):
    mess_id = userTableWorker.getAll(message.chat.id)[-1]
    if userTableWorker.getState(message.chat.id) == etc.States.S_CHOOSE_BUS_STOP.value:
        if RefreshDB.isRefreshing():
            bot.send_message(message.chat.id, text="Подождите пару минут, идет обновление базы данных")
            return 0

        # delete previous message that relate to timetable and naxt after before with "Ответ сервера"
        try:
            bot.delete_message(message.chat.id,mess_id-1)
            bot.delete_message(message.chat.id,mess_id)
        except:
            pass
        finally:
            message.text = userTableWorker.getAll(message.chat.id)[1]
            Fork_of_Stops_or_Numbers.numberHandler(message)
        # [411279120, '10', 'Газоаппарат - БЭТЗ', None, '3']
    elif userTableWorker.getState(message.chat.id) == etc.States.S2_DIR_HANDLER.value:
        if RefreshDB.isRefreshing():
            bot.send_message(message.chat.id, text="Подождите пару минут, идет обновление базы данных")
            return 0

        # delete previous message that relate to timetable and naxt after before with "Ответ сервера"
        try:
            bot.delete_message(message.chat.id,mess_id-1)
            bot.delete_message(message.chat.id,mess_id)
        except:
            pass
        finally:
            message.text = userTableWorker.getAll(message.chat.id)[3]
            From_Stop_handlers.back_s2_Stop_Handler(message)
        # message.text = userTableWorker.getAll(message.chat.id)[3]
        # From_Stop_handlers.back_s2_Stop_Handler(message)
        # [411279120, '3', None, 'Мицкевича', '6']
    else:
        reset_handler(message)


@bot.message_handler(commands=['reset'])
def reset_handler(message):
    if userTableWorker.getState(message.chat.id) == etc.States.S_ENTER_NUMBER_OR_STOP.value:
        return 0
    else:
        mess_id = userTableWorker.getAll(message.chat.id)[-1]
        # delete previous message that relate to timetable and naxt after before with "Ответ сервера"
        try:
            bot.delete_message(message.chat.id,mess_id-1)
            bot.delete_message(message.chat.id,mess_id)
        except:
            pass
        finally:
            bot.send_message(message.chat.id,text="Введите номер автобуса или остановку",reply_markup=GetFavoritesMarkup(message))
            userTableWorker.setAll(message.chat.id, None, None, None, etc.States.S_ENTER_NUMBER_OR_STOP.value, None)