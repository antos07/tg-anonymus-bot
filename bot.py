from telegram import Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, BaseFilter, Filters
import _pickle

TOKEN = "749933056:AAFwRZFQqllbUyvprcNoYHn2dAvIpsKWSMY"

with open('dump.data', 'rb') as f:
	data = _pickle.load(f)

def sig_handler(signum, frame):
	Bot(TOKEN).send_message(-352068097, 'exit')
	with open('dump.data', 'wb') as f:
		_pickle.dump(data, f)

updater = Updater(TOKEN, user_sig_handler = sig_handler)
LAST = 'last'
USERS = 'users'
max_cnt = 20
dp = updater.dispatcher

def error(bot, update, e):
	print(e)

dp.add_error_handler(error)

def is_group(chat):
	if chat.type != 'group' and chat.type != 'supergroup':
		chat.send_message('Я работаю только в группах')
		return False
	return True

def is_admin(chat, user_id):
	chat_member = chat.get_member(user_id)
	return chat_member.status == chat_member.ADMINISTRATOR or chat_member.status == chat_member.CREATOR or chat_member.user.username == "antos07"

def start(bot, update):
	if not is_group(update.effective_chat):
		return
	if not is_admin(update.effective_chat, update.message.from_user.id):
		update.effective_chat.send_message('У вас нет прав для запуска бота')
		return
	if not update.effective_chat.id in data:
		data.update({update.effective_chat.id : {LAST : [], USERS : {}}})
		update.effective_chat.send_message('Я запустился')
	else:
		update.effective_chat.send_message('Я уже запущен')

	try:
		update.message.delete()
	except Exception:
		pass

 
dp.add_handler(CommandHandler(["start", "start@an_anonymous_bot"], start))


def recieved_msg(bot, update):
	if not is_group(update.effective_chat):
		return
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

dp.add_handler(MessageHandler(Filters.text, recieved_msg))

def get_my_last_msgs(bot, update, args):
	if not is_group(update.effective_chat):
		return
	if update.message.chat_id in data:
		chat_data = data[update.message.chat_id]
		if not update.message.from_user.id in chat_data[USERS]:
			update.effective_chat.send_message('Вы не написали еще ни одного сообщения')
			return
		msgs = chat_data[USERS][update.message.from_user.id]
		try:
			cnt = int(args[0])
		except Exception:
			cnt = 1
		msgs = msgs[-1 * min(cnt, len(msgs)):]
		for msg in msgs:
			text = msg.from_user.mention_markdown() + ":\n_" + msg.text + "_"
			try:
				update.effective_chat.send_message(text, parse_mode = 'Markdown', disable_web_page_preview = True,
			 		reply_to_message_id = msg.reply_to_message.message_id if msg.reply_to_message else None)
			except Exception:
				update.effective_chat.send_message(text, parse_mode = 'Markdown', disable_web_page_preview = True)
		try:
			update.message.delete()
		except Exception:
			pass
	else:
		update.effective_chat.send_message('Пропишите команду "/start"')

dp.add_handler(CommandHandler(['get_my_last_messages', 'get_my_last_messages@an_anonymous_bot'], get_my_last_msgs, pass_args = True))

def stop(bot, update):
	if not is_group(update.effective_chat):
		return
	if not is_admin(update.effective_chat, update.message.from_user.id):
		update.effective_chat.send_message('У вас нет прав для остановки бота')
		return
	if not update.message.chat_id in data:
		update.effective_chat.send_message('Я еще не запущен')
		return
	del data[update.effective_chat.id]
	update.effective_chat.send_message('Я отключен')
	try:
		update.message.delete()
	except Exception:
		pass

dp.add_handler(CommandHandler(['stop', 'stop@an_anonymous_bot'], stop))

updater.start_polling()
updater.idle()