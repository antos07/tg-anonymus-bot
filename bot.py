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

dp.add_handler(MessageHandler(Filters.text, recieved_msg))

def get_my_last_msgs(bot, update, args):
	if update.message.chat_id in data:
		chat_data = data[update.message.chat_id]
		if not update.message.from_user.id in chat_data[USERS]:
			update.effective_chat.send_message('Вы не написали еще ни одного сообщения')
		msgs = chat_data[USERS][update.message.from_user.id]
		try:
			cnt = int(args[0])
		except Exception:
			cnt = 1
		msgs = msgs[-1 * min(cnt, len(msgs)):]
		for msg in msgs:
			text = msg.from_user.mention_markdown() + ":\n_" + msg.text + "_"
			update.effective_chat.send_message(text, parse_mode = 'Markdown', disable_web_page_preview = True,
			 reply_to_message_id = msg.reply_to_message.message_id if msg else None)
		try:
			update.message.delete()
		except Exception:
			pass
	else:
		update.effective_chat.send_message('Пропишите команду "/start"')

dp.add_handler(CommandHandler(['get_my_last_messages', 'get_my_last_messages@an_anonymous_bot'], get_my_last_msgs, pass_args = True))


updater.start_polling()
#sleep(60)
#updater.stop()