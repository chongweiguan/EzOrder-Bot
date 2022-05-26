from telegram.ext import *
from telegram import *

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


def response(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    query.answer()
    if query.data == "New Order":
        return NewOrder(query,context)

def NewOrder(update: Update, context: CallbackContext):
    update.message.reply_text('What will the title of your Order List be?')
    return ConversationHandler.END

def orderList(update: Update, _: CallbackContext) -> None:
    ORDER_MESSAGE_BUTTONS = [
        [InlineKeyboardButton('Publish',
                              url='https://docs.python-telegram-bot.org/en/stable/telegram.inlinekeyboardbutton.html')]
    ]
    text = f"{update.message.text}\n\n\nOrders: "
    reply_markup = InlineKeyboardMarkup(ORDER_MESSAGE_BUTTONS)
    update.message.reply_text(
        text=text,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )
    print(update.callback_query)
    return ConversationHandler.END

def check(update: Update, _: CallbackContext) -> None:
    print(update)

def cancel(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Order List creation has been canceled.')

def error(update, context):
    print(f"Update {update} caused error {context.error}")

ORDER = range(1)

def main():
    dispatcher.add_handler(CommandHandler("start", startCommand))
    dispatcher.add_handler(CallbackQueryHandler(response))
    dispatcher.add_error_handler(error)
    dispatcher.add_handler(MessageHandler(Filters.text, orderList))

 #   conv_handler = ConversationHandler(
 #       entry_points=[dispatcher.add_handler(CallbackQueryHandler(response))],
 #       states={
 #           ORDER: [MessageHandler(Filters.text, orderList)]
 #       },
 #       fallbacks=[CommandHandler('cancel', cancel)],
 #   )
 #   dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

main()