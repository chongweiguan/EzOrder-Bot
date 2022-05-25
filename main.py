import logging
from telegram.ext import *
from telegram import *
from requests import *

print("Bot started...")

updater = Updater(token='5374066926:AAE7IMAU8bjduSafS1DAzjk6Kpz6X9zIHQ0')
dispatcher = updater.dispatcher

def startCommand(update: Update, context: CallbackContext) -> None:
    """Sends a message with three inline buttons attached."""
    keyboard = [
        [
            InlineKeyboardButton("New Order", callback_data="New Order"),
            InlineKeyboardButton("Check", callback_data="Check"),
            InlineKeyboardButton("Split", callback_data="Split")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Hi! I am EzOrder Bot, I am here to make your life a little bit"
                              "easier Here are some commands to interact with me!",
                              reply_markup=reply_markup)

def error(update, context):
    print(f"Update {update} caused error {context.error}")

def main():
    dispatcher.add_handler(CommandHandler("start", startCommand))
    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()

main()