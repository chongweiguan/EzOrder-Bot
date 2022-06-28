from telegram import *
from telegram.ext import *
from OrderList import OrderList
from SplitList import SplitList
from backEnd import backEnd
from user import User
from datetime import datetime
import json
from Secrets import API_Token, BotURL

updater = Updater(API_Token)
dispatcher = updater.dispatcher
START_MESSAGE = 'This bot will help you create an order list, check your outstanding payments, or split money! use /start to begin!'
botURL = BotURL
backEnd = backEnd()
listId = 0
splitListId = 0
backEndId = 0


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


def startCommand(update: Update, context: CallbackContext) -> None:
    userId = update.message.from_user.id
    if not backEnd.isUser(userId):
        backEnd.addUser(userId)
    user = backEnd.getUser(userId)
    user.personalUpdate = update
    update.message.reply_text("The bot is now activated, you no longer have to activate it again!")


def createCommand(update: Update, context: CallbackContext) -> None:
    userId = update.message.from_user.id
    if not backEnd.isUser(userId):
        backEnd.addUser(userId)
    user = backEnd.getUser(userId)
    user.personalUpdate = update
    keyboard = [
        [
            InlineKeyboardButton("New Order", callback_data="135New Order"),
            InlineKeyboardButton("Check", callback_data="135Check"),
            InlineKeyboardButton("Split", callback_data="135SplitOrder")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Hi! I am EzOrder Bot, I am here to make your life a little bit"
                              "easier Here are some commands to interact with me!",
                              reply_markup=reply_markup)


def addCommand(update: Update, context: CallbackContext) -> None:
    userId = update.message.from_user.id
    user = backEnd.getUser(userId)
    user_name = f'{update.message.from_user.username}'

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
    user_name = f'{update.message.from_user.username}'

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
    user_name = f'{update.message.from_user.username}'

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
    user_name = f'{update.message.from_user.username}'
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
                        and user.Editing == False and user.Copying == False and user.Splitting == False):
        update.message.reply_text(START_MESSAGE)
        return

    if user.addingCommand:
        return addingOrder(update, context)

    if user.editingCommand:
        return editingOrder(update, context)

    if user.Ordering:
        if backEnd.latestList(userId).phoneNum == "" and \
                backEnd.latestList(userId).Title == "":
            backEnd.latestList(userId).Title = update.message.text
            user.titleList.append(update.message.text)
            update.message.reply_text('What is your phone number?' +
                                      ' (Send 1 if you do not want to display your phone number)')
            return

        if backEnd.latestList(userId).phoneNum == "":
            if update.message.text.isnumeric() and len(update.message.text) == 8:
                backEnd.latestList(userId).phoneNum = update.message.text
                backEnd.getUser(userId).Ordering = False
                return orderList(update, context)
            elif update.message.text == "1":
                backEnd.latestList(userId).phoneNum = update.message.from_user.username
                backEnd.getUser(userId).Ordering = False
                return orderList(update, context)
            else:
                update.message.reply_text('Invalid Input: Please make sure that you have sent a 8 digit phone number'
                                          + ' or 1')

    if user.Splitting:
        if backEnd.latestList(userId).phoneNum == "" and \
                backEnd.latestList(userId).Title == "":
            backEnd.latestList(userId).Title = update.message.text
            user.titleList.append(update.message.text)
            update.message.reply_text('What is your phone number? ')
            return
        elif backEnd.latestList(userId).phoneNum == "":
            if update.message.text.isnumeric() and len(update.message.text) == 8:
                backEnd.latestList(userId).phoneNum = update.message.text
                update.message.reply_text("Please send me your first item")
                backEnd.latestList(userId).addPrice = True
                return
            elif update.message.text == "1":
                backEnd.latestList(userId).phoneNum = update.message.from_user.username
                update.message.reply_text("Please send me your first item")
                backEnd.latestList(userId).addPrice = True
                return
            else:
                update.message.reply_text('Invalid Input: Please make sure that you have sent a 8 digit phone number'
                                          + ' or 1')
        elif update.message.text != "/done" and backEnd.latestList(userId).addPrice == True:
            backEnd.latestList(userId).addItem(update.message.text)
            update.message.reply_text("What is the price of this item?")
            backEnd.latestList(userId).addPrice = False
            return
        elif update.message.text != "/done" and backEnd.latestList(userId).addPrice == False:
            if isfloat(update.message.text):
                backEnd.latestList(userId).getLatestItem()[0] = update.message.text
                update.message.reply_text("Good. now send me another item, or /done to finish.")
                backEnd.latestList(userId).addPrice = True
            else:
                update.message.reply_text("Price has to be a number")
                return
        elif update.message.text == "/done":
            backEnd.latestList(userId).addPrice = False
            return splitList(update, context)


