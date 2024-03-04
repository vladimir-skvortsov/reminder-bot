import os
from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser
from langchain.prompts import ChatPromptTemplate
import datetime
from dotenv import load_dotenv

load_dotenv()

gigachat_auth_data = os.getenv('GIGACHAT_AUTH_DATA')
chat = GigaChat(credentials=gigachat_auth_data, verify_ssl_certs=False, temperature=0)

def parse_date(user_input):
  now = datetime.datetime.now()
  formatted_now = now.strftime('%Y-%m-%d')
  weekday = print(now.strftime("%A"))
  date = ResponseSchema(
    name='date',
    description=f'Now is {formatted_now}, {weekday}. Does the provided text refers to some sort if date? If yes, calculate the date in format "YYYY-mm-dd", None if no or unknown',
  )
  response_schemas = [date]
  output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
  format_instructions = output_parser.get_format_instructions()
  template = '''
    For the following text, extract the following information:

    date: Does the provided text refers to some sort if date? \
    If yes, calculate the date in format "YYYY-mm-dd", None if no or unknown.

    text: {user_input}

    {format_instructions}
  '''
  prompt = ChatPromptTemplate.from_template(template=template)
  messages = prompt.format_messages(
    user_input=user_input,
    format_instructions=format_instructions,
  )
  response = chat(messages)
  output_dict = output_parser.parse(response.content)
  date_string = output_dict.get('date')

  if date_string == 'None':
    return None

  return datetime.datetime.strptime(date_string, '%Y-%m-%d')
