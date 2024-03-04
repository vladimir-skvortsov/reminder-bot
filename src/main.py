import os
import telebot
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv('BOT_TOKEN')
state_storage = telebot.storage.StateMemoryStorage()
bot = telebot.TeleBot(bot_token, state_storage=state_storage)

@bot.message_handler(commands=['start'])
def send_welcome(message):
  bot.reply_to(message, "Welcome! I'm your reminder bot.")

bot.add_custom_filter(telebot.custom_filters.StateFilter(bot))
bot.add_custom_filter(telebot.custom_filters.IsDigitFilter())

bot.infinity_polling()
