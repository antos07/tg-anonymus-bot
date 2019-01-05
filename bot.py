from telegram import Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, BaseFilter, Filters
import psycopg2 as ps2
from os import environ as ENVIRON

def init_db():
	db_url = ENVIRON['DATABASE_URL']
	con = ps2.connect(db_url, sslmode='require')
	return con, con.cursor()

TOKEN = "749933056:AAFwRZFQqllbUyvprcNoYHn2dAvIpsKWSMY"
max_cnt = 20
con, db = init_db()

def sig_handler(signum, frame):
	db.close()
	con.close()

updater = Updater(TOKEN)
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
	db.execute("""
		SELECT * FROM chats WHERE chat_id=%s
	""", (update.effective_chat.id,))
	if not db.fetchone():
		db.execute('''
			INSERT INTO chats(chat_id)
			VALUES
			(%s)
		''', (update.effective_chat.id,))
		con.commit()
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
	db.execute("SELECT * FROM chats WHERE chat_id=%s", (update.message.chat_id,))
	chat_data = db.fetchone() 
	if chat_data:
		text = update.message.from_user.mention_markdown() + ":\n_" + update.message.text + "_"
		last = chat_data[2]

		if last is None:
			last = []

		last.append(text)
		if len(last) > max_cnt:
			last.pop(0)

		if update.message.from_user:
			users_ids = chat_data[3]
			if users_ids is None:
				users_ids = []
			if not update.message.from_user.id in users_ids:
				users_ids.append(update.message.from_user.id)
				db.execute("""
					INSERT INTO users(user_id, chat_id)
					VALUES (%s, %s)
					""", (update.message.from_user.id, update.message.chat_id))

			db.execute("SELECT msgs FROM users WHERE user_id=%s AND chat_id=%s", (update.message.from_user.id, update.message.chat_id))
			msgs = db.fetchone()[0]

			if msgs is None:
				msgs = []

			msgs.append(text)

			if len(msgs) > max_cnt:
				msgs.pop(0)


			db.execute("UPDATE users SET msgs=%s", (msgs,))
			con.commit()

		db.execute("""
			UPDATE chats
			SET last_msgs=%s,
			users_ids=%s
		WHERE chat_id=%s
		""", (last, users_ids, update.message.chat_id))
		con.commit()

dp.add_handler(MessageHandler(Filters.text, recieved_msg))

def get_my_last_msgs(bot, update, args):
	if not is_group(update.effective_chat):
		return

	db.execute("SELECT chat_id, users_ids FROM chats WHERE chat_id=%s", (update.effective_chat.id,))
	data = db.fetchone()
	if not data:
		update.effective_chat.send_message('Пропишите команду "/start"')
		return
	if not data[1] or not update.message.from_user.id in data[1]:
		update.effective_chat.send_message('Вы не написали еще ни одного сообщения')
		return
	db.execute("SELECT msgs FROM users WHERE user_id=%s AND chat_id=%s", (update.message.from_user.id, update.effective_chat.id))
	msgs = db.fetchone()[0]
	try:
		cnt = int(args[0])
	except Exception:
		cnt = 1
	msgs = msgs[-1 * min(cnt, len(msgs)):]
	for msg in msgs:
		try:
			update.effective_chat.send_message(msg, parse_mode = 'Markdown', disable_web_page_preview = True,
		 		reply_to_message_id = msg.reply_to_message.message_id if msg.reply_to_message else None)
		except Exception:
			update.effective_chat.send_message(msg, parse_mode = 'Markdown', disable_web_page_preview = True)
	try:
		update.message.delete()
	except Exception:
		pass
		

dp.add_handler(CommandHandler(['get_my_last_messages', 'get_my_last_messages@an_anonymous_bot'], get_my_last_msgs, pass_args = True))

def stop(bot, update):
	if not is_group(update.effective_chat):
		return
	if not is_admin(update.effective_chat, update.message.from_user.id):
		update.effective_chat.send_message('У вас нет прав для остановки бота')
		return
	db.execute("SELECT chat_id, users_ids FROM chats WHERE chat_id=%s", (update.effective_chat.id,))
	data = db.fetchone()
	if not data:
		update.effective_chat.send_message('Я еще не запущен')
		return
	
	db.execute("""
		DELETE FROM users WHERE chat_id=%s;
		DELETE FROM chats WHERE chat_id=%s
		""", (update.effective_chat.id, update.effective_chat.id,))

	update.effective_chat.send_message('Я отключен')
	try:
		update.message.delete()
	except Exception:
		pass

dp.add_handler(CommandHandler(['stop', 'stop@an_anonymous_bot'], stop))

updater.start_polling()
updater.idle()