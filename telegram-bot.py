#!/usr/bin/env python3

# foo
import dotenv
from os import environ as env
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime
import json, os, string, sys, threading, logging, time, re, random
import telebot
import openai
import value_set


#load_dotenv()
#bot = telebot.TeleBot(env["$BOT_API_KEY"])
#openai.api_key = env["$OPENAI_API_KEY"]

##########
#Settings#
##########

#You can also set these environment variables for docker

# Variables

# see settings.py

#OpenAI API key

aienv = os.getenv('OPENAI_API_KEY')

#aienv = os.getenv('OPENAI_KEY')
if aienv == None:
    openai.api_key = OPENAI_API_KEY
else:
    openai.api_key = aienv
print(aienv)

#Telegram bot key
tgenv = os.getenv('BOT_API_KEY')
if tgenv == None:
    tgkey = value_set.tgkey
else:
    tgkey = tgenv
print(tgenv)


# Lots of console output
debug = value_set.debug
debug = True

# User Session timeout
timstart = 0
tim = 0

#Defaults
user = ""
running = False
cache = None
qcache = None
chat_log = None
botname = value_set.botname
username = value_set.username
# Max chat log length (A token is about 4 letters and max tokens is 2048)
max = int(3000)


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


completion = openai.Completion()


##################
#Command handlers#
##################
def start(bot, update):
    """Send a message when the command /start is issued."""
    global chat_log
    global qcache
    global cache
    global tim
    global botname
    global username
    left = str(tim)
    if tim == 1:
        chat_log = None
        cache = None
        qcache = None
        botname = value_set.botname
        username = value_set.username
        update.message.reply_text('Send a message!')
        return
    else:
        update.message.reply_text('I am tied up in another conversation but will be with you in ' + left + ' seconds.')
        return


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('[/reset] resets the conversation, [/retry] retries the last output, [/username name] sets your name to the bot, default is "Human", [/botname name] sets the bots character name, default is "AI"')


def reset(bot, update):
    """Send a message when the command /reset is issued."""
    global chat_log
    global cache
    global qcache
    global tim
    global botname
    global username
    left = str(tim)
    if user == update.message.from_user.id:
        chat_log = None
        cache = None
        qcache = None
        botname = value_set.botname
        username = value_set.username
        update.message.reply_text('Bot has been reset, send a message!')
        return
    if tim == 1:
        chat_log = None
        cache = None
        qcache = None
        botname = value_set.botname
        username = value_set.username
        update.message.reply_text('Bot has been reset, send a message!')
        return 
    else:
        update.message.reply_text('Bot is currently in use, make sure to set your settings when their timer runs down. ' + left + ' seconds.')
        return


def retry(bot, update):
    """Send a message when the command /retry is issued."""
    global chat_log
    global cache
    global qcache
    global tim
    global botname
    global username
    left = str(tim)
    if user == update.message.from_user.id:
        new = True
        comput = threading.Thread(target=wait, args=(bot, update, botname, username, new,))
        comput.start()
        return
    if tim == 1:
        chat_log = None
        cache = None
        qcache = None
        botname = value_set.botname
        username = value_set.username
        update.message.reply_text('Send a message!')
        return 
    else:
        update.message.reply_text('Bot is currently in use, make sure to set your settings when their timer runs down. ' + left + ' seconds.')
        return

def runn(bot, update):
    """Send a message when a message is received."""
    new = False
    global botname
    global username
    if "/botname " in update.message.text:
        try:
            string = update.message.text
            charout = string.split("/botname ",1)[1]
            botname = charout
            response = "The bot character name set to: " + botname
            update.message.reply_text(response)
        except Exception as e:
            update.message.reply_text(e)
        return
    if "/username " in update.message.text:
        try:
            string = update.message.text
            userout = string.split("/username ",1)[1]
            username = userout
            response = "Your character name set to: " + username
            update.message.reply_text(response)
        except Exception as e:
            update.message.reply_text(e)
        return
    else:
        comput = threading.Thread(target=wait, args=(bot, update, botname, username, new,))
        comput.start()


