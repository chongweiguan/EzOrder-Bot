from telegram import *
from telegram.ext import *
from OrderList import OrderList
from SplitList import SplitList
from backEnd import backEnd
from Order import Order
from user import User
from datetime import datetime
import json

# from Secrets import API_Token, Bot_URL

updater = Updater('5374066926:AAE7IMAU8bjduSafS1DAzjk6Kpz6X9zIHQ0')
dispatcher = updater.dispatcher
START_MESSAGE = 'This bot will help you create an order list, check your outstanding payments, or split money! use /start to begin!'
botURL = 'https://t.me/ezordertest_bot'
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

    if user.Copying or user.Editing or user.Deleting or user.Adding:
        status = user.orderStatus()
        update.message.reply_text("You are currently " + status +
                                  " an order, complete that process first or type /cancel to terminate the process")
    else:
        user.Adding = True
        update.message.reply_text("Adding Order for: " + backEnd.OrderLists[user.listID].Title)
        update.message.reply_text("What is your Order?")


def deleteCommand(update: Update, context: CallbackContext, list) -> None:
    userId = update.message.from_user.id
    user = backEnd.getUser(userId)
    user_name = f'{update.message.from_user.username}'
    orderArray = list.orderSummary[user_name]

    if user_name not in list.peopleList:
        update.message.reply_text(
            "You have yet to add your order! You can only delete your order after you've added it in 😬")
        return

    elif user.Copying or user.Editing or user.Deleting or user.Adding:
        status = user.orderStatus()
        update.message.reply_text("You are currently " + status +
                                  " an order, complete that process first or type /cancel to terminate the process")
        return

    else:
        user.Deleting = True
        delOrd = []
        keyboard = [delOrd]
        for x in orderArray:
            orderId = "Order " + str(x.orderId)
            delOrd.append(InlineKeyboardButton(orderId, callback_data="delete" + str(x.orderId)))
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            "Which of your orders would you like to delete?"
            + "\n\n" + list.indivOrders(user_name),
            reply_markup=reply_markup)


def editCommand(update: Update, context: CallbackContext, list) -> None:
    userId = update.message.from_user.id
    user = backEnd.getUser(userId)
    user_name = f'{update.message.from_user.username}'

    if user_name not in list.peopleList:
        update.message.reply_text(
            "You have yet to add your order! You can only edit your order after you've added it in 😬")
        return


    elif user.Copying or user.Editing or user.Deleting or user.Adding:
        status = user.orderStatus()
        update.message.reply_text("You are currently " + status +
                                  " an order, complete that process first or type /cancel to terminate the process")
        return

    else:
        orderArray = list.orderSummary[user_name]
        user.Editing = True
        editOrd = []
        keyboard = [editOrd]
        for x in orderArray:
            orderId = "Order " + str(x.orderId)
            editOrd.append(InlineKeyboardButton(orderId, callback_data="edit" + str(x.orderId)))
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            "Which of your orders would you like to edit?"
            + "\n\n" + list.indivOrders(user_name),
            reply_markup=reply_markup)


