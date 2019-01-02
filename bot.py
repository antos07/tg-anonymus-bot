from telegram import Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from time import sleep

TOKEN = "749933056:AAFwRZFQqllbUyvprcNoYHn2dAvIpsKWSMY"

updater = Updater(TOKEN)
data = {}
LAST = 'last'
USERS = 'users'
max_cnt = 20
dp = updater.dispatcher

def error(bot, update, e):
	print(e)

dp.add_error_handler(error)

def start(bot, update):
	if update.effective_chat.type != 'group' and update.effective_chat.type != 'supergroup':
		update.effective_chat.send_message('Я работаю только в группах')
	elif not update.effective_chat.id in data:
		data.update({update.effective_chat.id : {LAST : [], USERS : {}}})
		update.effective_chat.send_message('Я запустился')
	else:
		update.effective_chat.send_message('Я уже запущен')


dp.add_handler(CommandHandler(["start", "start@an_anonymous_bot"], start))


def recieved_msg(bot, update):
	if update.message.chat_id in data:
		chat_data = data[update.message.chat_id]

		chat_data[LAST].append(update.message)
		if len(chat_data[LAST]) > max_cnt:
			chat_data[LAST].pop(0)

		if update.message.from_user:
			if update.message.from_user.id in chat_data[USERS]:
				user_msgs = chat_data[USERS][update.message.from_user.id]
				user_msgs.append(update.message)
				if len(user_msgs) > max_cnt:
					user_msgs.pop(0)
			else:
				chat_data[USERS].update({update.message.from_user.id : [update.message]})
	else:
		update.effective_chat.send_message('Пропишите команду "/start"')

dp.add_handler(MessageHandler(Filters.all, recieved_msg))

updater.start_polling()
#sleep(60)
#updater.stop()