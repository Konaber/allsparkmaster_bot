from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import InlineQueryHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent
from wakeonlan import send_magic_packet
import logging
import paramiko

file = open(".secret.txt")
lines = file.readlines()

# Global constants
strBotToken = lines[0].strip('\n')
strIp = lines[1].strip('\n')
strMac = lines[2].strip('\n')
strCommodus = lines[3].strip('\n')
strCommodusPw = lines[4].strip('\n')
strArkserver = lines[5].strip('\n')
strArkserverPw = lines[6].strip('\n')
strHelp = "/rise - start the server\n/fall - shutdown the server\n/startArkserver - start the Arkserver instance\n/stopArkserver - stop the Arkserver instance"

updater = Updater(token=strBotToken)

dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

sshArkserverStart = paramiko.SSHClient()
sshArkserverStart.set_missing_host_key_policy(paramiko.AutoAddPolicy())
sshArkserverStop = paramiko.SSHClient()
sshArkserverStop.set_missing_host_key_policy(paramiko.AutoAddPolicy())

def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=strHelp)

def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=strHelp)

def wakeUpAllspark(update, context):
    send_magic_packet(strMac)
    context.bot.send_message(chat_id=update.effective_chat.id, text="The Allspark will rise!")

def slumberAllspark(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="The Allspark will fall!")
    sshArkserverStop.close()
    sshCommodus = paramiko.SSHClient()
    sshCommodus.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sshCommodus.connect(strIp, username=strCommodus, password=strCommodusPw)
    stdin, stdout, stderr = sshCommodus.exec_command('sudo shutdown -P now', get_pty=True)
    stdin.write(strCommodusPw)
    stdin.write("\n")
    stdin.flush()

def startArkserver(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Starting Arkserver!")
    sshArkserverStop.close()
    sshArkserverStart.connect(strIp, username=strArkserver, password=strArkserverPw)
    sshArkserverStart.exec_command('./arkserver start')

def stopArkserver(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Stopping Arkserver!")
    sshArkserverStart.close()
    sshArkserverStop.connect(strIp, username=strArkserver, password=strArkserverPw)
    sshArkserverStop.exec_command('./arkserver stop')

def inline(update, context):
    query = update.inline_query.query
    if not query:
        return
    results = list()
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='help',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    context.bot.answer_inline_query(update.inline_query.id, results)

help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)

wakeUpAllspark_handler = CommandHandler('rise', wakeUpAllspark)
dispatcher.add_handler(wakeUpAllspark_handler)

slumberAllspark_handler = CommandHandler('fall', slumberAllspark)
dispatcher.add_handler(slumberAllspark_handler)

startArkserver_handler = CommandHandler('startArkserver', startArkserver)
dispatcher.add_handler(startArkserver_handler)

stopArkserver_handler = CommandHandler('stopArkserver', stopArkserver)
dispatcher.add_handler(stopArkserver_handler)

inline_handler = InlineQueryHandler(inline)
dispatcher.add_handler(inline_handler)

echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)


updater.start_polling()
