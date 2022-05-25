from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

ORDER_MESSAGE_BUTTONS = [
    [InlineKeyboardButton('Publish',
                          url='https://docs.python-telegram-bot.org/en/stable/telegram.inlinekeyboardbutton.html')]
]


def start_command(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('What will the title of your Order List be?')

    return ORDER


def orderList(update: Update, _: CallbackContext) -> None:
    text = f"{update.message.text}\n\n\nOrders: "
    reply_markup = InlineKeyboardMarkup(ORDER_MESSAGE_BUTTONS)
    update.message.reply_text(
        text=text,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

    return ConversationHandler.END


def cancel(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Order List creation has been canceled.')


ORDER = range(1)


def main() -> None:
    token = '5374066926:AAE7IMAU8bjduSafS1DAzjk6Kpz6X9zIHQ0'
    updater = Updater(token)
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler(
            'start', start_command)],
        states={
            ORDER: [MessageHandler(Filters.text, orderList)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

main()