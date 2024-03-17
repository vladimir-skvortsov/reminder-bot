import os
import telebot
import datetime
import boto3
import utils
import db
import re
from dotenv import load_dotenv
import dateparser

load_dotenv()

bot_token = os.getenv('BOT_TOKEN')
state_storage = telebot.storage.StateMemoryStorage()
bot = telebot.TeleBot(bot_token, state_storage=state_storage)

aws_access_key = os.getenv('AWS_ACCESS_KEY')
aws_secret_key = os.getenv('AWS_SECRET_KEY')
aws_bucket = os.getenv('AWS_BUCKET')
s3 = boto3.client(
  's3',
  aws_access_key_id=aws_access_key,
  aws_secret_access_key=aws_secret_key,
)

reminders_per_page = 7

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
    '/start — start using bot / go to main menu\n'
    '/help — open help\n'
    '/add — add new reminder\n'
    '/list — get a list of your reminders\n'
    '/list_completed — get a list of completed reminders\n'
    '/cancel — cancel the current operation',
    parse_mode='HTML',
    reply_markup=reply_markup,
  )

@bot.message_handler(commands=['cancel'])
def cancel(message):
  bot.delete_state(message.from_user.id, message.chat.id)

@bot.message_handler(commands=['list'])
def list_uncompleted_reminders(message):
  reminders = db.Reminder.get_all_uncompleted()
  page_reminders = reminders[:reminders_per_page]

  text = utils.reminders_to_message(page_reminders)

  inline_markup = telebot.types.InlineKeyboardMarkup()
  reminders_buttons = [
    telebot.types.InlineKeyboardButton(index + 1, callback_data=f'reminder_{reminder.id}')
    for index, reminder in enumerate(page_reminders)
  ]
  inline_markup.row(*reminders_buttons)
  if len(reminders) > reminders_per_page:
    inline_markup.row(
      telebot.types.InlineKeyboardButton('Page 2 >>', callback_data=f'page_uncompleted_1')
    )

  bot.send_message(message.chat.id, text, reply_markup=inline_markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
  data = call.data
  chat_id = call.json['message']['chat']['id']
  message_id = call.json['message']['message_id']

  if data.startswith('reminder_'):
    reminder_id = int(re.findall('\d+', data)[0])
    reminder = db.Reminder.get(reminder_id)
    text = utils.reminder_to_message(reminder)

    inline_markup = telebot.types.InlineKeyboardMarkup()
    inline_markup.row(
      telebot.types.InlineKeyboardButton('✔️ Mark completed', callback_data=f'mark_completed_{reminder_id}'),
      telebot.types.InlineKeyboardButton('🗑️ Delete', callback_data=f'delete_{reminder_id}'),
    )
    inline_markup.row(
      telebot.types.InlineKeyboardButton('Back to list', callback_data=f'back_to_list'),
    )

    bot.edit_message_text(
      text,
      chat_id,
      message_id,
      parse_mode='HTML',
      reply_markup=inline_markup,
    )
  elif data.startswith('mark_completed_'):
    reminder_id = int(re.findall('\d+', data)[0])
    reminder = db.Reminder.get(reminder_id)
    reminder.is_done = True
    db.Reminder.update(reminder)

    reminders = db.Reminder.get_all_uncompleted()
    page_reminders = reminders[:reminders_per_page]

    text = utils.reminders_to_message(page_reminders)

    inline_markup = telebot.types.InlineKeyboardMarkup()
    reminders_buttons = [
      telebot.types.InlineKeyboardButton(index + 1, callback_data=f'reminder_{reminder.id}')
      for index, reminder in enumerate(page_reminders)
    ]
    inline_markup.row(*reminders_buttons)
    if len(reminders) > len(page_reminders):
      inline_markup.row(
        telebot.types.InlineKeyboardButton('Page 2 >>', callback_data=f'page_uncompleted_1'),
      )

    bot.edit_message_text(text, chat_id, message_id, reply_markup=inline_markup)
  elif data.startswith('delete_'):
    reminder_id = int(re.findall('\d+', data)[0])
    db.Reminder.delete(reminder_id)

    reminders = db.Reminder.get_all_uncompleted()
    page_reminders = reminders[:reminders_per_page]

    text = utils.reminders_to_message(page_reminders)

    inline_markup = telebot.types.InlineKeyboardMarkup()
    reminders_buttons = [
      telebot.types.InlineKeyboardButton(index + 1, callback_data=f'reminder_{reminder.id}')
      for index, reminder in enumerate(page_reminders)
    ]
    inline_markup.row(*reminders_buttons)
    if len(reminders) > len(page_reminders):
      inline_markup.row(
        telebot.types.InlineKeyboardButton('Page 2 >>', callback_data=f'page_uncompleted_1'),
      )

    bot.edit_message_text(text, chat_id, message_id, reply_markup=inline_markup)
  elif data.startswith('back_to_list'):
    reminders = db.Reminder.get_all_uncompleted()
    page_reminders = reminders[:reminders_per_page]

    text = utils.reminders_to_message(page_reminders)

    inline_markup = telebot.types.InlineKeyboardMarkup()
    reminders_buttons = [
      telebot.types.InlineKeyboardButton(index + 1, callback_data=f'reminder_{reminder.id}')
      for index, reminder in enumerate(page_reminders)
    ]
    inline_markup.row(*reminders_buttons)
    if len(reminders) > len(page_reminders):
      inline_markup.row(
        telebot.types.InlineKeyboardButton('Page 2 >>', callback_data=f'page_uncompleted_1'),
      )

    bot.edit_message_text(text, chat_id, message_id, reply_markup=inline_markup)
  elif data.startswith('page_uncompleted_'):
    page_index = int(re.findall('\d+', data)[0])
    reminders = db.Reminder.get_all_uncompleted()
    start_index = page_index * reminders_per_page
    end_index = (page_index + 1) * reminders_per_page
    page_reminders = reminders[start_index:end_index]

    text = utils.reminders_to_message(page_reminders, start_index)

    inline_markup = telebot.types.InlineKeyboardMarkup()

    reminders_buttons = [
      telebot.types.InlineKeyboardButton(start_index + index + 1, callback_data=f'reminder_{reminder.id}')
      for index, reminder in enumerate(page_reminders)
    ]
    inline_markup.row(*reminders_buttons)

    pages_buttons = []
    if page_index != 0:
      pages_buttons.append(
        telebot.types.InlineKeyboardButton(f'<< Page {page_index}', callback_data=f'page_uncompleted_{page_index - 1}'),
      )
    if len(reminders) > (page_index + 1) * reminders_per_page:
      pages_buttons.append(
        telebot.types.InlineKeyboardButton(f'Page {page_index + 2} >>', callback_data=f'page_uncompleted_{page_index + 1}'),
      )
    if len(pages_buttons):
      inline_markup.row(*pages_buttons)

    bot.edit_message_text(text, chat_id, message_id, reply_markup=inline_markup)
  elif data.startswith('page_completed_'):
    page_index = int(re.findall('\d+', data)[0])
    reminders = db.Reminder.get_all_completed()
    start_index = page_index * reminders_per_page
    end_index = (page_index + 1) * reminders_per_page
    page_reminders = reminders[start_index:end_index]

    text = utils.reminders_to_message(page_reminders, start_index)

    inline_markup = telebot.types.InlineKeyboardMarkup()

    reminders_buttons = [
      telebot.types.InlineKeyboardButton(start_index + index + 1, callback_data=f'reminder_{reminder.id}')
      for index, reminder in enumerate(page_reminders)
    ]
    inline_markup.row(*reminders_buttons)

    pages_buttons = []
    if page_index != 0:
      pages_buttons.append(
        telebot.types.InlineKeyboardButton(f'<< Page {page_index}', callback_data=f'page_completed_{page_index - 1}'),
      )
    if len(reminders) > (page_index + 1) * reminders_per_page:
      pages_buttons.append(
        telebot.types.InlineKeyboardButton(f'Page {page_index + 2} >>', callback_data=f'page_completed_{page_index + 1}'),
      )
    if len(pages_buttons):
      inline_markup.row(*pages_buttons)

    bot.edit_message_text(text, chat_id, message_id, reply_markup=inline_markup)

@bot.message_handler(commands=['list_completed'])
def list_completed_reminders(message):
  reminders = db.Reminder.get_all_completed()
  page_reminders = reminders[:reminders_per_page]

  text = utils.reminders_to_message(page_reminders)

  inline_markup = telebot.types.InlineKeyboardMarkup()
  reminders_buttons = [
    telebot.types.InlineKeyboardButton(index + 1, callback_data=f'reminder_{reminder.id}')
    for index, reminder in enumerate(page_reminders)
  ]
  inline_markup.row(*reminders_buttons)
  if len(reminders) > reminders_per_page:
    inline_markup.row(
      telebot.types.InlineKeyboardButton('Page 2 >>', callback_data=f'page_completed_1')
    )

  bot.send_message(message.chat.id, text, reply_markup=inline_markup)

@bot.message_handler(commands=['add'])
def add_reminder(message):
  reply_markup = telebot.types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=False,
  )
  reply_markup.row(telebot.types.KeyboardButton(utils.keyboard_buttons['cancel']))
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
  if (message.text == utils.keyboard_buttons['cancel']):
    bot.delete_state(message.from_user.id, message.chat.id)
    reply_markup = utils.get_main_keyboard()
    bot.send_message(message.chat.id, 'Cancelled', reply_markup=reply_markup)
    return

  reply_markup = telebot.types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=False,
  )
  reply_markup.row(telebot.types.KeyboardButton(utils.keyboard_buttons['cancel']))
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
  if (message.text == utils.keyboard_buttons['cancel']):
    bot.delete_state(message.from_user.id, message.chat.id)
    reply_markup = utils.get_main_keyboard()
    bot.send_message(message.chat.id, 'Cancelled', reply_markup=reply_markup)
    return

  date_string = message.text.strip().lower()

  try:
    date = dateparser.parse(date_string)
  except Exception as e:
    bot.send_message(message.chat.id, 'I don\'t understand')
    return

  reply_markup = telebot.types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=False,
  )
  reply_markup.row(
    telebot.types.KeyboardButton('Yes'),
    telebot.types.KeyboardButton('No'),
  )
  reply_markup.row(telebot.types.KeyboardButton(utils.keyboard_buttons['cancel']))
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
  if (message.text == utils.keyboard_buttons['cancel']):
    bot.delete_state(message.from_user.id, message.chat.id)
    reply_markup = utils.get_main_keyboard()
    bot.send_message(message.chat.id, 'Cancelled', reply_markup=reply_markup)
    return

  if message.text == 'Yes':
    bot.send_message(message.chat.id, 'Ok, attach the files')
    bot.set_state(
      message.from_user.id,
      StatesGroup.reminder_creation_files,
      message.chat.id,
    )
    return

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
  file_id = None
  file_name = None

  if message.document:
    file_id = message.document.file_id
    file_name = message.document.file_name
  elif message.photo:
    file_id = message.photo[-1].file_id
    file_name = message.photo[-1].file_name
  elif message.audio:
    file_id = message.audio.file_id
    file_name = message.audio.file_name

  file_info = bot.get_file(file_id)
  downloaded_file = bot.download_file(file_info.file_path)
  object_name = f'{file_id}_{file_name}'
  with open(file_name, 'wb') as file:
    file.write(downloaded_file)
  s3.upload_file(file_name, aws_bucket, object_name)
  os.remove(file_name)

  with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
    reminder = db.Reminder(
      name=data['reminder_creation_name'],
      date=data['reminder_creation_date'],
      files=[object_name],
    )
    db.Reminder.add(reminder)

  bot.delete_state(message.from_user.id, message.chat.id)

  reply_markup = utils.get_main_keyboard()
  bot.send_message(
    message.chat.id,
    'Reminder is created',
    reply_markup=reply_markup,
  )

@bot.message_handler()
def reminder_date(message):
  if message.text == utils.keyboard_buttons['add']:
    return add_reminder(message)
  if message.text == utils.keyboard_buttons['list_uncompleted']:
    return list_uncompleted_reminders(message)
  if message.text == utils.keyboard_buttons['list_completed']:
    return list_completed_reminders(message)

  reply_markup = utils.get_main_keyboard()
  bot.send_message(
    message.chat.id,
    'Sorry, I don\'t understand',
    reply_markup=reply_markup,
  )

bot.add_custom_filter(telebot.custom_filters.StateFilter(bot))

bot.infinity_polling()
