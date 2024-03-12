import telebot

def get_main_keyboard():
  reply_markup = telebot.types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True,
  )
  reply_markup.row(
    telebot.types.KeyboardButton('➕ Add'),
  )
  reply_markup.row(
    telebot.types.KeyboardButton('📄 List reminders'),
    telebot.types.KeyboardButton('✔️ List completed reminders'),
  )
  return reply_markup
