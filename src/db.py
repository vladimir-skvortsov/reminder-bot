import os
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc
from dotenv import load_dotenv

load_dotenv()

db_uri = os.getenv('DB_URI')
engine = create_engine(db_uri)
Session = sessionmaker(bind=engine)

Base = declarative_base()

class Reminder(Base):
  __tablename__ = 'reminders'

  id = Column(Integer, primary_key=True)
  name = Column(String)
  is_done = Column(Boolean, default=False)
  date = Column(DateTime)
  date_completed = Column(DateTime)
  files = Column(ARRAY(String), default=[])
  is_periodic = Column(Boolean, default=False)
  period_days = Column(Integer)
  is_notified = Column(Boolean, default=False)
  chat_id = Column(Integer)

  def __repr__(self) -> str:
    return f'Reminder(id={self.id}, name={self.name}, is_done={self.is_done}, date={self.date}, files={self.files})'

  @classmethod
  def get(cls, id):
    session = Session()
    return session.query(cls).get(id)

  @classmethod
  def get_all(cls):
    session = Session()
    return session.query(cls).all()

  @classmethod
  def get_all_completed(cls):
    session = Session()
    return session.query(cls).filter_by(is_done=True).order_by(desc(Reminder.date)).all()

  @classmethod
  def get_all_uncompleted(cls):
    session = Session()
    return session.query(cls).filter_by(is_done=False).all()

  @classmethod
  def add(cls, reminder):
    session = Session()
    session.add(reminder)
    session.commit()

  @classmethod
  def update(cls, reminder):
    session = Session()
    session.merge(reminder)
    session.commit()

  @classmethod
  def delete(cls, id):
    session = Session()
    reminder = session.query(cls).get(id)
    if reminder is not None:
      session.delete(reminder)
      session.commit()

if __name__ == '__main__':
  from sqlalchemy import create_engine

  engine = create_engine('postgresql://postgres:postgres@localhost/postgres')
  Base.metadata.create_all(engine)

  # reminders = Reminder.get_all()
  # for reminder in reminders:
  #   Reminder.delete(reminder.id)
  # print(reminders)