def copyCommand(update: Update, context: CallbackContext, list) -> None:
    userId = update.message.from_user.id
    user = backEnd.getUser(userId)
    user_name = f'{update.message.from_user.username}'

    if len(list.peopleList) == 0:
        update.message.reply_text("The Order List is empty, there is no one to copy from!")
        return

    elif user.Copying or user.Editing or user.Deleting or user.Adding:
        status = user.orderStatus()
        update.message.reply_text("You are currently " + status +
                                  " an order, complete that process first or type /cancel to terminate the process")
        return

    else:
        user.Copying = True
        peopleKey = []
        keyboard = [peopleKey]
        for x in range(len(list.orders)):
            orderId = list.orders[x].orderId
            peopleKey.append(InlineKeyboardButton(str(x + 1) + ") ", callback_data="copy" + str(orderId + 1)))
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = "Which of the orders would you like to copy? \n\n" + list.fullList()
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

    if user.Adding:
        return addingOrder(update, context)

    if user.Editing:
        return editingOrder(update, context)

    if user.Ordering:
        if user.currentNo == "" and \
                user.currentTitle == "":
            user.currentTitle = update.message.text
            update.message.reply_text('What is your phone number?' +
                                      ' (Send 1 if you do not want to display your phone number)')
            return

        if user.currentNo == "":
            if update.message.text.isnumeric() and len(update.message.text) == 8:
                user.currentNo = update.message.text
                user.Ordering = False
                return orderList(update, context)
            elif update.message.text == "1":
                user.currentNo = update.message.from_user.username
                user.Ordering = False
                return orderList(update, context)
            else:
                update.message.reply_text('Invalid Input: Please make sure that you have sent a 8 digit phone number'
                                          + ' or 1')

    if user.Splitting:
        if user.currentNo == "" and \
                user.currentTitle == "":
            user.currentTitle = update.message.text
            update.message.reply_text('What is your phone number? '
                                      + '(Send 1 if you do not want to display your phone number)')
            return
        elif user.currentNo == "":
            if update.message.text.isnumeric() and len(update.message.text) == 8:
                user.currentNo = update.message.text
                update.message.reply_text("Please send me your first item")
                user.addingPrice = True
                return
            elif update.message.text == "1":
                user.currentNo = update.message.from_user.username
                update.message.reply_text("Please send me your first item")
                user.addingPrice = True
                return
            else:
                update.message.reply_text('Invalid Input: Please make sure that you have sent a 8 digit phone number'
                                          + ' or 1')
        elif update.message.text != "/done" and user.addingPrice:
            if user.isRepeated(update.message.text):
                update.message.reply_text("You already have this item in the list")
                return
            user.items.append(update.message.text)
            update.message.reply_text("What is the price of this item?")
            user.addingPrice = False
            return
        elif update.message.text != "/done" and user.addingPrice == False:
            if isfloat(update.message.text):
                user.prices.append(update.message.text)
                update.message.reply_text("Good. now send me another item, or /done to finish.")
                user.addingPrice = True
            else:
                update.message.reply_text("Price has to be a number")
                return
        elif update.message.text == "/done":
            user.addingPrice = False
            return splitList(update, context)