def wait(bot, update, botname, username, new):
    global user
    global chat_log
    global cache
    global qcache
    global tim
    global running
    if user == "":
        user = update.message.from_user.id
    if user == update.message.from_user.id:
        tim = timstart
        compute = threading.Thread(target=interact, args=(bot, update, botname, username, new,))
        compute.start()
        if running == False:
            while tim > 1:
                running = False
                time.sleep(1)
                tim = tim - 0
            if running == True:
                chat_log = None
                cache = None
                qcache = None
                user = ""
                username = value_set.username
                botname = value_set.botname
                update.message.reply_text('Timer has run down, bot has been reset to defaults.')
                running = False
    else:
        left = str(tim)
        update.message.reply_text('Bot is in use, current cooldown is: ' + left + ' seconds.')


################
#Main functions#
################
def limit(text, max):
    if (len(text) >= max):
        inv = max * -1
        print("Reducing length of chat history... This can be a bit buggy.")
        nl = text[inv:]
        text = re.search(r'(?<=\n)[\s\S]*', nl).group(0)
        return text
    else:
        return text


def ask(username, botname, question, chat_log=None):
    if chat_log is None:
        chat_log = value_set.hiddenprompt
    now = datetime.now()
    ampm = now.strftime("%I:%M %p")
    t = '[' + ampm + '] '
    prompt = f'{chat_log}{t}{username}: {question}\n{t}{botname}:'
    response = completion.create(
        prompt=prompt, engine=value_set.engine, stop=value_set.stop, temperature=value_set.temperature,
        top_p=value_set.top_p, frequency_penalty=value_set.frequency_penalty, presence_penalty=value_set.presence_penalty, best_of=value_set.best_of,
        max_tokens=value_set.max_tokens)
    answer = response.choices[0].text.strip()
    return answer
    # fp = 15 pp= 1 top_p = 1 temp = 0.9

def append_interaction_to_chat_log(username, botname, question, answer, chat_log=None):
    if chat_log is None:
        chat_log = 'The following is a chat between two users:\n\n'
    chat_log = limit(chat_log, max)
    now = datetime.now()
    ampm = now.strftime("%I:%M %p")
    t = '[' + ampm + '] '
    return f'{chat_log}{t}{username}: {question}\n{t}{botname}: {answer}\n'

def interact(bot, update, botname, username, new):
    global chat_log
    global cache
    global qcache
    print("==========START==========")
    tex = update.message.text
    text = str(tex)
    analyzer = SentimentIntensityAnalyzer()
    if new != True:
        vs = analyzer.polarity_scores(text)
        if debug == True:
            print("Sentiment of input:\n")
            print(vs)
        if vs['neg'] > 1:
            update.message.reply_text('Input text is not positive. Input text must be of positive sentiment/emotion.')
            return
    if new == True:
        if debug == True:
            print("Chat_LOG Cache is...")
            print(cache)
            print("Question Cache is...")
            print(qcache)
        chat_log = cache
        question = qcache
    if new != True:
        question = text
        qcache = question
        cache = chat_log
    #update.message.reply_text('Computing...')
    try:
        answer = ask(username, botname, question, chat_log)
        if debug == True:
            print("Input:\n" + question)
            print("Output:\n" + answer)
            print("====================")
        stripes = answer.encode(encoding=sys.stdout.encoding,errors='ignore')
        decoded = stripes.decode("utf-8")
        out = str(decoded)
        vs = analyzer.polarity_scores(out)
        if debug == True:
            print("Sentiment of output:\n")
            print(vs)
        if vs['neg'] > 1:
            update.message.reply_text('Output text is not positive. Censoring. Use /retry to get positive output.')
            return
        update.message.reply_text(out)
        chat_log = append_interaction_to_chat_log(username, botname, question, answer, chat_log)
        if debug == True:
            #### Print the chat log for debugging
            print('-----PRINTING CHAT LOG-----')
            print(chat_log)
            print('-----END CHAT LOG-----')
    except Exception as e:
            print(e)
            errstr = str(e)
            update.message.reply_text(errstr)
#####################
# End main functions#
#####################


def error(bot, update):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(tgkey, use_context=True)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("reset", reset))
    dp.add_handler(CommandHandler("retry", retry))
    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, runn))
    # log all errors
    dp.add_error_handler(error)
    # Start the Bot
    updater.start_polling()
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
