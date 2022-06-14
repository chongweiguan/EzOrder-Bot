from telegram import *
from telegram.ext import *
from OrderList import OrderList
from backEnd import backEnd
from user import User

updater = Updater('5316303881:AAEIysIUYoZ45d1EwN_5Jl6dGonJfv_ZE8g')
dispatcher = updater.dispatcher
START_MESSAGE = 'This bot will help you create an order list, check your outstanding payments, or split money! use /start to begin!'
botURL = 'https://t.me/ezezezezezorderbot'
backEnd = backEnd()
listId = 1


def startCommand(update: Update, context: CallbackContext) -> None:
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


def addCommand(update: Update, context: CallbackContext) -> None:
    userId = update.message.from_user.id
    user = backEnd.getUser(userId)

    if user is None or not user.Adding:
        update.message.reply_text("To use this command click Add Order on an active Order List")
    if user.Adding:
        user.addingCommand = True
        update.message.reply_text("Adding Order for: \n\n" + backEnd.OrderLists[user.addingID].fullList())
        update.message.reply_text("What is your Order?")



def prompts(update: Update, context: CallbackContext):
    userId = update.message.from_user.id
    user = backEnd.getUser(userId)

    if user is None or (user.Adding == False and user.Ordering == False):
        update.message.reply_text(START_MESSAGE)
        return

    if user.addingCommand:
        return AddingOrder(update, context)

    if backEnd.latestList(userId).phoneNum == "" and \
            backEnd.latestList(userId).Title == "":
        backEnd.latestList(userId).Title = update.message.text
        user.titleList.append(update.message.text)
        update.message.reply_text('What is your phone number? ')
        return

    if backEnd.latestList(userId).phoneNum == "":
        backEnd.latestList(userId).phoneNum = update.message.text
        backEnd.getUser(userId).ordering = False
        return orderList(update, context)




def response(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    query.answer()
    if query.data == "New Order":
        return NewOrder(query, context)
    if query.data[0:9] == "Add Order":
        update.message = query.data[9:]
        index = int(query.data[9:])
        # check if user is in backend, if not add the user in. Then add the orderList into the user
        # change users.adding to true
        userId = update.callback_query.from_user.id
        if not backEnd.isUser(userId):
            backEnd.addUser(userId)
        currentUser = backEnd.getUser(userId)
        currentUser.addingID = index
        currentUser.addingUpdate = update
        currentList = backEnd.OrderLists[index]
        currentUser.Adding = True
        currentUser.memberLists[index] = currentList


def NewOrder(update: Update, context: CallbackContext) -> None:
    # instantiate a user and set the users Ordering to True
    userId = update.message.chat.id
    backEnd.addUser(userId)
    user = backEnd.getUser(userId)
    user.Ordering = True
    # instantiate a OrderList and add it to backend
    global listId
    orderingList = OrderList(listId, "", "", [], [])
    backEnd.OrderLists.append(orderingList)
    # add the orderList to the users creators list
    user.creatorLists.append(orderingList)
    listId += 1
    # add the user to backend userList if not inside alr
    update.message.reply_text('What will the title of your Order List be?')


def orderList(update: Update, context: CallbackContext) -> None:
    userId = update.message.from_user.id

    keyboard = [
        [InlineKeyboardButton('Publish Order List',
                              switch_inline_query=backEnd.latestList(userId).Title)],
        [
            InlineKeyboardButton('Close Order', callback_data='Close Order'),
            InlineKeyboardButton('Open Order', callback_data='Open Order')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        text=backEnd.latestList(userId).fullList(),
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )


def inlineOrderList(update: Update, context: CallbackContext):
    userId = update.inline_query.from_user.id
    user = backEnd.getUser(userId)

    results = []

    for title in user.titleList:
        index = backEnd.getOrderIndex(title)
        ORDER_BUTTONS = [
            [InlineKeyboardButton('Add Order', callback_data='Add Order' + str(index))],
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
    userId = update.message.from_user.id
    user = backEnd.getUser(userId)

    backEnd.OrderLists[user.addingID].peopleList.append(user_name)
    backEnd.OrderLists[user.addingID].orders.append(added_order)
    text = backEnd.OrderLists[int(user.addingUpdate.message)].fullList()

    ORDER_BUTTONS = [
        [InlineKeyboardButton('Add Order', callback_data='Add Order' + user.addingUpdate.message)],
        [InlineKeyboardButton('Edit Order', callback_data='Edit Order')],
        [InlineKeyboardButton('Copy Order', callback_data='Copy Order')],
        [InlineKeyboardButton('Bot Chat', url=botURL)]
    ]

    update.message.reply_text(text)
    user.addingUpdate.callback_query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(ORDER_BUTTONS)
    )
    backEnd.getUser(userId).Adding = False
    backEnd.getUser(userId).addingCommand = False


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
    dispatcher.add_handler(CommandHandler("add", addCommand))
    dispatcher.add_handler(CallbackQueryHandler(response))
    dispatcher.add_error_handler(error)
    dispatcher.add_handler(MessageHandler(Filters.text, prompts))
    # dispatcher.add_handler(MessageHandler(Filters.text, phoneNumber))
    dispatcher.add_handler(InlineQueryHandler(inlineOrderList))
    updater.start_polling()
    updater.idle()


main()
