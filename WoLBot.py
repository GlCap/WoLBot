import logging
import subprocess
import socket
import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import KeyboardButton, ReplyKeyboardMarkup

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

""" Bot Config:"""

"""Telegram BOT API Token"""
bot_token = "TOKEN"
"""IP or HostName of the desired server"""
server_ip = "IP/HostName"
""" Server port to use to check online/offline state """
server_port_check = 80
"""Server name"""
server_name = "SERVER_NAME"
"""List containing authorized usernames"""
authorized_users = ["autorized", "usernames"]
"""Server admin chat_id to send logging messages """
admin_id = "server admin chat_id"
"""Command to execute on the machine running the bot telegram to wake the desired server"""
wake_cmd = "wake on lan command"
"""Command to execute on the machine running the bot telegram to shutdown the desired server"""
shutdown_cmd = "shutdown command"
"""List containing currently connected users"""
connected_users = []

""" Output messages:"""

""" Message sent when the user prompts the /start command"""
welcome_text = "Welcome "
""" Message sent when the user prompts the /help command"""
help_text = "todo"
""" Message sent when the user prompts an invalid command"""
not_valid_text = " is not a valid command."
""" Message sent when the user prompts the /login command"""
wake_text = "Waking " + server_name + '.'
""" Message sent when the user prompts the /logout command"""
shutdown_text = "Shutting down " + server_name + '.'
""" Message sent when the user prompts the /status command"""
status_text = "Checking " + server_name + " current status:"
""" Message response on online status check"""
online_text = server_name + ": Online."
""" Message response on offline status check"""
offline_text = server_name + ": Offline."
""" Message sent when the user prompts the /start command"""
error_auth_text = "You are not authorized."
""" Message sent when the user logs in"""
login_text = "You are now logged in, remember to logout."
""" Message sent when the user logs out"""
logout_text = "Logout successful, goodbye!"
""" Message sent when the user tries to login while being already logged in"""
error_already_loggedin = "You are already logged in."
""" Message sent when the user tries to login while being already logged out"""
error_already_loggedout =  "You are already logged out."

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    now = datetime.datetime.now()
    
    if hasattr(not update.message.from_user, 'username'):
        bot.send_message(chat_id=update.message.chat_id, text=error_auth_text)
        logger.info("Someone executed /start command at " + now.strftime("%Y-%m-%d %H:%M:%S"))
        return
   
    username = '@' + update.message.from_user.username
    logger.info(username + " executed /start command at " + now.strftime("%Y-%m-%d %H:%M:%S"))
    
    if username in authorized_users:
        kb = [
            [KeyboardButton('/login')],
            [KeyboardButton('/logout')],
            [KeyboardButton('/status')]
            ]
        kb_markup = ReplyKeyboardMarkup(kb, resize_keyboard=True)
        bot.send_message(chat_id=update.message.chat_id, text=welcome_text + username , reply_markup=kb_markup)
    else:
        bot.send_message(chat_id=update.message.chat_id, text=error_auth_text)


def help(bot, update):
    """Send a message when the command /help is issued."""
    now = datetime.datetime.now()
    
    if hasattr(not update.message.from_user, 'username'):
        bot.send_message(chat_id=update.message.chat_id, text=error_auth_text)
        logger.info("Someone executed /help command at " + now.strftime("%Y-%m-%d %H:%M:%S"))
        return

    username = '@' + update.message.from_user.username
    logger.info(username + " executed /help command at " + now.strftime("%Y-%m-%d %H:%M:%S"))

    if username in authorized_users:
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
    
    if hasattr(not update.message.from_user, 'username'):
        bot.send_message(chat_id=update.message.chat_id, text=error_auth_text)
        logger.info("Someone executed /wake command at " + now.strftime("%Y-%m-%d %H:%M:%S"))
        return

    username = '@' + update.message.from_user.username
    logger.info(username + " executed /login command at " + now.strftime("%Y-%m-%d %H:%M:%S"))
    
    if username in authorized_users:
        if username not in connected_users:
            if not connected_users:
                connected_users.append(username)
                subprocess.call(wake_cmd)
                bot.send_message(chat_id=update.message.chat_id, text=wake_text)
                bot.send_message(chat_id=admin_id, text=username + " logged in, " + server_name + " is waking up.")
            else:
                connected_users.append(username)
                bot.send_message(chat_id=update.message.chat_id, text=login_text)
                bot.send_message(chat_id=admin_id, text=username + " logged in.")
        else:
            bot.send_message(chat_id=update.message.chat_id, text=error_already_loggedin)
    else:
        bot.send_message(chat_id=update.message.chat_id, text=error_auth_text)

def shutdown(bot, update):
    now = datetime.datetime.now()
    
    if hasattr(not update.message.from_user, 'username'):
        bot.send_message(chat_id=update.message.chat_id, text=error_auth_text)
        logger.info("Someone executed /logout command at " + now.strftime("%Y-%m-%d %H:%M:%S"))
        return

    username = '@' + update.message.from_user.username
    logger.info(username + " executed /logout command at " + now.strftime("%Y-%m-%d %H:%M:%S"))

    if username in authorized_users:
        if username in connected_users:
            connected_users.remove(username)
            if not connected_users:
                subprocess.call(shutdown_cmd)
                bot.send_message(chat_id=update.message.chat_id, text='@' + shutdown_text)
                bot.send_message(chat_id=admin_id, text='@' + username + " logged out, "+ server_name +" is shutting down.")
            else:
                bot.send_message(chat_id=update.message.chat_id, text=logout_text)
                bot.send_message(chat_id=admin_id, text='@' + username + " logged out.")
        else:
            bot.send_message(chat_id=update.message.chat_id, text=error_already_loggedout)
    else:
        bot.send_message(chat_id=update.message.chat_id, text=error_auth_text)

def status(bot, update):
    now = datetime.datetime.now()
    
    if hasattr(not update.message.from_user, 'username'):
        bot.send_message(chat_id=update.message.chat_id, text=error_auth_text)
        logger.info("Someone executed /status command at " + now.strftime("%Y-%m-%d %H:%M:%S"))
        return

    username = '@' + update.message.from_user.username
    logger.info(username + " executed /status command at " + now.strftime("%Y-%m-%d %H:%M:%S"))

    if username in authorized_users:
        bot.send_message(chat_id=update.message.chat_id, text=status_text)
        bot.send_message(chat_id=update.message.chat_id, text="Connected users:\n" + "\n".join(connected_users))
        if is_connected():
            bot.send_message(chat_id=update.message.chat_id, text=online_text)
        else:
            bot.send_message(chat_id=update.message.chat_id, text=offline_text)
    else:
        bot.send_message(chat_id=update.message.chat_id, text=error_auth_text)

def is_connected():
    try:
        host = socket.gethostbyname(server_ip)
        socket.create_connection((host, server_port_check), 2)
        return True
    except:
        return False

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(bot_token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("login", wake))
    dp.add_handler(CommandHandler("logout", shutdown))
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