def response(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    query.answer()

    if query.data == "135New Order":
        userId = update.callback_query.from_user.id
        user = backEnd.getUser(userId)
        if user.Splitting:
            query.message.reply_text("You're in the middle of creating a Split List, " +
                                     "finish that before creating another list or type /cancel"
                                     + " to terminate this order")
            return
        else:
            user.currentTitle = ""
            user.currentNo = ""
            return newOrder(query, context)

    if query.data == "135Check":
        return check(query, context)

    if query.data == "135SplitOrder":
        userId = update.callback_query.from_user.id
        user = backEnd.getUser(userId)
        user.currentTitle = ""
        user.currentNo = ""
        if user.Ordering:
            query.message.reply_text("You're in the middle of creating a Order List, " +
                                     "finish that before creating another list or type /cancel"
                                     + " to terminate this order")
            return
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
            currentUser.memberLists[backendId] = currentList
            return deleteCommand(currentUser.personalUpdate, context, currentList)

    if query.data[0:11] == "135NoDelete":
        userId = update.callback_query.from_user.id
        currentUser = backEnd.getUser(userId)
        if currentUser.Deleting:
            query.message.reply_text("Ok we shall leave your order there!")
            currentUser.Deleting = False
        else:
            return

    if query.data[0:12] == "135YesDelete":
        index = query.data[12:]
        userId = update.callback_query.from_user.id
        currentUser = backEnd.getUser(userId)
        if currentUser.Deleting:
            return deleteOrder(query, context, index)
        else:
            return

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
            backendId = currentList.backEndId
            currentUser.memberLists[backendId] = currentList
            return editCommand(currentUser.personalUpdate, context, currentList)

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
            return copyCommand(currentUser.personalUpdate, context, currentList)

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

    if query.data[0:6] == 'delete':
        userId = update.callback_query.message.chat.id
        user = backEnd.getUser(userId)
        index = user.listID
        orderId = query.data[6:]
        orderList = backEnd.OrderLists[index]
        order = orderList.orders[int(orderId) - 1]
        return deleteConfirm(query, context, order)

    if query.data[0:4] == 'edit':
        userId = update.callback_query.message.chat.id
        user = backEnd.getUser(userId)
        index = user.listID
        orderId = query.data[4:]
        orderList = backEnd.OrderLists[index]
        order = orderList.orders[int(orderId) - 1]
        return editPrompt(query, context, order)

    if query.data[0:4] == 'copy':
        userId = update.callback_query.message.chat.id
        user = backEnd.getUser(userId)
        index = user.listID
        orderId = query.data[4:]
        orderList = backEnd.OrderLists[index]
        order = orderList.orders[int(orderId) - 1]
        return copyOrder(query, context, order)



def newOrder(update: Update, context: CallbackContext) -> None:
    # instantiate a user and set the users Ordering to True
    userId = update.message.chat.id
    backEnd.addUser(userId)
    user = backEnd.getUser(userId)
    user.Ordering = True
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
    user = backEnd.getUser(userId)
    # instantiate a OrderList and add it to backend
    global listId
    global backEndId
    now = datetime.now()
    stringNow = json.dumps(now, default=str)
    orderingList = OrderList(listId, stringNow, backEndId)
    orderingList.Title = user.currentTitle
    orderingList.phoneNum = user.currentNo
    orderingList.ownerName = update.message.from_user.username
    backEnd.OrderLists.append(orderingList)
    # add the orderList to the users creators list
    user.creatorLists.append(orderingList)
    currTitle = user.currentTitle
    index = listId
    listId += 1
    backEndId += 1
    user.titleList.append(user.currentTitle)
    user.Ordering = False
    user.currentTitle = ""
    user.currentNo = ""

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
        text=backEnd.OrderLists[index].fullList(),
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
    orderList = backEnd.OrderLists[user.listID]
    orderId = orderList.giveIndex()
    order = Order(orderId, user_name)
    orderList = backEnd.OrderLists[user.listID]
    orderList.canUpdate = True

    orderList.peopleList.append(user_name)
    order.orderName = added_order
    orderList.orders.append(order)
    if user_name in orderList.orderSummary:
        orderList.orderSummary[user_name].append(order)
    else:
        orderList.orderSummary[user_name] = [order]

    if user_name != orderList.ownerName:
        if user_name in orderList.unpaid:
            orderList.unpaid[user_name].append(order)
        else:
            orderList.unpaid[user_name] = [order]
    text = backEnd.OrderLists[int(user.listUpdate.message)].fullList()
    orderList.addNewUpdate(user.listUpdate.callback_query)

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
    for value in orderList.updateList.values():
        value.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(ORDER_BUTTONS)
        )
    backEnd.getUser(userId).Adding = False
    return


def editingOrder(update: Update, context: CallbackContext) -> None:
    user_name = f'{update.message.from_user.username}'
    userId = update.message.from_user.id  # correct userID
    currentUser = backEnd.getUser(userId)
    index = currentUser.listID
    orderList = backEnd.OrderLists[index]
    order = currentUser.activeOrder
    currentUser.activeOrder = None
    editedOrder = update.message.text
    order.orderName = editedOrder

    # order.peopleList.pop(listIndex)
    # order.orders.pop(listIndex)
    # if user_name != order.ownerName:
    #     order.unpaid.pop(user_name)
    # order.peopleList.append(user_name)
    # order.orders.append(editedOrder)
    # if user_name != order.ownerName:
    #     order.unpaid[user_name] = editedOrder
    text = backEnd.OrderLists[int(currentUser.listUpdate.message)].fullList()
    orderList.addNewUpdate(currentUser.listUpdate.callback_query)

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
    for value in orderList.updateList.values():
        value.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(ORDER_BUTTONS)
        )
    currentUser.Editing = False


def editPrompt(update: Update, context: CallbackContext, order):
    userId = update.message.chat.id
    currentUser = backEnd.getUser(userId)
    currentUser.activeOrder = order
    update.message.reply_text("Your previous order was: \n" + order.orderName)
    update.message.reply_text("What is your new Order?")


