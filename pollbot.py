from telegram.ext import *
from telegram import *

updater = Updater(token='5374066926:AAE7IMAU8bjduSafS1DAzjk6Kpz6X9zIHQ0')
dispatcher = updater.dispatcher
START_MESSAGE = 'This bot will help you create an order list, check your outstanding payments, or split money! use /start to begin!'
newOrder = [0]
TITLE_ARRAY = []

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

    if query.data == "Add Order":
        print(update)

def NewOrder(update: Update, context: CallbackContext):
    update.message.reply_text('What will the title of your Order List be?')
    newOrder[0] = 1

def orderList(update: Update, context: CallbackContext) -> None:
    if newOrder[0] == 1:
        text = f"{update.message.text}\n\n\nOrders: "
        title = f"{update.message.text}"
        ORDER_MESSAGE_BUTTONS = [
            [InlineKeyboardButton('Publish Order List', switch_inline_query=title)],
            [
                InlineKeyboardButton('Close Order', callback_data='Close Order'),
                InlineKeyboardButton('Open Order', callback_data='Open Order')
            ]
        ]
        TITLE_ARRAY.append(title)
        reply_markup = InlineKeyboardMarkup(ORDER_MESSAGE_BUTTONS)
        update.message.reply_text(
            text=text,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
        newOrder[0] = 0
    else:
        update.message.reply_text(START_MESSAGE)

def inlineOrderList(update: Update, context: CallbackContext):
    results = []
    ORDER_BUTTONS = [
        [
            InlineKeyboardButton('Add Order', callback_data='Add Order'),
            InlineKeyboardButton('Edit Order', callback_data='Edit Order'),
            InlineKeyboardButton('Copy Order', callback_data='Copy Order')
        ]
    ]
    for title in TITLE_ARRAY:
      results.append(
        InlineQueryResultArticle(
            id=title,
            title=title,
            input_message_content=InputTextMessageContent(title + '\n\n\nOrders:'),
            reply_markup=InlineKeyboardMarkup(ORDER_BUTTONS)
        )
      )
    update.inline_query.answer(results)

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
    dispatcher.add_handler(InlineQueryHandler(inlineOrderList))

    updater.start_polling()
    updater.idle()

main()