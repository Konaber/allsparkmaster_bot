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
strBotToken    = lines[ 0].strip('\n')
strIp          = lines[ 1].strip('\n')
strMac         = lines[ 2].strip('\n')
strCommodus    = lines[ 3].strip('\n')
strCommodusPw  = lines[ 4].strip('\n')
strArkserver   = lines[ 5].strip('\n')
strArkserverPw = lines[ 6].strip('\n')
strCssserver   = lines[ 7].strip('\n')
strCssserverPw = lines[ 8].strip('\n')
strMcserver    = lines[ 9].strip('\n')
strMcserverPw  = lines[10].strip('\n')

strHelp = ""
strHelp += "/wakeup - start the server\n"
strHelp += "/sleep - shutdown the server\n"
strHelp += "/startArkserver - start the Arkserver server\n"
strHelp += "/stopArkserver - stop the Arkserver server\n"
strHelp += "/startCssserver - start the CounterStrike-Source server\n"
strHelp += "/stopCssserver - stop the CounterStrike-Source server\n" 
strHelp += "/startMcserver - start the Minecraft server\n"
strHelp += "/stopMcserver - stop the Minecraft server\n" 

updater = Updater(token=strBotToken)

dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())


# Functions for handlers
def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=strHelp)

def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=strHelp)

def wakeUpAllspark(update, context):
    send_magic_packet(strMac)
    context.bot.send_message(chat_id=update.effective_chat.id, text="The Allspark will wake up!")

def sleepAllspark(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="The Allspark will sleep!")
    ssh.connect(strIp, username=strCommodus, password=strCommodusPw)
    stdin, stdout, stderr = sshCommodus.exec_command('sudo shutdown -P now', get_pty=True)
    stdin.write(strCommodusPw)
    stdin.write("\n")
    stdin.flush()

def startArkserver(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Starting Arkserver")
    ssh.connect(strIp, username=strArkserver, password=strArkserverPw)
    sendCommand('./arkserver start', update, context)
    ssh.close()

def stopArkserver(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Stopping Arkserver")
    ssh.connect(strIp, username=strArkserver, password=strArkserverPw)
    sendCommand('./arkserver stop', update, context)
    ssh.close()

def startCssserver(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Starting Cssserver!")
    ssh.connect(strIp, username=strCssserver, password=strCssserverPw)
    sendCommand('./cssserver start', update, context)
    ssh.close()

def stopCssserver(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Stopping Cssserver!")
    ssh.connect(strIp, username=strCssserver, password=strCssserverPw)
    sendCommand('./cssserver stop', update, context)
    ssh.close()

def startMcserver(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Starting Minecraft server")
    ssh.connect(strIp, username=strMcserver, password=strMcserverPw)
    sendCommand('./mcserver start', update, context)
    ssh.close()

def stopMcserver(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Stopping Minecraft server")
    ssh.connect(strIp, username=strMcserver, password=strMcserverPw)
    sendCommand('./mcserver stop', update, context)
    ssh.close()


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

def sendCommand(strCommand, update, context):
    stdin, stdout, stderr = ssh.exec_command(strCommand)
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Success")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Error")
        stdoutLines = stdout.readlines()
        output = ""
        for line in stdoutLines:
            output=output+line
        context.bot.send_message(chat_id=update.effective_chat.id, text=output)

# Create handlers
help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)

wakeUpAllspark_handler = CommandHandler('wakeup', wakeUpAllspark)
dispatcher.add_handler(wakeUpAllspark_handler)

sleepAllspark_handler = CommandHandler('sleep', sleepAllspark)
dispatcher.add_handler(sleepAllspark_handler)

startArkserver_handler = CommandHandler('startArkserver', startArkserver)
dispatcher.add_handler(startArkserver_handler)

stopArkserver_handler = CommandHandler('stopArkserver', stopArkserver)
dispatcher.add_handler(stopArkserver_handler)

startCssserver_handler = CommandHandler('startCssserver', startCssserver)
dispatcher.add_handler(startCssserver_handler)

stopCssserver_handler = CommandHandler('stopCssserver', stopCssserver)
dispatcher.add_handler(stopCssserver_handler)

startMcserver_handler = CommandHandler('startMcserver', startMcserver)
dispatcher.add_handler(startMcserver_handler)

stopMcserver_handler = CommandHandler('stopMcserver', stopMcserver)
dispatcher.add_handler(stopMcserver_handler)

inline_handler = InlineQueryHandler(inline)
dispatcher.add_handler(inline_handler)

echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)

updater.start_polling()