def response(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    query.answer()

    if query.data == "135New Order":
        userId = update.callback_query.from_user.id
        user = backEnd.getUser(userId)
        if user.splitting == True:
            query.message.reply_text("You're in the middle of creating a Split List, " +
                                     "finish that before creating another list")
        else:
            return newOrder(query, context)

    if query.data == "135Check":
        return check(query, context)

    if query.data == "135SplitOrder":
        userId = update.callback_query.from_user.id
        user = backEnd.getUser(userId)
        if user.Ordering == True:
            query.message.reply_text("You're in the middle of creating an Order List, " +
                                     "finish that before creating another list")
        else:
            return split(query, context)

    if query.data[0:12] == "135Add Order":
        userId = update.callback_query.from_user.id
        if backEnd.getUser(userId) is None:
            return
        else:
            update.message = query.data[12:]
            index = int(query.data[12:])
            # check if user is in backend, if not add the user in. Then add the orderList into the user
            # change users.adding to true
            if not backEnd.isUser(userId):
                backEnd.addUser(userId)
            currentUser = backEnd.getUser(userId)
            currentUser.listID = index
            currentUser.listUpdate = update
            currentList = backEnd.OrderLists[index]
            currentList.groupChatListUpdate = update
            backendId = currentList.backEndId
            currentUser.Adding = True
            currentUser.memberLists[backendId] = currentList
            return addCommand(currentUser.personalUpdate, context)

    if query.data[0:15] == "135Delete Order":
        userId = update.callback_query.from_user.id
        if backEnd.getUser(userId) is None:
            return
        else:
            update.message = query.data[15:]
            index = int(query.data[15:])
            # check if user is in backend, if not add the user in. Then add the orderList into the user
            # change users.adding to true
            if not backEnd.isUser(userId):
                backEnd.addUser(userId)
            currentUser = backEnd.getUser(userId)
            currentUser.listID = index
            currentUser.listUpdate = update
            currentList = backEnd.OrderLists[index]
            currentList.groupChatListUpdate = update
            backendId = currentList.backEndId
            currentUser.Deleting = True
            currentUser.memberLists[backendId] = currentList
            return deleteCommand(currentUser.personalUpdate, context)

    if query.data == "135NoDelete":
        query.message.reply_text("Ok we shall leave your order there!")

    if query.data == "135YesDelete":
        return deleteOrder(query, context)

    if query.data[0:13] == "135Edit Order":
        userId = update.callback_query.from_user.id
        if backEnd.getUser(userId) is None:
            return
        else:
            update.message = query.data[13:]
            index = int(query.data[13:])
            # check if user is in backend, if not add the user in. Then add the orderList into the user
            # change users.adding to true
            if not backEnd.isUser(userId):
                backEnd.addUser(userId)
            currentUser = backEnd.getUser(userId)
            currentUser.listID = index
            currentUser.listUpdate = update
            currentList = backEnd.OrderLists[index]
            currentList.groupChatListUpdate = update
            currentUser.Editing = True
            backendId = currentList.backEndId
            currentUser.memberLists[backendId] = currentList
            return editCommand(currentUser.personalUpdate, context)

    if query.data[0:13] == "135Copy Order":
        userId = update.callback_query.from_user.id
        if backEnd.getUser(userId) is None:
            return
        else:
            update.message = query.data[13:]
            index = int(query.data[13:])
            # check if user is in backend, if not add the user in. Then add the orderList into the user
            # change users.adding to true
            if not backEnd.isUser(userId):
                backEnd.addUser(userId)
            currentUser = backEnd.getUser(userId)
            currentUser.listID = index
            currentUser.listUpdate = update
            currentList = backEnd.OrderLists[index]
            currentList.groupChatListUpdate = update
            currentUser.Copying = True
            backendId = currentList.backEndId
            currentUser.memberLists[backendId] = currentList
            return copyCommand(currentUser.personalUpdate, context)

    if query.data[0:9] == "135Update":
        update.message = query.data[9:]
        index = int(query.data[9:])
        order = backEnd.OrderLists[index]
        userId = update.callback_query.from_user.id
        currentUser = backEnd.getUser(userId)
        currentUser.listID = index
        currentUser.listUpdate = update
        if not order.canUpdate:
            return
        else:
            return updateList(update, context)

    if query.data[0:14] == "135Close Order":
        update.message = query.data[14:]
        index = int(query.data[14:])
        order = backEnd.OrderLists[index]
        length = len(order.peopleList)
        if length == 0:
            query.message.reply_text("Cannot close an empty Order List")
        elif not order.orderStatus:
            query.message.reply_text("Order List is already Closed")
        else:
            order.orderStatus = False
            userId = update.callback_query.message.chat.id
            currentUser = backEnd.getUser(userId)
            currentUser.listID = index
            # currentUser.listUpdate = update
            return closedOrder(update, context)

    if query.data[0:17] == "135SplitCloseList":
        update.message = query.data[17:]
        index = int(query.data[17:])
        splitOrder = backEnd.SplitLists[index]

        if splitOrder.isEmpty():
            query.message.reply_text("Cannot close an empty Order List")
        elif not splitOrder.orderStatus:
            query.message.reply_text("Order List is already Closed")
        # currentUser.listUpdate = update
        else:
            splitOrder.orderStatus = False
            userId = update.callback_query.message.chat.id
            currentUser = backEnd.getUser(userId)
            currentUser.listID = index
            return closedSplitList(update, context)

    if query.data[0:13] == "135Open Order":
        update.message = query.data[13:]
        index = int(query.data[13:])
        order = backEnd.OrderLists[index]
        if order.orderStatus:
            query.message.reply_text("Order List is already Opened")
        else:
            order.orderStatus = True
            userId = update.callback_query.message.chat.id
            currentUser = backEnd.getUser(userId)
            currentUser.listID = index
            # currentUser.listUpdate = update
            return openOrder(update, context)

    if query.data[0:16] == '135SplitOpenList':
        update.message = query.data[16:]
        index = int(query.data[16:])
        splitOrder = backEnd.SplitLists[index]
        if splitOrder.orderStatus:
            query.message.reply_text("Order List is already Opened")
        # currentUser.listUpdate = update
        else:
            splitOrder.orderStatus = True
            userId = update.callback_query.message.chat.id
            currentUser = backEnd.getUser(userId)
            currentUser.listID = index
            return openSplitList(update, context)

    if query.data[0:7] == "135Paid":
        userId = update.callback_query.from_user.id
        if backEnd.getUser(userId) is None:
            return
        else:
            update.message = query.data[7:]
            index = int(query.data[7:])
            username = update.callback_query.from_user.username
            currentUser = backEnd.getUser(userId)
            currentUser.listID = index
            order = backEnd.OrderLists[index]
            if order.getOrder(username) == "no such order":
                return
            elif order.ownerName == username:
                return
            elif order.paidStatus(username):
                return paid(update, context)
            else:
                return unpay(update, context)

    # if query.data[0:9] == "135Remind":
    #     update.message = query.data[9:]
    #     index = int(query.data[9:])
    #     order = backEnd.OrderLists[index]
    #     userId = update.callback_query.message.chat.id
    #     currentUser = backEnd.getUser(userId)
    #     currentUser.listID = index
    #     return reminder(update, context)

    if query.data[0:13] == "135Contribute":
        item = ''
        indexString = ''
        for i in range(len(query.data)):
            if ord(query.data[13 + i]) >= 48 and ord(query.data[13 + i]) <= 57:
                indexString = indexString + query.data[13 + i]
            else:
                item = item + query.data[14 + i:]
                break
        index = int(indexString)
        userId = update.callback_query.from_user.id
        currentUser = backEnd.getUser(userId)
        if currentUser == None:
            backEnd.addUser(userId)
        currentUser = backEnd.getUser(userId)
        # currentUser.listID = index
        currentList = backEnd.SplitLists[index]
        backendId = currentList.backEndId
        currentUser.memberLists[backendId] = currentList
        currentList.groupChatUpdate = update

        return contribute(update, context, item, index)

    if query.data[0:14] == "135SplitUpdate":
        update.message = query.data[14:]
        index = int(query.data[14:])
        splitOrder = backEnd.SplitLists[index]
        if not splitOrder.canUpdate:
            return
        else:
            print("update")
            userId = update.callback_query.from_user.id
            currentUser = backEnd.getUser(userId)
            currentUser.listID = index
            # currentUser.listUpdate = update
            return updateSplitList(update, context)

    if query.data[0:12] == "135SplitPaid":
        item = ''
        indexString = ''
        for i in range(len(query.data)):
            if ord(query.data[12 + i]) >= 48 and ord(query.data[12 + i]) <= 57:
                indexString = indexString + query.data[12 + i]
            else:
                item = item + query.data[13 + i:]
                break
        index = int(indexString)
        # userId = update.callback_query.from_user.id
        # currentUser = backEnd.getUser(userId)
        # currentUser.listID = index
        currentList = backEnd.SplitLists[index]
        currentList.groupChatUpdate = update
        return splitPaid(update, context, item, index)

    if not query.data[0:3] == "135":
        userId = update.callback_query.message.chat.id
        user = backEnd.getUser(userId)
        index = user.listID
        order = backEnd.OrderLists[index]
        orderPeople = order.peopleList
        if user.Copying and user.copyingCommand:
            for x in orderPeople:
                if query.data == x:
                    copyOrder(x, query, context)


def newOrder(update: Update, context: CallbackContext) -> None:
    # instantiate a user and set the users Ordering to True
    userId = update.message.chat.id
    backEnd.addUser(userId)
    user = backEnd.getUser(userId)
    user.Ordering = True
    # instantiate a OrderList and add it to backend
    global listId
    global backEndId
    now = datetime.now()
    stringNow = json.dumps(now, default=str)
    orderingList = OrderList(listId, stringNow, backEndId)
    orderingList.ownerName = update.from_user.username
    backEnd.OrderLists.append(orderingList)
    # add the orderList to the users creators list
    user.creatorLists.append(orderingList)
    listId += 1
    backEndId += 1
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
    index = backEnd.latestList(userId).listId
    user = backEnd.getUser(userId)
    user.Ordering = False

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

    for x in range(len(user.creatorLists)):
        order = user.creatorLists[x]
        index = order.listId
        title = order.Title
        backIndex = order.backEndId
        if backEnd.listType(backIndex) == "order":
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
                    id=backIndex,
                    title=title,
                    description=order.timing,
                    input_message_content=InputTextMessageContent(backEnd.OrderLists[index].fullList()),
                    reply_markup=InlineKeyboardMarkup(ORDER_BUTTONS),
                    thumb_url="https://i.ibb.co/60fTBV9/ezorder-logo.jpg",
                )
            )
        else:
            currSplitList = backEnd.SplitLists[index]
            items = currSplitList.itemArray()
            itemsKey = []
            buttons = [itemsKey]
            for x in items:
                itemsKey.append(InlineKeyboardButton(x, callback_data="135Contribute" + str(index) + "/" + x))
            reply_markup = InlineKeyboardMarkup(buttons)
            results.append(
                InlineQueryResultArticle(
                    id=backIndex,
                    title=title,
                    description=currSplitList.timing,
                    input_message_content=InputTextMessageContent(backEnd.SplitLists[index].contributorsList()),
                    reply_markup=reply_markup,
                    thumb_url="https://i.ibb.co/60fTBV9/ezorder-logo.jpg"
                )
            )
    update.inline_query.answer(results)


