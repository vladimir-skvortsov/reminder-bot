import os
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import datetime

load_dotenv()

db_uri = os.getenv('DB_URI')
engine = create_engine(db_uri)
Session = sessionmaker(bind=engine)

Base = declarative_base()

class Reminder(Base):
  __tablename__ = 'reminders'

  id = Column(Integer, primary_key=True)
  name = Column(String)
  date = Column(DateTime)
  files = Column(ARRAY(String))

  def __repr__(self) -> str:
    return f'Reminder(id={self.id}, name={self.name}, date={self.date})'

  @classmethod
  def get_all_reminders(cls):
    session = Session()
    return session.query(cls).all()

  @classmethod
  def add_reminder(cls, reminder):
    session = Session()
    session.add(reminder)
    session.commit()

  @classmethod
  def update_reminder(cls, reminder):
    session = Session()
    session.merge(reminder)
    session.commit()

  @classmethod
  def delete_reminder(cls, id):
    session = Session()
    reminder = session.query(cls).get(id)
    if reminder is not None:
      session.delete(reminder)
      session.commit()

if __name__ == '__main__':
  reminders = Reminder.get_all_reminders()
  print(reminders)
