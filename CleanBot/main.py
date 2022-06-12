from telegram.ext import *
from telegram import *
from backEnd import backEnd
from OrderList import OrderList
from Secrets import API_Token, Bot_URL

updater = Updater(token=API_Token)
dispatcher = updater.dispatcher
START_MESSAGE = 'This bot will help you create an order list, check your outstanding payments, or split money! use /start to begin!'
botURL = Bot_URL
backEnd = backEnd([], [], [])
TITLE_ARRAY = []
inlineChat = []
inlineChat.append("")
orderIndex = []
orderIndex.append("")

def startCommand(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [
            InlineKeyboardButton("New Order", callback_data="New Order"),
            InlineKeyboardButton("Check", callback_data="Check"),
            InlineKeyboardButton("Split", callback_data="Split")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if backEnd.Adding == True:
        update.message.reply_text("Adding Order for: \n\n" + backEnd.OrderLists[orderIndex[0]].fullList())
        update.message.reply_text("What is your Order?")
    else:
        update.message.reply_text("Hi! I am EzOrder Bot, I am here to make your life a little bit"
                              "easier Here are some commands to interact with me!",
                              reply_markup=reply_markup)


def prompts(update: Update, context: CallbackContext):
    if backEnd.Ordering == False and backEnd.Checking == False and backEnd.Splitting == False and backEnd.Adding == False:
        update.message.reply_text(START_MESSAGE)

    if backEnd.OrderLists[len(backEnd.OrderLists)-1].phoneNum == "" and \
            backEnd.OrderLists[len(backEnd.OrderLists)-1].Title == "":
        backEnd.OrderLists[len(backEnd.OrderLists)-1].Title = update.message.text
        TITLE_ARRAY.append(update.message.text)
        update.message.reply_text('What is your phone number? ')
        return

    if backEnd.OrderLists[len(backEnd.OrderLists)-1].phoneNum == "":
        backEnd.OrderLists[len(backEnd.OrderLists) - 1].phoneNum = update.message.text
        backEnd.Ordering = False
        return orderList(update, context)

    if backEnd.Adding == True:
        return AddingOrder(update, context)



def response(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    query.answer()
    if query.data == "New Order":
        return NewOrder(query,context)
    if query.data[0:9] == "Add Order":
        update.message = query.data[9:]
        index = int(query.data[9:])
        orderIndex[0] = index
        backEnd.Adding = True
        inlineChat[0] = update

def NewOrder(update: Update, context: CallbackContext) -> None:
    orderlist = OrderList("", "", [], [])
    backEnd.OrderLists.append(orderlist)
    backEnd.Ordering = True
    update.message.reply_text('What will the title of your Order List be?')

def orderList(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton('Publish Order List', switch_inline_query=backEnd.OrderLists[len(backEnd.OrderLists) - 1].Title)],
        [
            InlineKeyboardButton('Close Order', callback_data='Close Order'),
            InlineKeyboardButton('Open Order', callback_data='Open Order')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        text=backEnd.OrderLists[len(backEnd.OrderLists) - 1].fullList(),
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

def inlineOrderList(update: Update, context: CallbackContext):
    results = []
    for title in TITLE_ARRAY:
        index = backEnd.getOrderIndex(title)
        ORDER_BUTTONS = [
            [InlineKeyboardButton('Add Order', callback_data='Add Order'+str(index))],
            [InlineKeyboardButton('Edit Order', callback_data='Edit Order')],
            [InlineKeyboardButton('Copy Order', callback_data='Copy Order')],
            [InlineKeyboardButton('Bot Chat', url=botURL)]
        ]
        results.append(
            InlineQueryResultArticle(
                id=title,
                title=title,
                input_message_content=InputTextMessageContent(backEnd.OrderLists[index].fullList()),
                reply_markup=InlineKeyboardMarkup(ORDER_BUTTONS),
            )
          )
    update.inline_query.answer(results)

def AddingOrder(update: Update, context: CallbackContext) -> None:
    user_name = f'{update.message.from_user.first_name}'
    added_order = update.message.text

    backEnd.OrderLists[orderIndex[0]].peopleList.append(user_name)
    backEnd.OrderLists[orderIndex[0]].orders.append(added_order)
    text = backEnd.OrderLists[int(inlineChat[0].message)].fullList()

    ORDER_BUTTONS = [
        [InlineKeyboardButton('Add Order', callback_data='Add Order' + (inlineChat[0].message))],
        [InlineKeyboardButton('Edit Order', callback_data='Edit Order')],
        [InlineKeyboardButton('Copy Order', callback_data='Copy Order')],
        [InlineKeyboardButton('Bot Chat', url=botURL)]
    ]

    update.message.reply_text(text)
    inlineChat[0].callback_query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(ORDER_BUTTONS)
    )
    backEnd.Adding = False



def error(update, context):
    print(f"Update {update} caused error {context.error}")

def cancel(update: Update, _: CallbackContext) -> None:
    backEnd.Ordering = False
    backEnd.Checking = False
    backEnd.Splitting = False
    backEnd.OrderLists = []
    backEnd.CheckLists = []
    backEnd.SplitLists = []
    TITLE_ARRAY = []
    update.message.reply_text('Order List creation has been canceled.')

def main():
    dispatcher.add_handler(CommandHandler("start", startCommand))
    dispatcher.add_handler(CommandHandler("cancel", cancel))
    dispatcher.add_handler(CallbackQueryHandler(response))
    dispatcher.add_error_handler(error)
    dispatcher.add_handler(MessageHandler(Filters.text, prompts))
    #dispatcher.add_handler(MessageHandler(Filters.text, phoneNumber))
    dispatcher.add_handler(InlineQueryHandler(inlineOrderList))
    updater.start_polling()
    updater.idle()

main()
