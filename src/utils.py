import telebot

keyboard_buttons = {
  'add': '➕ Add',
  'list_uncompleted': '📄 List reminders',
  'list_completed': '✔️ List completed reminders',
  'cancel': '✖️ Cancel',
}

def format_reminder_date(date):
  return date.strftime('%A, %B %d at %I:%M %p')

def get_main_keyboard():
  reply_markup = telebot.types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=False,
  )
  reply_markup.row(
    telebot.types.KeyboardButton(keyboard_buttons['add']),
  )
  reply_markup.row(
    telebot.types.KeyboardButton(keyboard_buttons['list_uncompleted']),
    telebot.types.KeyboardButton(keyboard_buttons['list_completed']),
  )
  return reply_markup

def reminders_to_message(reminders):
  message = ''
  for index, reminder in enumerate(reminders):
    formatted_date = format_reminder_date(reminder.date)
    message += f'{index + 1}. {reminder.name} ({formatted_date})\n'

  message += '\nChoose reminder to edit:'

  return message

def reminder_to_message(reminder):
  formatted_date = format_reminder_date(reminder.date)
  return f'{reminder.name}\n\n<b>Next sending time:</b>\n{formatted_date}'
