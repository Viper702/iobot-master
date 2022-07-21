import logging
from os import environ as env
from dotenv import load_dotenv # if you dont have dotenv yet: pip install python-dotenv

import telebot
import openai

import logger as telebot.logger
telebot.logger.setLevel(logging.DEBUG)

load_dotenv()
bot = telebot.TeleBot(env["BOT_API_KEY"])
openai.api_key = env["OPENAI_API_KEY"]


@bot.message_handler(func=lambda message: True)
def get_codex(message):
    response = openai.Completion.create(
        engine="code-davinci-001",
        prompt='"""\n{}\n"""'.format(message.text),
        temperature=0,
        max_tokens=800,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=['"""'])
    
    bot.send_message(message.chat.id,
    f'```python\n{response["choices"][0]["text"]}\n```',
    parse_mode="Markdown")
        
bot.infinity_polling()
