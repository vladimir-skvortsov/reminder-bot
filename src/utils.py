import telebot

keyboard_buttons = {
  'add': '➕ Add',
  'list_uncompleted': '📄 List reminders',
  'list_completed': '✔️ List completed reminders',
  'cancel': '✖️ Cancel',
  'mark_completed': '✔️ Mark completed',
  'mark_uncompleted': '✖️ Mark uncompleted',
  'edit': '✏️ Edit',
  'delete': '🗑️ Delete',
  'keep_the_same': '👍 Keep the same',
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

def reminders_to_message(reminders, start_index=0):
  message = ''
  for index, reminder in enumerate(reminders):
    formatted_date = format_reminder_date(reminder.date)
    message += f'{start_index + index + 1}. {reminder.name} ({formatted_date})\n'

  message += '\nChoose reminder to edit:'

  return message

def reminder_to_message(reminder):
  formatted_date = format_reminder_date(reminder.date)
  text = f'{reminder.name}\n\n'
  text += f'<b>Next sending time:</b>\n{formatted_date}\n\n'

  if reminder.is_periodic:
    text += f'<b>Period:</b>\n{reminder.period_days} day(s)\n\n'

  text += f'<b>{len(reminder.files) if len(reminder.files) else "No"} files attached</b>'

  return text