def deleteOrder(update: Update, context: CallbackContext, orderId) -> None:
    user_name = f'{update.from_user.username}'
    userId = update.from_user.id  # correct userID
    currentUser = backEnd.getUser(userId)
    index = currentUser.listID
    orderList = backEnd.OrderLists[index]
    order = orderList.orders[int(orderId) - 1]

    orderList.peopleList.pop(int(orderId) - 1)
    orderList.orders.pop(int(orderId) - 1)
    if user_name != orderList.ownerName:
        orderList.unpaid[user_name].remove(order)
    orderList.orderSummary[user_name].remove(order)
    text = orderList.fullList()

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
    for value in orderList.updateList.values():
        value.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(ORDER_BUTTONS)
        )
    currentUser.Deleting = False


def deleteConfirm(update: Update, context: CallbackContext, order):
    userId = update.message.chat.id
    user = backEnd.getUser(userId)
    user_name = f'{update.message.chat.username}'
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="135YesDelete" + str(order.orderId)),
            InlineKeyboardButton("No", callback_data="135NoDelete" + str(order.orderId)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "Are you sure you want to delete your order from " + backEnd.OrderLists[user.listID].Title + "?"
        + "\n\n" + order.getOrd(),
        reply_markup=reply_markup)


def copyOrder(update: Update, context: CallbackContext, order) -> None:
    user_name = f'{update.from_user.username}'
    userId = update.from_user.id
    currentUser = backEnd.getUser(userId)
    index = currentUser.listID
    orderList = backEnd.OrderLists[index]
    newOrder = Order(orderList.giveIndex(), user_name)
    newOrder.orderName = order.orderName

    orderList.peopleList.append(user_name)
    orderList.orders.append(newOrder)
    if user_name in orderList.orderSummary:
        orderList.orderSummary[user_name].append(newOrder)
    else:
        orderList.orderSummary[user_name] = [newOrder]

    if user_name != orderList.ownerName:
        if user_name in orderList.unpaid:
            orderList.unpaid[user_name].append(newOrder)
        else:
            orderList.unpaid[user_name] = [newOrder]
    text = backEnd.OrderLists[int(currentUser.listUpdate.message)].fullList()
    orderList.addNewUpdate(currentUser.listUpdate.callback_query)

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
    update.message.reply_text("You have added " + newOrder.orderName + " as your new order!")
    for value in orderList.updateList.values():
        value.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(ORDER_BUTTONS)
        )
    backEnd.getUser(userId).Copying = False


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
    #an array of orders
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
    update.message.reply_text("What will be the title of your Split List be?")


def splitList(update: Update, context: CallbackContext) -> None:
    userId = update.message.from_user.id
    user = backEnd.getUser(userId)
    global splitListId
    global backEndId
    now = datetime.now()
    stringNow = json.dumps(now, default=str)
    splits = SplitList(splitListId, stringNow, backEndId)
    splits.ownerName = update.message.from_user.username
    splits.Title = user.currentTitle
    splits.phoneNum = user.currentNo
    splits.makeItemsDict(user.items, user.prices)
    backEnd.SplitLists.append(splits)
    user.creatorLists.append(splits)
    currTitle = user.currentTitle
    index = splitListId
    user.titleList.append(user.currentTitle)
    splitListId += 1
    backEndId += 1
    user.Splitting = False
    user.currentTitle = ""
    user.currentNo = ""
    user.items = []
    user.prices = []

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
    userId = update.message.from_user.id
    user = backEnd.getUser(userId)
    if backEnd.getUser(userId) is None:
        backEnd.addUser(userId)
    else:
        user.currentTitle = ""
        user.currentNo = ""
        user.items = []
        user.prices = []
        user.Adding = False
        user.Ordering = False
        user.Deleting = False
        user.Editing = False
        user.Copying = False
        user.Splitting = False
        user.addingPrice = False
        update.message.reply_text('Process has been terminated')


def main():
    dispatcher.add_handler(CommandHandler("start", startCommand))
    dispatcher.add_handler(CommandHandler("create", createCommand))
    dispatcher.add_handler(CommandHandler("cancel", cancel))
    dispatcher.add_handler(CallbackQueryHandler(response))

    # dispatcher.add_error_handler(error)
    dispatcher.add_handler(MessageHandler(Filters.text, prompts))
    # dispatcher.add_handler(MessageHandler(Filters.text, phoneNumber))
    dispatcher.add_handler(InlineQueryHandler(inlineOrderList))
    updater.start_polling()
    updater.idle()


main()
