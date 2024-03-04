import os
from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat
from dotenv import load_dotenv

load_dotenv()

gigachat_auth_data = os.getenv('GIGACHAT_AUTH_DATA')
chat = GigaChat(credentials=gigachat_auth_data, verify_ssl_certs=False, temperature=0)

messages = [
  SystemMessage(content='Выдавай максимально короткие и точные ответы'),
  HumanMessage(content='Сколько метров Эйфелева башня?'),
]
res = chat(messages)
print(res)