def addingOrder(update: Update, context: CallbackContext) -> None:
    user_name = f'{update.message.from_user.username}'
    added_order = update.message.text
    userId = update.message.from_user.id
    user = backEnd.getUser(userId)
    order = backEnd.OrderLists[user.listID]
    order.canUpdate = True

    order.peopleList.append(user_name)
    order.orders.append(added_order)
    if user_name != order.ownerName:
        order.unpaid[user_name] = added_order
    text = backEnd.OrderLists[int(user.listUpdate.message)].fullList()
    order.addNewUpdate(user.listUpdate.callback_query)

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
    for value in order.updateList.values():
        value.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(ORDER_BUTTONS)
        )
    backEnd.getUser(userId).Adding = False
    backEnd.getUser(userId).addingCommand = False
    return


def editingOrder(update: Update, context: CallbackContext) -> None:
    user_name = f'{update.message.from_user.username}'
    userId = update.message.from_user.id  # correct userID
    currentUser = backEnd.getUser(userId)
    index = currentUser.listID
    order = backEnd.OrderLists[index]
    listIndex = order.getIndex(user_name)
    editedOrder = update.message.text

    order.peopleList.pop(listIndex)
    order.orders.pop(listIndex)
    if user_name != order.ownerName:
        order.unpaid.pop(user_name)
    order.peopleList.append(user_name)
    order.orders.append(editedOrder)
    if user_name != order.ownerName:
        order.unpaid[user_name] = editedOrder
    text = backEnd.OrderLists[int(currentUser.listUpdate.message)].fullList()
    order.addNewUpdate(currentUser.listUpdate.callback_query)

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
    for value in order.updateList.values():
        value.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(ORDER_BUTTONS)
        )
    currentUser.Editing = False
    currentUser.editingCommand = False


