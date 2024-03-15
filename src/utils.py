import telebot

keyboard_buttons = {
  'add': '➕ Add',
  'list_uncompleted': '📄 List reminders',
  'list_completed': '✔️ List completed reminders',
  'cancel': '✖️ Cancel',
}

def get_main_keyboard():
  reply_markup = telebot.types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True,
  )
  reply_markup.row(
    telebot.types.KeyboardButton(keyboard_buttons['add']),
  )
  reply_markup.row(
    telebot.types.KeyboardButton(keyboard_buttons['list_uncompleted']),
    telebot.types.KeyboardButton(keyboard_buttons['list_completed']),
  )
  return reply_markup
