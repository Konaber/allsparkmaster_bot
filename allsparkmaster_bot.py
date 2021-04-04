from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import InlineQueryHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent
from wakeonlan import send_magic_packet
import logging
import paramiko
import time

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

#logging.basicConfig(filename='cheetor.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Thread locking functions
bThreadLocked = False

def getThreadLocked():
    return bThreadLocked

def setThreadLocked():
    global bThreadLocked
    bThreadLocked = True

def setThreadUnlocked():
    global bThreadLocked
    bThreadLocked = False

# Server running functions
bArkserver = False
bCssserver = False
bMcserver = False

def setArkserverStarted():
    logging.debug(setArkserverStarted.__name__)
    global bArkserver
    bArkserver = True

def setArkserverStopped():
    logging.debug(setArkserverStopped.__name__)
    global bArkserver
    bArkserver = False

def getArkserverStatus():
    logging.debug(getArkserverStatus.__name__)
    return bArkserver

def setCssserverStarted():
    logging.debug(setCssserverStarted.__name__)
    global bCssserver
    bCssserver = True

def setCssserverStopped():
    logging.debug(setCssserverStopped.__name__)
    global bCssserver
    bCssserver = False

def getCssserverStatus():
    logging.debug(getCssserverStatus.__name__)
    return bCssserver

def setMcserverStarted():
    logging.debug(setMcserverStarted.__name__)
    global bMcserver
    bMcserver = True

def setMcserverStopped():
    logging.debug(setMcserverStopped.__name__)
    global bMcserver
    bMcserver = False

def getMcserverStatus():
    logging.debug(getMcserverStatus.__name__)
    return bMcserver

# Functions for handlers
def help(update, context):
    logging.debug(help.__name__)
    sendMessage(strHelp, update, context)

def wakeUpAllspark(update, context):
    logging.info(wakeUpAllspark.__name__)
    if False == getThreadLocked():
        setThreadLocked()
        send_magic_packet(strMac)
        sendMessage("The Allspark will wake up!", update, context)
        time.sleep(30)
        retValue = connectSsh(strIp, strCommodus, strCommodusPw, update, context)
        if True == retValue:
            str = "The Allspark is awake"
            logging.info(str)
            context.bot.send_message(chat_id=update.effective_chat.id, text=str)
        else:
            str = "ERROR: The Allspark is still sleeping"
            logging.info(str)
            sendMessage(str, update, context)
        ssh.close()
        setThreadUnlocked()
    else:
        str = "Allspark is busy, wait for last command to finish"
        logging.info(str)
        sendMessage(str, update, context)

def sleepAllspark(update, context):
    logging.info(sleepAllspark.__name__)
    if False == getThreadLocked():
        setThreadLocked()
        if (False == getArkserverStatus()) and (False == getCssserverStatus()) and (False == getMcserverStatus()):
            sendMessage("The Allspark will sleep!", update, context)
            retValue = connectSsh(strIp, strCommodus, strCommodusPw, update, context)
            if True == retValue:
                stdin, stdout, stderr = ssh.exec_command('sudo shutdown -P now', get_pty=True)
                time.sleep(1)
                stdin.write(strCommodusPw)
                stdin.write("\n")
                time.sleep(1)
                stdin.flush()
            ssh.close()
        else:
            sendMessage("ERROR: Check running servers!", update, context)
        setThreadUnlocked()
    else:
        sendMessage("Allspark is busy, wait for last command to finish", update, context)

def startArkserver(update, context):
    logging.info(startArkserver.__name__)
    if False == getThreadLocked():
        setThreadLocked()
        sendMessage("Starting Arkserver", update, context)
        retValue = connectSsh(strIp, strArkserver, strArkserverPw, update, context)
        if True == retValue:
            sendCommand('./arkserver start', update, context)
            setArkserverStarted()
        ssh.close()
        setThreadUnlocked()
    else:
        sendMessage("Allspark is busy, wait for last command to finish", update, context)

def stopArkserver(update, context):
    logging.info(stopArkserver.__name__)
    if False == getThreadLocked():
        setThreadLocked()
        sendMessage("Stopping Arkserver", update, context)
        retValue = connectSsh(strIp, strArkserver, strArkserverPw, update, context)
        if True == retValue:
            sendCommand('./arkserver stop', update, context)
            setArkserverStopped()
        ssh.close()
        setThreadUnlocked()
    else:
        sendMessage("Allspark is busy, wait for last command to finish", update, context)

