import telebot
bot = telebot.TeleBot("1267389438:AAHZH3YY33nveMK2VM8qsCMLYORYp6mqOXg", parse_mode=None)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(content_types=['text'])
def hui_sosi(message):
    bot.send_message(message.chat.id, message.text + " hui sosi, ya jivoy blya")

#RUN
bot.polling(none_stop=True)