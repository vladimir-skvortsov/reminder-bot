import os
import telebot
import datetime
from dotenv import load_dotenv
import ai
import utils
import db

load_dotenv()

bot_token = os.getenv('BOT_TOKEN')
state_storage = telebot.storage.StateMemoryStorage()
bot = telebot.TeleBot(bot_token, state_storage=state_storage)

class StatesGroup(telebot.handler_backends.StatesGroup):
  reminder_creation_name = telebot.handler_backends.State()
  reminder_creation_date = telebot.handler_backends.State()
  reminder_creation_files_prompt = telebot.handler_backends.State()
  reminder_creation_files = telebot.handler_backends.State()

@bot.message_handler(commands=['start'])
def start(message):
  reply_markup = utils.get_main_keyboard()
  bot.send_message(
    message.chat.id,
    'Welcome! I\'m your personal reminder bot.\n\n'
    '<b>Here are some useful commands for you:</b>\n\n'
    '/start - start using bot / go to main menu\n'
    '/help - open help\n'
    '/add - add new reminder\n'
    '/list - get a list of your reminders\n'
    '/list_completed - get a list of completed reminders\n'
    '/cancel - cancel the current operation',
    parse_mode='HTML',
    reply_markup=reply_markup,
  )

@bot.message_handler(commands=['cancel'])
def list_reminders(message):
  bot.delete_state(message.from_user.id, message.chat.id)

@bot.message_handler(commands=['list'])
def list_reminders(message):
  reminders = db.Reminder.get_all()
  text = '\n'.join(list(map(lambda reminder: f'- {reminder.name}', reminders)))

  bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['add'])
def list_reminders(message):
  reply_markup = telebot.types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True,
  )
  reply_markup.row(telebot.types.KeyboardButton('✖️ Cancel'))
  bot.send_message(
    message.chat.id,
    'What should I remind you about?',
    reply_markup=reply_markup,
  )
  bot.set_state(
    message.from_user.id,
    StatesGroup.reminder_creation_name,
    message.chat.id
  )

@bot.message_handler(state=StatesGroup.reminder_creation_name)
def reminder_name(message):
  if (message.text == '✖️ Cancel'):
    bot.delete_state(message.from_user.id, message.chat.id)
    bot.send_message(message.chat.id, 'Cancelled')
    return

  reply_markup = telebot.types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True,
  )
  reply_markup.row(telebot.types.KeyboardButton('✖️ Cancel'))
  bot.send_message(
    message.chat.id,
    'Enter the date',
    reply_markup=reply_markup,
  )
  bot.set_state(
    message.from_user.id,
    StatesGroup.reminder_creation_date,
    message.chat.id
  )
  with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
    data['reminder_creation_name'] = message.text.strip()

@bot.message_handler(state=StatesGroup.reminder_creation_date)
def reminder_date(message):
  if (message.text == '✖️ Cancel'):
    bot.delete_state(message.from_user.id, message.chat.id)
    bot.send_message(message.chat.id, 'Cancelled')
    return

  date_string = message.text.strip().lower()

  try:
    date = datetime.datetime.strptime(date_string, '%d.%m.%Y')
  except:
    bot.send_message(message.chat.id, 'I don\'t understand')
    return

  reply_markup = telebot.types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True,
  )
  reply_markup.row(
    telebot.types.KeyboardButton('Yes'),
    telebot.types.KeyboardButton('No'),
  )
  reply_markup.row(telebot.types.KeyboardButton('✖️ Cancel'))
  bot.send_message(
    message.chat.id,
    'Do you want to attach any files?',
    reply_markup=reply_markup,
  )
  bot.set_state(
    message.from_user.id,
    StatesGroup.reminder_creation_files_prompt,
    message.chat.id
  )
  with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
    data['reminder_creation_date'] = date

@bot.message_handler(state=StatesGroup.reminder_creation_files_prompt)
def reminder_date(message):
  if message.text == 'Yes':
    bot.send_message(message.chat.id, 'Ok, attach the files')
    bot.set_state(
      message.from_user.id,
      StatesGroup.reminder_creation_files,
      message.chat.id
    )
  else:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
      reminder = db.Reminder(
        name=data['reminder_creation_name'],
        date=data['reminder_creation_date'],
      )
      db.Reminder.add(reminder)

    bot.delete_state(message.from_user.id, message.chat.id)

    reply_markup = utils.get_main_keyboard()
    bot.send_message(
      message.chat.id,
      'Reminder is created',
      reply_markup=reply_markup,
    )

@bot.message_handler(
  state=StatesGroup.reminder_creation_files,
  content_types=['document', 'photo', 'audio'],
)
def reminder_date(message):
  if message.document:
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with open(message.document.file_name, 'wb') as new_file:
      new_file.write(downloaded_file)
  elif message.photo:
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with open('photo.jpg', 'wb') as new_file:
      new_file.write(downloaded_file)
  elif message.audio:
    file_info = bot.get_file(message.audio.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with open(message.audio.title + '.mp3', 'wb') as new_file:
      new_file.write(downloaded_file)

  with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
    reminder = db.Reminder(
      name=data['reminder_creation_name'],
      date=data['reminder_creation_date'],
    )
    db.Reminder.add(reminder)

  bot.delete_state(message.from_user.id, message.chat.id)

  reply_markup = utils.get_main_keyboard()
  bot.send_message(
    message.chat.id,
    'Reminder is created',
    reply_markup=reply_markup,
  )

bot.add_custom_filter(telebot.custom_filters.StateFilter(bot))

bot.infinity_polling()
