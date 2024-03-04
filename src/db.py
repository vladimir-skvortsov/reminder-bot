import os
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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

def add_reminder(reminder):
  session = Session()
  session.add(reminder)
  session.commit()

def update_reminder(reminder):
  session = Session()
  session.merge(reminder)
  session.commit()

def delete_reminder(id):
  session = Session()
  reminder = session.query(Reminder).get(id)
  if reminder is not None:
    session.delete(reminder)
    session.commit()
