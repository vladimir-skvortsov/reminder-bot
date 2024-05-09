from fastapi import FastAPI
from db import Reminder
import utils
import datetime
from bot import bot

app = FastAPI()

@app.post('/notify')
async def notify():
  now = datetime.datetime.now()
  reminders = Reminder.get_all()
  reply_markup = utils.get_main_keyboard()

  for reminder in reminders:
    if reminder.date >= now or reminder.is_notified or reminder.is_done:
      continue

    bot.send_message(
        reminder.chat_id,
        reminder.name,
        reply_markup=reply_markup,
    )

    if reminder.is_periodic:
      reminder.date += datetime.timedelta(days=reminder.period_days)
    else:
      reminder.is_notified = True
    Reminder.update(reminder)

  return {}