def deleteOrder(update: Update, context: CallbackContext) -> None:
    user_name = f'{update.from_user.username}'
    userId = update.from_user.id  # correct userID
    currentUser = backEnd.getUser(userId)
    index = currentUser.listID
    order = backEnd.OrderLists[index]
    listIndex = order.getIndex(user_name)

    order.peopleList.pop(listIndex)
    order.orders.pop(listIndex)
    if user_name != order.ownerName:
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
    for value in order.updateList.values():
        value.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(ORDER_BUTTONS)
        )
    currentUser.Deleting = False
    currentUser.deletingCommand = False


def copyOrder(name, update: Update, context: CallbackContext) -> None:
    user_name = f'{update.from_user.username}'
    userId = update.from_user.id
    currentUser = backEnd.getUser(userId)
    index = currentUser.listID
    ordList = backEnd.OrderLists[index]
    order = ordList.getOnlyOrder(name)
    orderObject = backEnd.OrderLists[index]

    ordList.peopleList.append(user_name)
    ordList.orders.append(order)
    if user_name != ordList.ownerName:
        ordList.unpaid[user_name] = order
    text = backEnd.OrderLists[int(currentUser.listUpdate.message)].fullList()
    orderObject.addNewUpdate(currentUser.listUpdate.callback_query)

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
    update.message.reply_text("You have copied " + name + " order!")
    for value in orderObject.updateList.values():
        value.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(ORDER_BUTTONS)
        )
    backEnd.getUser(userId).Copying = False
    backEnd.getUser(userId).copyingCommand = False


