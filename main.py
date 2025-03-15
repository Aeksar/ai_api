from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from asyncio import sleep
from mistralai import Mistral
from dotenv import load_dotenv
import os
from pprint import pprint

from set_db import Mongo
from logger import logger

load_dotenv()

TOKEN = os.environ.get('BOT_TOKEN')
API_KEY = os.environ.get('MISTRAL_TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher()

model = "mistral-small-latest"
client = Mistral(api_key=API_KEY)
mongo = Mongo()


@dp.message(CommandStart())
async def start(msg: Message):
    response = await client.chat.complete_async(
        model=model,
        messages=[{
            "role": "user",
            "content": "Привет"
        }]
    )
    
    await msg.answer(response.choices[0].message.content)


@dp.message()
async def pupupu(msg: Message):

    chat_id = msg.from_user.id
    
    await mongo.insert_prompt(
        chat_id=chat_id, 
        role='user', 
        message=msg.text
    )

    prompt = await mongo.get_prompt(chat_id)
    pprint(prompt)
    response = client.chat.complete(
    model=model,
    messages= prompt
    )
    
    answer = response.choices[0].message.content
    
    await mongo.insert_prompt(
        chat_id=chat_id, 
        role='assistant', 
        message=answer
    )
    
    await msg.answer(answer, parse_mode='Markdown')
    

dp.run_polling(bot)