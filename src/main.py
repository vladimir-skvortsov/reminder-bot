import os
import telebot
from dotenv import load_dotenv
import ai
from db import Reminder

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
  reply_markup = telebot.types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=False,
  )
  reply_markup.row(
    telebot.types.KeyboardButton('List reminders'),
    telebot.types.KeyboardButton('List completed reminders'),
  )

  bot.send_message(message.chat.id, 'Welcome! I\'m your reminder bot', reply_markup=reply_markup)

@bot.message_handler(commands=['list'])
def list_reminders(message):
  reminders = Reminder.get_all_reminders()
  text = '\n'.join(list(map(lambda reminder: f'- {reminder.name}', reminders)))

  bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['add'])
def list_reminders(message):
  bot.send_message(message.chat.id, 'Enter reminder name')
  bot.set_state(
    message.from_user.id,
    StatesGroup.reminder_creation_name,
    message.chat.id
  )

@bot.message_handler(state=StatesGroup.reminder_creation_name)
def reminder_name(message):
  bot.send_message(message.chat.id, 'Now the date')
  bot.set_state(
    message.from_user.id,
    StatesGroup.reminder_creation_date,
    message.chat.id
  )
  with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
    data['reminder_creation_name'] = message.text.strip()

@bot.message_handler(state=StatesGroup.reminder_creation_date)
def reminder_date(message):
  date = ai.parse_date(message)

  if date:
    bot.send_message(message.chat.id, 'Do you want to attach any files?')
    bot.set_state(
      message.from_user.id,
      StatesGroup.reminder_creation_date,
      message.chat.id
    )
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
      data['reminder_creation_date'] = date
  else:
    bot.send_message(message.chat.id, 'I don\'t understand')

@bot.message_handler(state=StatesGroup.reminder_creation_files_prompt)
def reminder_date(message):
  if message == 'Yes':
    bot.send_message(message.chat.id, 'Ok, attach the files')
    bot.set_state(
      message.from_user.id,
      StatesGroup.reminder_creation_files,
      message.chat.id
    )
  else:
    bot.send_message(message.chat.id, 'Reminder is created')

@bot.message_handler(state=StatesGroup.reminder_creation_files)
def reminder_date(message):
  bot.send_message(message.chat.id, 'Reminder is created')

@bot.message_handler()
def root(message):
  # TODO: parse command

  bot.send_message(message.chat.id, 'Enter reminder name')
  bot.set_state(
    message.from_user.id,
    StatesGroup.reminder_creation_name,
    message.chat.id
  )


bot.add_custom_filter(telebot.custom_filters.StateFilter(bot))
bot.add_custom_filter(telebot.custom_filters.IsDigitFilter())

bot.infinity_polling()