def statusArkserver(update, context):
    logging.info(statusArkserver.__name__)
    if False == getThreadLocked():
        setThreadLocked()
        sendMessage("Getting status of Arkserver", update, context)
        retValue = connectSsh(strIp, strArkserver, strArkserverPw, update, context)
        if True == retValue:
            stdout = sendCommand('./arkserver monitor', update, context)
            stdoutLines = stdout.readlines()
            output = ""
            for line in stdoutLines:
                output=output+line
                context.bot.send_message(chat_id=update.effective_chat.id, text=output)
        ssh.close()
        setThreadUnlocked()
    else:
        sendMessage("Allspark is busy, wait for last command to finish", update, context)

def startCssserver(update, context):
    logging.info(startCssserver.__name__)
    if False == getThreadLocked():
        setThreadLocked()
        sendMessage("Starting Cssserver!", update, context)
        retValue = connectSsh(strIp, strCssserver, strCssserverPw, update, context)
        if True == retValue:
            sendCommand('./cssserver start', update, context)
            setCssserverStarted()
        ssh.close()
        setThreadUnlocked()
    else:
        sendMessage("Allspark is busy, wait for last command to finish", update, context)

def stopCssserver(update, context):
    logging.info(stopCssserver.__name__)
    if False == getThreadLocked():
        setThreadLocked()
        sendMessage("Stopping Cssserver!", update, context)
        retValue = connectSsh(strIp, strCssserver, strCssserverPw, update, context)
        if True == retValue:    
            sendCommand('./cssserver stop', update, context)
            setCssserverStopped()
        ssh.close()
        setThreadUnlocked()
    else:
        sendMessage("Allspark is busy, wait for last command to finish", update, context)

def startMcserver(update, context):
    logging.info(startMcserver.__name__)
    if False == getThreadLocked():
        setThreadLocked()
        sendMessage("Starting Minecraft server", update, context)
        retValue = connectSsh(strIp, strMcserver, strMcserverPw, update, context)
        if True == retValue:
            sendCommand('./mcserver start', update, context)
            setMcserverStarted()
        ssh.close()
        setThreadUnlocked()
    else:
        sendMessage("Allspark is busy, wait for last command to finish", update, context)

def stopMcserver(update, context):
    logging.info(stopMcserver.__name__)
    if False == getThreadLocked():
        setThreadLocked()
        sendMessage("Stopping Minecraft server", update, context)
        retValue = connectSsh(strIp, strMcserver, strMcserverPw, update, context)
        if True == retValue:
            sendCommand('./mcserver stop', update, context)
            setMcserverStopped()
        ssh.close()
        setThreadUnlocked()
    else:
        sendMessage("Allspark is busy, wait for last command to finish", update, context)

def secretReset(update, context):
    logging.warn(secretReset.__name__)
    ssh.close()
    setThreadUnlocked()

def unknown(update, context):
    sendMessage("Sorry, I didn't understand that command. See /help for my commands", update, context)

def sendCommand(strCommand, update, context):
    stdin, stdout, stderr = ssh.exec_command(strCommand)
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        sendMessage("Success", update, context)
    else:
        sendMessage("Error", update, context)
        stdoutLines = stdout.readlines()
        output = ""
        for line in stdoutLines:
            output=output+line
        sendMessage(output, update, context)
    return stdout

def connectSsh(strIp, strUsername, strPassword, update, context):
    retValue = False
    try:
        ssh.connect(strIp, username=strUsername, password=strPassword, timeout=10)
        retValue = True
    except:
        sendMessage("ERROR: SSH exception, is the Allspark awake?", update, context)
        retValue = False
    return retValue

def sendMessage(strMessage, update, context):
    try:
        context.bot.send_message(chat_id=update.effective_chat.id, text=strMessage, timeout=10, allow_sending_without_reply=True)
    except:
        logging.error(sendMessage.__name__ + "; " + strMessage)

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

statusArkserver_handler = CommandHandler('statusArkserver', statusArkserver)
dispatcher.add_handler(statusArkserver_handler)

startCssserver_handler = CommandHandler('startCssserver', startCssserver)
dispatcher.add_handler(startCssserver_handler)

stopCssserver_handler = CommandHandler('stopCssserver', stopCssserver)
dispatcher.add_handler(stopCssserver_handler)

startMcserver_handler = CommandHandler('startMcserver', startMcserver)
dispatcher.add_handler(startMcserver_handler)

stopMcserver_handler = CommandHandler('stopMcserver', stopMcserver)
dispatcher.add_handler(stopMcserver_handler)

secretReset_handler = CommandHandler('secretReset', secretReset)
dispatcher.add_handler(secretReset_handler)

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

updater.start_polling(drop_pending_updates=True)