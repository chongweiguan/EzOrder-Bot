from telegram import *
from telegram.ext import *
from OrderList import OrderList
from backEnd import backEnd
from user import User

updater = Updater('5374066926:AAE7IMAU8bjduSafS1DAzjk6Kpz6X9zIHQ0')
dispatcher = updater.dispatcher
START_MESSAGE = 'This bot will help you create an order list, check your outstanding payments, or split money! use /start to begin!'
botURL = 'https://t.me/ezordertest_bot'
backEnd = backEnd()
listId = 0


def startCommand(update: Update, context: CallbackContext) -> None:
    userId = update.message.from_user.id
    if not backEnd.isUser(userId):
        backEnd.addUser(userId)
    user = backEnd.getUser(userId)
    user.personalUpdate = update
    keyboard = [
        [
            InlineKeyboardButton("New Order", callback_data="135New Order"),
            InlineKeyboardButton("Check", callback_data="135Check"),
            InlineKeyboardButton("Split", callback_data="135Split")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Hi! I am EzOrder Bot, I am here to make your life a little bit"
                              "easier Here are some commands to interact with me!",
                              reply_markup=reply_markup)


def addCommand(update: Update, context: CallbackContext) -> None:
    userId = update.message.from_user.id
    user = backEnd.getUser(userId)
    user_name = f'{update.message.from_user.first_name}'

    if user is None or not user.Adding:
        update.message.reply_text("To use this command click Add Order on an active Order List")
        return
    if user_name in backEnd.OrderLists[user.listID].peopleList:
        update.message.reply_text("You have already added your order!")
        user.Adding = False
        return
    if user.Adding:
        user.addingCommand = True
        update.message.reply_text("Adding Order for: " + backEnd.OrderLists[user.listID].Title)
        update.message.reply_text("What is your Order?")


def deleteCommand(update: Update, context: CallbackContext) -> None:
    userId = update.message.from_user.id
    user = backEnd.getUser(userId)
    user_name = f'{update.message.from_user.first_name}'

    if user is None or not user.Deleting:
        update.message.reply_text("To use this command click Delete Order on an active Order List")
        return
    if user_name not in backEnd.OrderLists[user.listID].peopleList:
        update.message.reply_text(
            "You have yet to add your order! You can only delete your order after you've added it in 😬")
        user.Deleting = False
        return
    if user.Deleting:
        user.deletingCommand = True
        keyboard = [
            [
                InlineKeyboardButton("Yes", callback_data="135YesDelete"),
                InlineKeyboardButton("No", callback_data="135NoDelete"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            "Are you sure you want to delete your order from '" + backEnd.OrderLists[user.listID].Title + "' ?"
            + "\n\n" + backEnd.OrderLists[user.listID].getOrder(user_name),
            reply_markup=reply_markup)


def editCommand(update: Update, context: CallbackContext) -> None:
    userId = update.message.from_user.id
    user = backEnd.getUser(userId)
    user_name = f'{update.message.from_user.first_name}'

    if user is None or not user.Editing:
        update.message.reply_text("To use this command click Edit Order on an active Order List")
        return

    if user_name not in backEnd.OrderLists[user.listID].peopleList:
        update.message.reply_text(
            "You have yet to add your order! You can only edit your order after you've added it in 😬")
        user.Editing = False
        return

    if user.Editing:
        user.editingCommand = True
        update.message.reply_text("Your previous order was: \n" + backEnd.OrderLists[user.listID].getOrder(user_name))
        update.message.reply_text("What is your new Order?")


def copyCommand(update: Update, context: CallbackContext) -> None:
    userId = update.message.from_user.id
    user = backEnd.getUser(userId)
    user_name = f'{update.message.from_user.first_name}'
    theOrder = backEnd.OrderLists[user.listID]
    thePeople = theOrder.peopleList

    if user is None or not user.Copying:
        update.message.reply_text("To use this command click Copy Order on an active Order List")
        return

    if user_name in backEnd.OrderLists[user.listID].peopleList:
        update.message.reply_text("You have already added your order!")
        user.Copying = False
        return

    if len(thePeople) == 0:
        update.message.reply_text("The Order List is empty, there is no one to copy from!")
        return

    if user.Copying:
        peopleKey = []
        keyboard = [peopleKey]
        user.copyingCommand = True
        for x in thePeople:
            peopleKey.append(InlineKeyboardButton(x, callback_data=x))
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = "Whose order would you like to COPY? \n\n" + theOrder.fullList()
        update.message.reply_text(
            text=text,
            reply_markup=reply_markup)


# for message handler
def prompts(update: Update, context: CallbackContext):
    userId = update.message.from_user.id
    user = backEnd.getUser(userId)

    if user is None or (user.Adding == False and user.Ordering == False and user.Deleting == False
                        and user.Editing == False and user.Copying == False):
        update.message.reply_text(START_MESSAGE)
        return

    if user.addingCommand:
        return addingOrder(update, context)

    if user.editingCommand:
        return editingOrder(update, context)

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

    if query.data == "135New Order":
        return newOrder(query, context)

    if query.data == "135Check":
        return check(query, context)

    if query.data[0:12] == "135Add Order":
        update.message = query.data[12:]
        index = int(query.data[12:])
        # check if user is in backend, if not add the user in. Then add the orderList into the user
        # change users.adding to true
        userId = update.callback_query.from_user.id
        if not backEnd.isUser(userId):
            backEnd.addUser(userId)
        currentUser = backEnd.getUser(userId)
        currentUser.listID = index
        currentUser.listUpdate = update
        currentList = backEnd.OrderLists[index]
        currentList.groupChatListUpdate = update
        currentUser.Adding = True
        currentUser.memberLists[index] = currentList
        return addCommand(currentUser.personalUpdate, context)

    if query.data[0:15] == "135Delete Order":
        update.message = query.data[15:]
        index = int(query.data[15:])
        # check if user is in backend, if not add the user in. Then add the orderList into the user
        # change users.adding to true
        userId = update.callback_query.from_user.id
        if not backEnd.isUser(userId):
            backEnd.addUser(userId)
        currentUser = backEnd.getUser(userId)
        currentUser.listID = index
        currentUser.listUpdate = update
        currentList = backEnd.OrderLists[index]
        currentList.groupChatListUpdate = update
        currentUser.Deleting = True
        currentUser.memberLists[index] = currentList
        return deleteCommand(currentUser.personalUpdate, context)

    if query.data == "135NoDelete":
        query.message.reply_text("Ok we shall leave your order there!")

    if query.data == "135YesDelete":
        return deleteOrder(query, context)

    if query.data[0:13] == "135Edit Order":
        update.message = query.data[13:]
        index = int(query.data[13:])
        # check if user is in backend, if not add the user in. Then add the orderList into the user
        # change users.adding to true
        userId = update.callback_query.from_user.id
        if not backEnd.isUser(userId):
            backEnd.addUser(userId)
        currentUser = backEnd.getUser(userId)
        currentUser.listID = index
        currentUser.listUpdate = update
        currentList = backEnd.OrderLists[index]
        currentList.groupChatListUpdate = update
        currentUser.Editing = True
        currentUser.memberLists[index] = currentList
        return editCommand(currentUser.personalUpdate, context)

    if query.data[0:13] == "135Copy Order":
        update.message = query.data[13:]
        index = int(query.data[13:])
        # check if user is in backend, if not add the user in. Then add the orderList into the user
        # change users.adding to true
        userId = update.callback_query.from_user.id
        if not backEnd.isUser(userId):
            backEnd.addUser(userId)
        currentUser = backEnd.getUser(userId)
        currentUser.listID = index
        currentUser.listUpdate = update
        currentList = backEnd.OrderLists[index]
        currentList.groupChatListUpdate = update
        currentUser.Copying = True
        currentUser.memberLists[index] = currentList
        return copyCommand(currentUser.personalUpdate, context)

    if query.data[0:9] == "135Update":
        update.message = query.data[9:]
        index = int(query.data[9:])
        userId = update.callback_query.from_user.id
        currentUser = backEnd.getUser(userId)
        currentUser.listID = index
        # currentUser.listUpdate = update
        return updateList(update, context)

    if query.data[0:14] == "135Close Order":
        update.message = query.data[14:]
        index = int(query.data[14:])
        userId = update.callback_query.message.chat.id
        currentUser = backEnd.getUser(userId)
        currentUser.listID = index
        # currentUser.listUpdate = update
        return closedOrder(update, context)

    if query.data[0:13] == "135Open Order":
        update.message = query.data[13:]
        index = int(query.data[13:])
        userId = update.callback_query.message.chat.id
        currentUser = backEnd.getUser(userId)
        currentUser.listID = index
        # currentUser.listUpdate = update
        return openOrder(update, context)

    if query.data[0:7] == "135Paid":
        update.message = query.data[7:]
        index = int(query.data[7:])
        userId = update.callback_query.from_user.id
        currentUser = backEnd.getUser(userId)
        currentUser.listID = index
        return paid(update, context)


def newOrder(update: Update, context: CallbackContext) -> None:
    # instantiate a user and set the users Ordering to True
    userId = update.message.chat.id
    backEnd.addUser(userId)
    user = backEnd.getUser(userId)
    user.Ordering = True
    # instantiate a OrderList and add it to backend
    global listId
    orderingList = OrderList(listId)
    backEnd.OrderLists.append(orderingList)
    # add the orderList to the users creators list
    user.creatorLists.append(orderingList)
    listId += 1
    # add the user to backend userList if not inside alr
    update.message.reply_text('What will the title of your Order List be?')


def updateList(update: Update, context: CallbackContext) -> None:
    userId = update.callback_query.from_user.id
    user = backEnd.getUser(userId)
    index = int(user.listUpdate.message)
    order = backEnd.OrderLists[index]

    keyboard = [
        [
            InlineKeyboardButton('Publish Order List',
                                 switch_inline_query=order.Title)
        ],
        [
            InlineKeyboardButton('Update', callback_data='135Update' + str(index))
        ],
        [
            InlineKeyboardButton('Close Order', callback_data='135Close Order' + str(index)),
            InlineKeyboardButton('Open Order', callback_data='135Open Order' + str(index))
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.edit_message_text(
        text=order.fullList(),
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )


def orderList(update: Update, context: CallbackContext) -> None:
    userId = update.message.from_user.id
    currTitle = backEnd.latestList(userId).Title
    index = backEnd.getOrderIndex(currTitle)

    keyboard = [
        [
            InlineKeyboardButton('Publish Order List',
                                 switch_inline_query=currTitle)
        ],
        [
            InlineKeyboardButton('Update', callback_data='135Update' + str(index))
        ],
        [
            InlineKeyboardButton('Close Order', callback_data='135Close Order' + str(index)),
            InlineKeyboardButton('Open Order', callback_data='135Open Order' + str(index))
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
            [
                InlineKeyboardButton('Add Order', callback_data='135Add Order' + str(index)),
                InlineKeyboardButton('Edit Order', callback_data='135Edit Order' + str(index))
            ],
            [
                InlineKeyboardButton('Copy Order', callback_data='135Copy Order' + str(index)),
                InlineKeyboardButton('Delete Order', callback_data='135Delete Order' + str(index))
            ],
            [
                InlineKeyboardButton('Bot Chat', url=botURL)
            ]
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


def addingOrder(update: Update, context: CallbackContext) -> None:
    user_name = f'{update.message.from_user.first_name}'
    added_order = update.message.text
    userId = update.message.from_user.id
    user = backEnd.getUser(userId)

    backEnd.OrderLists[user.listID].peopleList.append(user_name)
    backEnd.OrderLists[user.listID].orders.append(added_order)
    backEnd.OrderLists[user.listID].unpaid[user_name] = added_order
    text = backEnd.OrderLists[int(user.listUpdate.message)].fullList()

    ORDER_BUTTONS = [
        [
            InlineKeyboardButton('Add Order', callback_data='135Add Order' + user.listUpdate.message),
            InlineKeyboardButton('Edit Order', callback_data='135Edit Order' + user.listUpdate.message)
        ],
        [
            InlineKeyboardButton('Copy Order', callback_data='135Copy Order' + user.listUpdate.message),
            InlineKeyboardButton('Delete Order', callback_data='135Delete Order' + user.listUpdate.message)
        ],
        [
            InlineKeyboardButton('Bot Chat', url=botURL)
        ]
    ]

    update.message.reply_text("Your order has been added!")
    user.listUpdate.callback_query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(ORDER_BUTTONS)
    )
    backEnd.getUser(userId).Adding = False
    backEnd.getUser(userId).addingCommand = False
    return


def editingOrder(update: Update, context: CallbackContext) -> None:
    user_name = f'{update.message.from_user.first_name}'
    userId = update.message.from_user.id  # correct userID
    currentUser = backEnd.getUser(userId)
    index = currentUser.listID
    order = backEnd.OrderLists[index]
    listIndex = order.getIndex(user_name)
    editedOrder = update.message.text

    order.peopleList.pop(listIndex)
    order.orders.pop(listIndex)
    order.unpaid.pop(user_name)
    order.peopleList.append(user_name)
    order.orders.append(editedOrder)
    order.unpaid[user_name] = editedOrder
    text = backEnd.OrderLists[int(currentUser.listUpdate.message)].fullList()

    ORDER_BUTTONS = [
        [
            InlineKeyboardButton('Add Order', callback_data='135Add Order' + currentUser.listUpdate.message),
            InlineKeyboardButton('Edit Order', callback_data='135Edit Order' + currentUser.listUpdate.message)
        ],
        [
            InlineKeyboardButton('Copy Order', callback_data='135Copy Order' + currentUser.listUpdate.message),
            InlineKeyboardButton('Delete Order', callback_data='135Delete Order' + currentUser.listUpdate.message)
        ],
        [
            InlineKeyboardButton('Bot Chat', url=botURL)
        ]
    ]

    update.message.reply_text("Your Order has been Edited!")
    currentUser.listUpdate.callback_query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(ORDER_BUTTONS)
    )
    currentUser.Editing = False
    currentUser.editingCommand = False


def deleteOrder(update: Update, context: CallbackContext) -> None:
    user_name = f'{update.from_user.first_name}'
    userId = update.from_user.id  # correct userID
    currentUser = backEnd.getUser(userId)
    index = currentUser.listID
    order = backEnd.OrderLists[index]
    listIndex = order.getIndex(user_name)

    order.peopleList.pop(listIndex)
    order.orders.pop(listIndex)
    order.unpaid.pop(user_name)
    text = order.fullList()

    ORDER_BUTTONS = [
        [
            InlineKeyboardButton('Add Order', callback_data='135Add Order' + currentUser.listUpdate.message),
            InlineKeyboardButton('Edit Order', callback_data='135Edit Order' + currentUser.listUpdate.message)
        ],
        [
            InlineKeyboardButton('Copy Order', callback_data='135Copy Order' + currentUser.listUpdate.message),
            InlineKeyboardButton('Delete Order', callback_data='135Delete Order' + currentUser.listUpdate.message)
        ],
        [
            InlineKeyboardButton('Bot Chat', url=botURL)
        ]
    ]

    update.message.reply_text("Your Order has been deleted!")
    currentUser.listUpdate.callback_query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(ORDER_BUTTONS)
    )
    currentUser.Deleting = False
    currentUser.deletingCommand = False


def copyOrder(name, update: Update, context: CallbackContext) -> None:
    user_name = f'{update.from_user.first_name}'
    userId = update.from_user.id
    currentUser = backEnd.getUser(userId)
    index = currentUser.listID
    ordList = backEnd.OrderLists[index]
    order = ordList.getOnlyOrder(name)

    ordList.peopleList.append(user_name)
    ordList.orders.append(order)
    ordList.unpaid[user_name] = order
    text = backEnd.OrderLists[int(currentUser.listUpdate.message)].fullList()

    ORDER_BUTTONS = [
        [
            InlineKeyboardButton('Add Order', callback_data='135Add Order' + currentUser.listUpdate.message),
            InlineKeyboardButton('Edit Order', callback_data='135Edit Order' + currentUser.listUpdate.message)
        ],
        [
            InlineKeyboardButton('Copy Order', callback_data='135Copy Order' + currentUser.listUpdate.message),
            InlineKeyboardButton('Delete Order', callback_data='135Delete Order' + currentUser.listUpdate.message)
        ],
        [
            InlineKeyboardButton('Bot Chat', url=botURL)
        ]
    ]

    update.message.reply_text(text)
    currentUser.listUpdate.callback_query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(ORDER_BUTTONS)
    )
    backEnd.getUser(userId).Copying = False
    backEnd.getUser(userId).copyingCommand = False


def closedOrder(update: Update, context: CallbackContext) -> None:
    userId = update.callback_query.message.chat.id  # correct userID
    user = backEnd.getUser(userId)
    orderIndex = int(update.message)
    currentOrder = backEnd.OrderLists[orderIndex]
    currentListUpdate = currentOrder.groupChatListUpdate
    text = backEnd.OrderLists[orderIndex].paymentList()
    #index = user.listID
    title = backEnd.OrderLists[orderIndex].Title

    BUTTONS = [
        [
            InlineKeyboardButton('Paid', callback_data='135Paid' + str(orderIndex)),
        ]
    ]
    update.callback_query.message.reply_text("Order List " + "'" + title + "'" + " is now closed")
    currentListUpdate.callback_query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(BUTTONS)
    )

def openOrder(update: Update, context: CallbackContext) -> None:
    userId = update.callback_query.message.chat.id  # correct userID
    currentUser = backEnd.getUser(userId)
    orderIndex = int(update.message)
    currentOrder = backEnd.OrderLists[orderIndex]
    currentListUpdate = currentOrder.groupChatListUpdate
    text = backEnd.OrderLists[orderIndex].fullList()
    title = backEnd.OrderLists[orderIndex].Title

    BUTTONS = [
        [
            InlineKeyboardButton('Add Order', callback_data='135Add Order' + currentUser.listUpdate.message),
            InlineKeyboardButton('Edit Order', callback_data='135Edit Order' + currentUser.listUpdate.message)
        ],
        [
            InlineKeyboardButton('Copy Order', callback_data='135Copy Order' + currentUser.listUpdate.message),
            InlineKeyboardButton('Delete Order', callback_data='135Delete Order' + currentUser.listUpdate.message)
        ],
        [
            InlineKeyboardButton('Bot Chat', url=botURL)
        ]
    ]

    update.callback_query.message.reply_text("Order List " + "'" + title + "'" + "is now opened")
    currentListUpdate.callback_query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(BUTTONS)
    )


def paid(update: Update, context: CallbackContext) -> None:
    user_name = f'{update.callback_query.from_user.first_name}'
    userId = update.callback_query.from_user.id  # correct userID
    currentUser = backEnd.getUser(userId)
    index = currentUser.listID
    order = backEnd.OrderLists[index]
    currentListUpdate = order.groupChatListUpdate

    order.unpaid.pop(user_name)
    text = order.paymentList()

    BUTTONS = [
        [
            InlineKeyboardButton('Paid', callback_data='135Paid' + str(index)),
        ]
    ]
    currentListUpdate.callback_query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(BUTTONS)
    )

