from telegram import Bot
from telegram.ext import Updater, CommandHandler, MessageHandler

TOKEN = "749933056:AAG7N3k694uk1kbNe505VKuONIuBfR19wIQ"

updater = Updater(TOKEN)

def start(bot, update):
	if update.effective_chat.type != 'group' and update.effective_chat.type != 'supergroup':
		update.effective_chat.send_message('Я работаю только в группах')

updater.dispatcher.add_handler(CommandHandler("start", start))

updater.start_polling(timeout = 1)
updater.idle()