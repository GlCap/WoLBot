import logging
import subprocess
import socket
import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

server = "IP/HostName"
authorized_users = ["authorized", "user", "names"]

""" Output messages"""
welcome_text = 'Welcome!'
error_auth_text = "Not Authorized."
help_text = 'Help!'
not_valid_text = " is not a valid command!"
wake_text = "Waking server..."
shutdown_text = "Shutting down server..."
status_text = "Checking Server Status..."
online_text = "Server is Online."
offline_text = "Server is Offline."

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    now = datetime.datetime.now()
    logger.info(update.message.from_user.username + " executed /start command at " + now.strftime("%Y-%m-%d %H:%M:%S"))
    
    if hasattr(not update.message.from_user, 'username'):
        bot.send_message(chat_id=update.message.chat_id, text=error_auth_text)
        return

    if update.message.from_user.username in authorized_users:
        bot.send_message(chat_id=update.message.chat_id, text=welcome_text)
    else:
        bot.send_message(chat_id=update.message.chat_id, text=error_auth_text)


def help(bot, update):
    """Send a message when the command /help is issued."""
    now = datetime.datetime.now()
    logger.info(update.message.from_user.username + " executed /help command at " + now.strftime("%Y-%m-%d %H:%M:%S"))

    if hasattr(not update.message.from_user, 'username'):
        bot.send_message(chat_id=update.message.chat_id, text=error_auth_text)
        return

    if update.message.from_user.username in authorized_users:
        bot.send_message(chat_id=update.message.chat_id, text=help_text)
    else:
        bot.send_message(chat_id=update.message.chat_id, text=error_auth_text)

def echo(bot, update):
    """Echo the user message."""
    bot.send_message(chat_id=update.message.chat_id, text=update.message.text + not_valid_text)

def error(bot, update):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', bot, update.error)

def wake(bot, update):
    now = datetime.datetime.now()
    logger.info(update.message.from_user.username + " executed /wake command at " + now.strftime("%Y-%m-%d %H:%M:%S"))

    if hasattr(not update.message.from_user, 'username'):
        bot.send_message(chat_id=update.message.chat_id, text=error_auth_text)
        return

    if update.message.from_user.username in authorized_users:
        subprocess.call("wol_media.sh")
        bot.send_message(chat_id=update.message.chat_id, text=wake_text)
    else:
        bot.send_message(chat_id=update.message.chat_id, text=error_auth_text)

def shutdown(bot, update):
    now = datetime.datetime.now()
    logger.info(update.message.from_user.username + " executed /shutdown command at " + now.strftime("%Y-%m-%d %H:%M:%S"))

    if hasattr(not update.message.from_user, 'username'):
        bot.send_message(chat_id=update.message.chat_id, text=error_auth_text)
        return

    if update.message.from_user.username in authorized_users:
        subprocess.call("media_shutdown.sh")
        bot.send_message(chat_id=update.message.chat_id, text=shutdown_text)
    else:
        bot.send_message(chat_id=update.message.chat_id, text=error_auth_text)

def status(bot, update):
    now = datetime.datetime.now()
    logger.info(update.message.from_user.username + " executed /status command at " + now.strftime("%Y-%m-%d %H:%M:%S"))

    if hasattr(not update.message.from_user, 'username'):
        bot.send_message(chat_id=update.message.chat_id, text=error_auth_text)
        return

    if update.message.from_user.username in authorized_users:
        bot.send_message(chat_id=update.message.chat_id, text=status_text)
        if is_connected():
            bot.send_message(chat_id=update.message.chat_id, text=online_text)
        else:
            bot.send_message(chat_id=update.message.chat_id, text=offline_text)
    else:
        bot.send_message(chat_id=update.message.chat_id, text=error_auth_text)

def is_connected():
    try:
        host = socket.gethostbyname(server)
        socket.create_connection((host, 80), 2)
        return True
    except:
        return False

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("TOKEN")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("wake", wake))
    dp.add_handler(CommandHandler("shutdown", shutdown))
    dp.add_handler(CommandHandler("status", status))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

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