def closedOrder(update: Update, context: CallbackContext) -> None:
    orderIndex = int(update.message)
    currentOrder = backEnd.OrderLists[orderIndex]
    userId = update.callback_query.message.chat.id  # correct userID
    user = backEnd.getUser(userId)
    currentListUpdate = currentOrder.groupChatListUpdate
    text = backEnd.OrderLists[orderIndex].paymentList()
    # index = user.listID
    title = backEnd.OrderLists[orderIndex].Title

    BUTTONS = [
        [
            InlineKeyboardButton('Paid', callback_data='135Paid' + str(orderIndex)),
        ]
    ]
    update.callback_query.message.reply_text("Order List " + "'" + title + "'" + " is now closed")
    for value in currentOrder.updateList.values():
        value.edit_message_text(
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

    update.callback_query.message.reply_text("Order List " + "'" + title + "'" + " is now opened")
    for value in currentOrder.updateList.values():
        value.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(BUTTONS)
        )


def reminder(update: Update, context: CallbackContext) -> None:
    orderIndex = int(update.message)
    currentOrder = backEnd.OrderLists[orderIndex]
    currentListUpdate = currentOrder.groupChatListUpdate
    currentListUpdate.callback_query.id
    return


def paid(update: Update, context: CallbackContext) -> None:
    user_name = f'{update.callback_query.from_user.username}'
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
    for value in order.updateList.values():
        value.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(BUTTONS)
        )


