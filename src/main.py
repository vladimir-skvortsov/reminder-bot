import os
import utils
import datetime
import time
import threading
import uvicorn
import bot
import s3
from dotenv import load_dotenv
from db import Reminder

load_dotenv()

def check_media_groups():
  while True:
    now = datetime.datetime.now()

    for chat_id in list(bot.creation_media_groups):
      media_group = bot.creation_media_groups[chat_id]

      if media_group['last_check'] + datetime.timedelta(seconds=1) < now \
        and media_group['last_len'] == len(media_group['files']):
          objects = []

          for file in media_group['files']:
            file_id = file['file_id']
            file_name = file['file_name']
            file_info = bot.bot.get_file(file_id)
            downloaded_file = bot.bot.download_file(file_info.file_path)
            object_name = f'{file_id}_{file_name}'
            with open(file_name, 'wb') as file:
              file.write(downloaded_file)
            s3.client.upload_file(file_name, s3.aws_bucket, object_name)
            os.remove(file_name)
            objects.append(object_name)

          user_id = media_group['user_id']
          chat_id = media_group['chat_id']

          del bot.creation_media_groups[chat_id]

          with bot.bot.retrieve_data(user_id, chat_id) as data:
            reminder = Reminder(
              name=data['reminder_creation_name'],
              date=data['reminder_creation_date'],
              files=objects,
              is_periodic=data['reminder_creation_is_periodic'],
              period_days=data['reminder_creation_period_days'],
              chat_id=chat_id,
            )
            Reminder.add(reminder)

          bot.bot.delete_state(user_id, chat_id)

          reply_markup = utils.get_main_keyboard()
          bot.bot.send_message(
            chat_id,
            'Reminder is created',
            reply_markup=reply_markup,
          )
      else:
        media_group['last_check'] = now
        media_group['last_len'] = len(media_group['files'])

    for chat_id in list(bot.editing_media_groups):
      media_group = bot.editing_media_groups[chat_id]

      if media_group['last_check'] + datetime.timedelta(seconds=1) < now \
        and media_group['last_len'] == len(media_group['files']):
          objects = []

          for file in media_group['files']:
            file_id = file['file_id']
            file_name = file['file_name']
            file_info = bot.bot.get_file(file_id)
            downloaded_file = bot.bot.download_file(file_info.file_path)
            object_name = f'{file_id}_{file_name}'
            with open(file_name, 'wb') as file:
              file.write(downloaded_file)
            s3.client.upload_file(file_name, s3.aws_bucket, object_name)
            os.remove(file_name)
            objects.append(object_name)

          user_id = media_group['user_id']
          chat_id = media_group['chat_id']

          del bot.editing_media_groups[chat_id]

          with bot.bot.retrieve_data(user_id, chat_id) as data:
            reminder_id = data['reminder_editing_id']
            reminder = Reminder.get(reminder_id)
            reminder.name = data['reminder_editing_name']
            reminder.date = data['reminder_editing_date']
            reminder.date = [object_name]
            reminder.is_notified = False
            Reminder.update(reminder)

          bot.bot.delete_state(user_id, chat_id)

          reply_markup = utils.get_main_keyboard()
          bot.bot.send_message(
            chat_id,
            'Reminder is edited',
            reply_markup=reply_markup,
          )
      else:
        media_group['last_check'] = now
        media_group['last_len'] = len(media_group['files'])

    time.sleep(1)

if __name__ == '__main__':
  threading.Thread(
    target=bot.bot.infinity_polling,
    name='bot_infinity_polling',
    daemon=True,
  ).start()
  threading.Thread(
    target=check_media_groups,
    name='check_media_groups',
    daemon=True,
  ).start()

  uvicorn.run('server:app', host='0.0.0.0', port=3000, reload=True)