def check(update: Update, context: CallbackContext) -> None:
    print(update)
    userId = update.from_user.id
    user_name = f'{update.from_user.first_name}'
    print(user_name)
    currentUser = backEnd.getUser(userId)
    index = currentUser.listID
    order = backEnd.OrderLists[index]
    BUTTONS = [
        [
            InlineKeyboardButton('Update', callback_data='135CheckUpdate' + str(index)),
        ]
    ]

    text = "Who owes you money 😤💵\n\n" + currentUser.outstandingOrders() + \
           "\nPeople you owe money to 🥺💵\n\n" + currentUser.outstandingPayments(user_name)
    update.message.reply_text(
        text=text,
        reply_markup = InlineKeyboardMarkup(BUTTONS)
    )

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
    dispatcher.add_handler(CommandHandler("delete", deleteCommand))
    dispatcher.add_handler(CommandHandler("edit", editCommand))
    dispatcher.add_handler(CommandHandler("copy", copyCommand))
    dispatcher.add_handler(CallbackQueryHandler(response))

    dispatcher.add_error_handler(error)
    dispatcher.add_handler(MessageHandler(Filters.text, prompts))
    # dispatcher.add_handler(MessageHandler(Filters.text, phoneNumber))
    dispatcher.add_handler(InlineQueryHandler(inlineOrderList))
    updater.start_polling()
    updater.idle()


main()