def unpay(update: Update, context: CallbackContext) -> None:
    user_name = f'{update.callback_query.from_user.username}'
    userId = update.callback_query.from_user.id  # correct userID
    currentUser = backEnd.getUser(userId)
    index = currentUser.listID
    order = backEnd.OrderLists[index]
    currentListUpdate = order.groupChatListUpdate
    userOrder = order.getOnlyOrder(user_name)

    order.unpaid[user_name] = userOrder
    text = order.paymentList()

    BUTTONS = [
        [
            InlineKeyboardButton('Paid', callback_data='135Paid' + str(index)),
        ]
    ]
    for value in order.updateList.values():
        value.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(BUTTONS)
        )


def check(update: Update, context: CallbackContext) -> None:
    userId = update.from_user.id
    user_name = f'{update.from_user.username}'
    currentUser = backEnd.getUser(userId)
    index = currentUser.listID
    BUTTONS = [
        [
            InlineKeyboardButton('Update', callback_data='135CheckUpdate' + str(index)),
        ]
    ]

    text = "Who owes you money 😤💵\n\n" + currentUser.outstandingOrders() + \
           "\nPeople you owe money to 🥺💵\n\n" + currentUser.outstandingPayments(user_name)
    update.message.reply_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(BUTTONS)
    )


def split(update: Update, context: CallbackContext) -> None:
    userId = update.message.chat.id
    backEnd.addUser(userId)
    user = backEnd.getUser(userId)
    user.Splitting = True
    global splitListId
    global backEndId
    now = datetime.now()
    stringNow = json.dumps(now, default=str)
    splitList = SplitList(splitListId, stringNow, backEndId)
    splitList.ownerName = update.from_user.username
    backEnd.SplitLists.append(splitList)
    user.creatorLists.append(splitList)
    splitListId += 1
    backEndId += 1
    update.message.reply_text("What will be the title of your Split List be?")


def splitList(update: Update, context: CallbackContext) -> None:
    userId = update.message.from_user.id
    currTitle = backEnd.latestList(userId).Title
    index = backEnd.latestList(userId).listId
    user = backEnd.getUser(userId)
    user.Splitting = False

    keyboard = [
        [
            InlineKeyboardButton('Publish Split List',
                                 switch_inline_query=currTitle)
        ],
        [
            InlineKeyboardButton('Update', callback_data='135SplitUpdate' + str(index))
        ],
        [
            InlineKeyboardButton('Close List', callback_data='135SplitCloseList' + str(index)),
            InlineKeyboardButton('Open List', callback_data='135SplitOpenList' + str(index))
        ]
    ]
    text = backEnd.latestList(userId).contributorsList()
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        text=text,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )


def contribute(update: Update, context: CallbackContext, item, index) -> None:
    user_name = f'{update.callback_query.from_user.username}'
    userId = update.callback_query.from_user.id  # correct userID
    # currentUser = backEnd.getUser(userId)
    # index = currentUser.listID
    List = backEnd.SplitLists[index]
    contributorsArray = List.items[item][1]
    unpaidArray = List.items[item][2]
    List.canUpdate = True
    if user_name not in contributorsArray:
        contributorsArray.append(user_name)
    else:
        contributorsArray.remove(user_name)

    print("")
    if List.ownerName != user_name:
        if user_name not in unpaidArray:
            unpaidArray.append(user_name)
        else:
            unpaidArray.remove(user_name)

    items = List.itemArray()
    itemsKey = []
    buttons = [itemsKey]
    for x in items:
        itemsKey.append(InlineKeyboardButton(x, callback_data="135Contribute" + str(index) + "/" + x))
    reply_markup = InlineKeyboardMarkup(buttons)
    text = backEnd.SplitLists[index].contributorsList()
    update.callback_query.edit_message_text(
        text=text,
        reply_markup=reply_markup
    )


def updateSplitList(update: Update, context: CallbackContext) -> None:
    userId = update.callback_query.from_user.id
    user = backEnd.getUser(userId)
    index = int(user.listID)
    list = backEnd.SplitLists[index]

    keyboard = [
        [
            InlineKeyboardButton('Publish Split List',
                                 switch_inline_query=list.Title)
        ],
        [
            InlineKeyboardButton('Update', callback_data='135SplitUpdate' + str(index))
        ],
        [
            InlineKeyboardButton('Close List', callback_data='135SplitCloseList' + str(index)),
            InlineKeyboardButton('Open List', callback_data='135SplitOpenList' + str(index))
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.edit_message_text(
        text=list.contributorsList(),
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )


def closedSplitList(update: Update, context: CallbackContext) -> None:
    userId = update.callback_query.message.chat.id  # correct userID
    user = backEnd.getUser(userId)
    splitIndex = int(update.message)
    currList = backEnd.SplitLists[splitIndex]
    currentListUpdate = currList.groupChatUpdate
    text = currList.unpaidList()
    title = currList.Title
    items = currList.itemArray()
    itemsKey = []
    buttons = [itemsKey]
    for x in items:
        itemsKey.append(InlineKeyboardButton("Paid for " + x, callback_data="135SplitPaid" + str(splitIndex) + "/" + x))
    reply_markup = InlineKeyboardMarkup(buttons)
    update.callback_query.message.reply_text("Split List " + "'" + title + "'" + " is now closed")
    currentListUpdate.callback_query.edit_message_text(
        text=text,
        reply_markup=reply_markup
    )


def openSplitList(update: Update, context: CallbackContext) -> None:
    userId = update.callback_query.message.chat.id  # correct userID
    currentUser = backEnd.getUser(userId)
    splitIndex = int(update.message)
    currentList = backEnd.SplitLists[splitIndex]
    currentListUpdate = currentList.groupChatUpdate
    text = currentList.contributorsList()
    title = currentList.Title
    items = currentList.itemArray()
    itemsKey = []
    buttons = [itemsKey]
    for x in items:
        itemsKey.append(InlineKeyboardButton(x, callback_data="135Contribute" + str(splitIndex) + "/" + x))
    reply_markup = InlineKeyboardMarkup(buttons)
    update.callback_query.message.reply_text("Split List " + "'" + title + "'" + "is now opened")
    currentListUpdate.callback_query.edit_message_text(
        text=text,
        reply_markup=reply_markup
    )


def splitPaid(update: Update, context: CallbackContext, item, index) -> None:
    user_name = f'{update.callback_query.from_user.username}'
    userId = update.callback_query.from_user.id  # correct userID
    # currentUser = backEnd.getUser(userId)
    # index = currentUser.listID
    List = backEnd.SplitLists[index]
    currentListUpdate = List.groupChatUpdate
    currItem = List.items[item]
    unpaidList = currItem[2]

    unpaidList.remove(user_name)
    text = List.unpaidList()
    title = List.Title
    items = List.itemArray()
    itemsKey = []
    buttons = [itemsKey]
    for x in items:
        itemsKey.append(InlineKeyboardButton("Paid for " + x, callback_data="135SplitPaid" + str(index) + "/" + x))
    reply_markup = InlineKeyboardMarkup(buttons)

    currentListUpdate.callback_query.edit_message_text(
        text=text,
        reply_markup=reply_markup
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
    dispatcher.add_handler(CommandHandler("create", createCommand))
    dispatcher.add_handler(CommandHandler("cancel", cancel))
    dispatcher.add_handler(CommandHandler("add", addCommand))
    dispatcher.add_handler(CommandHandler("delete", deleteCommand))
    dispatcher.add_handler(CommandHandler("edit", editCommand))
    dispatcher.add_handler(CommandHandler("copy", copyCommand))
    dispatcher.add_handler(CallbackQueryHandler(response))

    # dispatcher.add_error_handler(error)
    dispatcher.add_handler(MessageHandler(Filters.text, prompts))
    # dispatcher.add_handler(MessageHandler(Filters.text, phoneNumber))
    dispatcher.add_handler(InlineQueryHandler(inlineOrderList))
    updater.start_polling()
    updater.idle()


main()
