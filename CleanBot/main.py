from telegram import *
from telegram.ext import *
from OrderList import OrderList
from SplitList import SplitList
from backEnd import backEnd
from Order import Order
from user import User
from datetime import datetime
import json
import firebase

updater = Updater('5316303881:AAEIysIUYoZ45d1EwN_5Jl6dGonJfv_ZE8g')
dispatcher = updater.dispatcher
START_MESSAGE = 'This bot will help you create an order list, check your outstanding payments, or split money! use /create to begin!'
CRASH_MESSAGE = 'Oops something went wrong, type /start and try again'
botURL = 'https://t.me/ezezezezezorderbot'
bot = Bot('5374066926:AAE7IMAU8bjduSafS1DAzjk6Kpz6X9zIHQ0')
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


def getAnd(str):
    for x in range(len(str)):
        if str[x] == "&":
            return x


def recoverList(index):
    dict = firebase.db.child("orderLists").child(index).get().val()
    if dict is None:
        return
    recovered = OrderList(index, dict['timing'], dict['backEndId'], dict['OwnerName'], dict["phoneNum"], dict["Title"])
    recovered.orderStatus = firebase.db.child("orderLists").child(index).get().val()["orderStatus"]
    orders = firebase.db.child("orderLists").child(index).child("orders").get()
    orderId = firebase.db.child("orderLists").child(index).get().val()["orderId"]
    unpaid = firebase.db.child("orderLists").child(index).child("unpaid").get()
    unpaidUpdate = firebase.db.child("orderLists").child(index).child("unpaidUpdate").get().val()
    updateList = firebase.db.child("orderLists").child(index).child("updateList").get().val()
    # if no orders just have a default orderlist object
    if firebase.db.child("orderLists").child(index).child("orders").get().val() is None:
        backEnd.OrderLists.append(recovered)
        return recovered
    # add orders one by one into orders field
    for v in orders.each():
        recovered.orders.append(v.val())
    if unpaid.each() is not None:
        # add orders into unpaid
        for x in unpaid.each():
            unpaidUser = firebase.db.child("orderLists").child(index).child("unpaid").child(x.key()).get()
            recovered.unpaid[x.key()] = []
            for y in unpaidUser.each():
                recovered.unpaid[x.key()].append(y.val())
        # add updates into unpaidUpdates
        for k, l in unpaidUpdate.items():
            update = Update.de_json(json.loads(l), bot)
            recovered.unpaidUpdate[k] = update
    # add updates of group chats of orderLists into an array
    for t, r in updateList.items():
        update = Update.de_json(json.loads(r), bot)
        recovered.updateList[t] = update
    backEnd.OrderLists.append(recovered)
    recovered.orderId = orderId
    return recovered


def recoverSplit(index):
    dict = firebase.db.child("splitLists").child(index).get().val()
    if dict is None:
        return
    recovered = SplitList(index, dict['timing'], dict['backEndId'], dict['OwnerName'], dict["phoneNum"], dict["Title"])
    recovered.orderStatus = firebase.db.child("splitLists").child(index).get().val()["orderStatus"]
    orders = firebase.db.child("splitLists").child(index).child("orders").get()
    updateList = firebase.db.child("splitLists").child(index).child("updateList").get().val()

    for x in orders.each():
        contArr = []
        unpaidArr = []
        updateArr = []
        item = x.key()
        price = x.val()["price"]
        cont = firebase.db.child("splitLists").child(index).child("orders").child(item).child("contributers").get()
        unpaid = firebase.db.child("splitLists").child(index).child("orders").child(item).child("unpaid").get()
        if cont.each() is not None:
            for c in cont.each():
                contArr.append(c.val()["username"])
        if unpaid.each() is not None:
            for u in unpaid.each():
                unpaidArr.append(u.val()["user"])
                update = Update.de_json(json.loads(u.val()["update"]), bot)
                updateArr.append(update)
        recovered.orders[item] = [price, contArr, unpaidArr, updateArr]
    if updateList is not None:
        for t, r in updateList.items():
            update = Update.de_json(json.loads(r), bot)
            recovered.updateList[t] = update
    backEnd.SplitLists.append(recovered)
    return recovered


def recoverUser(userId):
    dict = firebase.db.child("users").child(userId).child("creatorLists").get()
    backEnd.addUser(userId)
    recovered = backEnd.getUser(userId)
    if dict.val() is not None:
        for v in dict.each():
            recovered.creatorLists.append(v.val())
    update = firebase.db.child("users").child(userId).get().val()["personalUpdate"]
    recovered.personalUpdate = Update.de_json(json.loads(update), bot)
    debt = firebase.db.child("users").child(userId).child("debtList").get()
    if debt.val() is not None:
        for i in debt.each():
            recovered.debtList[i.key()] = i.val()
    return recovered


def isUserDatabase(userId):
    tri = firebase.db.child("users").child(userId).get().val()
    if tri is None:
        return False
    else:
        return True


def outstandingPayments(user, username):
    text = ""
    print(user.debtList)
    for x, y in user.debtList.items():
        id = y["listId"]
        type = y["type"]
        if type == "order":
            orderList = backEnd.getList(id)
            if orderList is None:
                orderList = recoverList(id)
                if orderList is None:
                    return
            orders = orderList.unpaid[username]
            if orders is not None:
                text = text + orderList.ownerName + " for " + orderList.Title + ": \n"
                index = 1
                for o in orders:
                    text += str(index) + ") " + o["order"] + " \n"
                    index += 1
        else:
            splitList = backEnd.getSplit(id)
            if splitList is None:
                splitList = recoverSplit(id)
                if splitList is None:
                    return
            items = splitList.orders
            itemDebt = ""
            index = 1
            for x, y in items.items():
                if username in y[2]:
                    itemDebt += str(index) + ") " + x + "\n"
                    index += 1
            if not itemDebt == "":
                text = text + splitList.ownerName + " for " + splitList.Title + ": \n" + itemDebt
        text = text + "\n"
    return text


def remindeveryone(currentUser):
    for i in range(len(currentUser.creatorLists)):
        type = currentUser.creatorLists[i]["type"]
        id = currentUser.creatorLists[i]["listId"]
        if type == "order":
            orderList = backEnd.getList(id)
            if orderList is None:
                orderList = recoverList(id)
                if orderList is None:
                    return
            if len(orderList.unpaid) != 0:
                for x, y in orderList.unpaid.items():
                    username = x
                    memberUpdate = orderList.unpaidUpdate[username]
                    text = "Just a reminder to transfer " + orderList.ownerName + ": for these orders:\n\n" + \
                           orderList.Title + "\n"
                    index = 1
                    for a in y:
                        text = text + str(index) + ") " + a["order"] + "\n"
                        index += 1
                    memberUpdate.message.reply_text(text)
        else:
            splitList = backEnd.getSplit(id)
            if splitList is None:
                splitList = recoverSplit(id)
                if splitList is None:
                    return
            personunpaiditems = {}
            for key in splitList.orders.keys():
                peopleupdatelist = splitList.orders[key][3]
                for i in range(len(peopleupdatelist)):
                    if peopleupdatelist[i] in personunpaiditems:
                        personunpaiditems[peopleupdatelist[i]].append(key)
                    else:
                        personunpaiditems[peopleupdatelist[i]] = []
                        personunpaiditems[peopleupdatelist[i]].append(key)

            for key in personunpaiditems:
                text = "Just a reminder to transfer " + splitList.ownerName + ": for the following items:\n\n" + \
                       splitList.Title + "\n"
                index = 1
                for i in range(len(personunpaiditems[key])):
                    text = text + str(index) + ") " + personunpaiditems[key][i] + "\n"
                    index += 1
                key.message.reply_text(text)


def outstandingOrders(currentUser, user_name):
    text = ""
    for i in range(len(currentUser.creatorLists)):
        type = currentUser.creatorLists[i]["type"]
        id = currentUser.creatorLists[i]["listId"]
        print(currentUser.creatorLists)
        if type == "order":
            orderList = backEnd.getList(id)
            if orderList is None:
                orderList = recoverList(id)
                if orderList is None:
                    return
            if len(orderList.unpaid) != 0:
                text = text + "Yet to pay for " + orderList.Title + ": " + orderList.getCheckList() + " \n"
        else:
            splitList = backEnd.getSplit(id)
            if splitList is None:
                splitList = recoverSplit(id)
                if splitList is None:
                    return
            items = splitList.orders
            debtors = ""
            index = 1
            for x, y in items.items():
                this = ""
                if not len(y[2]) == 0:
                    for r in y[2]:
                        this += r + "\n"
                    debtors += debtors + str(index) + ") " + x + "\n" + this
                    index += 1
            if not debtors == "":
                text = text + "Yet to pay for " + splitList.Title + ": \n" + debtors + " \n"
        text = text + " \n"
    return text


def startCommand(update: Update, context: CallbackContext) -> None:
    userId = update.message.from_user.id
    if not backEnd.isUser(userId):
        tri = firebase.db.child("users").child(userId).get().val()
        if tri is None:
            firebase.db.child("users").child(userId).set({"id": userId, "personalUpdate": update.to_json()})
            backEnd.addUser(userId)
        else:
            user = recoverUser(userId)
    user = backEnd.getUser(userId)
    user.personalUpdate = update
    update.message.reply_text("The bot is now activated, you no longer have to activate it again!")


def createCommand(update: Update, context: CallbackContext) -> None:
    userId = update.message.from_user.id
    if not backEnd.isUser(userId):
        tri = firebase.db.child("users").child(userId).get().val()
        if tri is None:
            firebase.db.child("users").child(userId).set({"id": userId, "personalUpdate": update.to_json()})
            backEnd.addUser(userId)
        else:
            user = recoverUser(userId)

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


def addCommand(update: Update, context: CallbackContext, listID) -> None:
    userId = update.message.from_user.id
    user = backEnd.getUser(userId)

    if user.Copying or user.Editing or user.Deleting or user.Adding:
        status = user.orderStatus()
        update.message.reply_text("You are currently " + status +
                                  " an order, complete that process first or type /cancel to terminate the process")
    else:
        user.Adding = True
        user.listID = listID
        update.message.reply_text("Adding Order for: " + backEnd.getList(user.listID).Title)
        update.message.reply_text("What is your Order?")


def deleteCommand(update: Update, context: CallbackContext, list, index) -> None:
    userId = update.message.from_user.id
    user = backEnd.getUser(userId)
    user_name = f'{update.message.from_user.username}'

    if not list.isOrder(user_name):
        update.message.reply_text(
            "You have yet to add your order! You can only delete your order after you've added it in 😬")
        return

    elif user.Copying or user.Editing or user.Deleting or user.Adding:
        status = user.orderStatus()
        update.message.reply_text("You are currently " + status +
                                  " an order, complete that process first or type /cancel to terminate the process")
        return

    else:
        orderArray = list.orderArray(user_name)
        idArray = list.idArray(user_name)
        user.listID = index
        user.Deleting = True
        user.deletePart = True
        delOrd = []
        keyboard = [delOrd]
        for x in range(len(orderArray)):
            orderIndex = str(x + 1)
            delOrd.append(InlineKeyboardButton(orderIndex, callback_data="delete" + str(str(idArray[x])) +
                                                                         "&" + str(user.listID)))
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            "Which of your orders would you like to delete?"
            + "\n\n" + list.indivOrders(user_name),
            reply_markup=reply_markup)


def editCommand(update: Update, context: CallbackContext, list, index) -> None:
    userId = update.message.from_user.id
    user = backEnd.getUser(userId)
    user_name = f'{update.message.from_user.username}'

    if not list.isOrder(user_name):
        update.message.reply_text(
            "You have yet to add your order! You can only edit your order after you've added it in 😬")
        return

    elif user.Copying or user.Editing or user.Deleting or user.Adding:
        status = user.orderStatus()
        update.message.reply_text("You are currently " + status +
                                  " an order, complete that process first or type /cancel to terminate the process")
        return

    else:
        orderArray = list.orderArray(user_name)
        idArray = list.idArray(user_name)
        user.listID = index
        user.Editing = True
        editOrd = []
        keyboard = [editOrd]
        for x in range(len(orderArray)):
            orderIndex = str(x + 1)
            editOrd.append(InlineKeyboardButton(orderIndex, callback_data="edit" + str(idArray[x]) +
                                                                          "&" + str(user.listID)))
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            "Which of your orders would you like to edit?"
            + "\n\n" + list.indivOrders(user_name),
            reply_markup=reply_markup)


def copyCommand(update: Update, context: CallbackContext, list, index) -> None:
    userId = update.message.from_user.id
    user = backEnd.getUser(userId)
    user_name = f'{update.message.from_user.username}'

    if len(list.orders) == 0:
        update.message.reply_text("The Order List is empty, there is no one to copy from!")
        return

    elif user.Copying or user.Editing or user.Deleting or user.Adding:
        status = user.orderStatus()
        update.message.reply_text("You are currently " + status +
                                  " an order, complete that process first or type /cancel to terminate the process")
        return

    else:
        user.Copying = True
        user.copyPart = True
        user.listID = index
        peopleKey = []
        keyboard = [peopleKey]
        for x in range(len(list.orders)):
            orderId = list.orders[x]["orderId"]
            peopleKey.append(InlineKeyboardButton(str(x + 1), callback_data="copy" + str(orderId)
                                                                            + "&" + str(user.listID)))
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = "Which of the orders would you like to copy? \n\n" + list.fullList()
        update.message.reply_text(
            text=text,
            reply_markup=reply_markup)


# for message handler
def prompts(update: Update, context: CallbackContext):
    userId = update.message.from_user.id
    user = backEnd.getUser(userId)

    if user is None:
        update.message.reply_text(CRASH_MESSAGE)
        return

    if (user.Adding == False and user.Ordering == False and user.Deleting == False
            and user.Editing == False and user.Copying == False and user.Splitting == False):
        update.message.reply_text(START_MESSAGE)
        return

    if user.Adding:
        return addingOrder(update, context)

    if user.editPart:
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


def response(update: Update, context: CallbackContext, order=None) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    query.answer()

    if query.data == "135New Order":
        userId = update.callback_query.from_user.id
        user = backEnd.getUser(userId)
        if user is None:
            query.message.reply_text("Oops something went wrong, try /create again")
            return
        elif user.Splitting:
            query.message.reply_text("You're in the middle of creating a Split List, " +
                                     "finish that before creating another list or type /cancel"
                                     + " to terminate this order")
            return
        elif user.Adding or user.Editing or user.Deleting or user.Copying:
            return
        else:
            user.currentTitle = ""
            user.currentNo = ""
            return newOrder(query, context)

    if query.data == "135Check":
        userId = update.callback_query.from_user.id
        user = backEnd.getUser(userId)
        if user is None:
            query.message.reply_text("Oops something went wrong, try /create again")
            return
        elif user.Adding or user.Editing or user.Deleting or user.Copying:
            return
        return check(query, context)

    if query.data == "135SplitOrder":
        userId = update.callback_query.from_user.id
        user = backEnd.getUser(userId)
        if user is None:
            query.message.reply_text("Oops something went wrong, try /create again")
            return
        elif user.Ordering:
            query.message.reply_text("You're in the middle of creating a Order List, " +
                                     "finish that before creating another list or type /cancel"
                                     + " to terminate this order")
            return
        elif user.Adding or user.Editing or user.Deleting or user.Copying:
            return
        else:
            user.currentTitle = ""
            user.currentNo = ""
            return split(query, context)

    if query.data[0:12] == "135Add Order":
        userId = update.callback_query.from_user.id
        if backEnd.getUser(userId) is None:
            if isUserDatabase(userId):
                user = recoverUser(userId)
            else:
                return
        index = int(query.data[12:])
        # check if user is in backend, if not add the user in. Then add the orderList into the user
        # change users.adding to true
        currentUser = backEnd.getUser(userId)
        # currentUser.listID = index
        currentUser.listUpdate = update
        currentList = backEnd.getList(index)
        if currentList is None:
            currentList = recoverList(index)
            if currentList is None:
                return
        currentList.groupChatListUpdate = update
        return addCommand(currentUser.personalUpdate, context, index)

    if query.data[0:15] == "135Delete Order":
        userId = update.callback_query.from_user.id
        if backEnd.getUser(userId) is None:
            if isUserDatabase(userId):
                user = recoverUser(userId)
            else:
                return
        index = int(query.data[15:])
        # check if user is in backend, if not add the user in. Then add the orderList into the user
        # change users.adding to true
        currentUser = backEnd.getUser(userId)
        currentUser.listUpdate = update
        currentList = backEnd.getList(index)
        if currentList is None:
            currentList = recoverList(index)
            if currentList is None:
                return
        return deleteCommand(currentUser.personalUpdate, context, currentList, index)

    if query.data[0:11] == "135NoDelete":
        userId = update.callback_query.from_user.id
        currentUser = backEnd.getUser(userId)
        if currentUser is None:
            query.message.reply_text(CRASH_MESSAGE)
        elif currentUser.deleteConfirm:
            query.message.reply_text("Ok we shall leave your order there!")
            currentUser.Deleting = False
        else:
            return

    if query.data[0:12] == "135YesDelete":
        index = query.data[12:]
        userId = update.callback_query.from_user.id
        currentUser = backEnd.getUser(userId)
        if currentUser is None:
            query.message.reply_text(CRASH_MESSAGE)
        elif currentUser.deleteConfirm:
            return deleteOrder(query, context, index)
        else:
            return

    if query.data[0:13] == "135Edit Order":
        userId = update.callback_query.from_user.id
        if backEnd.getUser(userId) is None:
            if isUserDatabase(userId):
                user = recoverUser(userId)
            else:
                return
        index = int(query.data[13:])
        # check if user is in backend, if not add the user in. Then add the orderList into the user
        # change users.adding to true
        currentUser = backEnd.getUser(userId)
        # currentUser.listID = index
        currentUser.listUpdate = update
        currentList = backEnd.getList(index)
        if currentList is None:
            currentList = recoverList(index)
            if currentList is None:
                return
        currentList.groupChatListUpdate = update
        return editCommand(currentUser.personalUpdate, context, currentList, index)

    if query.data[0:13] == "135Copy Order":
        userId = update.callback_query.from_user.id
        if backEnd.getUser(userId) is None:
            if isUserDatabase(userId):
                user = recoverUser(userId)
            else:
                return
        index = int(query.data[13:])
        currentUser = backEnd.getUser(userId)
        # currentUser.listID = index
        currentUser.listUpdate = update
        currentList = backEnd.getUser(index)
        if currentList is None:
            currentList = recoverList(index)
            if currentList is None:
                return
        currentList.groupChatListUpdate = update
        return copyCommand(currentUser.personalUpdate, context, currentList, index)

    if query.data[0:9] == "135Update":
        index = int(query.data[9:])
        orderList = backEnd.getList(index)
        userId = update.callback_query.from_user.id
        currentUser = backEnd.getUser(userId)
        if currentUser is None:
            currentUser = recoverUser(userId)
        currentUser.listID = index
        currentUser.listUpdate = update
        if orderList is None:
            orderList = recoverList(index)
            if orderList is None:
                return
        return updateList(update, context, index)

    if query.data[0:14] == "135Close Order":
        index = int(query.data[14:])
        orderList = backEnd.getList(index)
        if orderList is None:
            orderList = recoverList(index)
            if orderList is None:
                return
        length = len(orderList.orders)
        if length == 0:
            query.message.reply_text("Cannot close an empty Order List")
        elif not orderList.orderStatus:
            query.message.reply_text("Order List is already Closed")
        else:
            orderList.orderStatus = False
            firebase.db.child("orderLists").child(index).update({"orderStatus": False})
            userId = update.callback_query.message.chat.id
            currentUser = backEnd.getUser(userId)
            if currentUser is None:
                currentUser = recoverUser(userId)
            currentUser.listID = index
            # currentUser.listUpdate = update
            return closedOrder(update, context, index)

    if query.data[0:17] == "135SplitCloseList":
        index = int(query.data[17:])
        splitOrder = backEnd.getSplit(index)
        if splitOrder is None:
            splitOrder = recoverSplit(index)
            if splitOrder is None:
                return
        if splitOrder.isEmpty():
            query.message.reply_text("Cannot close an empty Order List")
        elif not splitOrder.orderStatus:
            query.message.reply_text("Order List is already Closed")
        else:
            splitOrder.orderStatus = False
            firebase.db.child("splitLists").child(index).update({"orderStatus": False})
            userId = update.callback_query.message.chat.id
            currentUser = backEnd.getUser(userId)
            if currentUser is None:
                currentUser = recoverUser(userId)
            currentUser.listID = index
            return closedSplitList(update, context, index)

    if query.data[0:13] == "135Open Order":
        index = int(query.data[13:])
        orderList = backEnd.getList(index)
        if orderList is None:
            orderList = recoverList(index)
            if orderList is None:
                return
        if orderList.orderStatus:
            query.message.reply_text("Order List is already Opened")
        else:
            orderList.orderStatus = True
            firebase.db.child("orderLists").child(index).update({"orderStatus": True})
            userId = update.callback_query.message.chat.id
            currentUser = backEnd.getUser(userId)
            if currentUser is None:
                currentUser = recoverUser(userId)
            currentUser.listID = index
            # currentUser.listUpdate = update
            return openOrder(update, context, index)

    if query.data[0:9] == "135Remind":
        index = int(query.data[9:])
        orderList = backEnd.getList(index)
        if orderList is None:
            orderList = recoverList(index)
            if orderList is None:
                return
        userId = update.callback_query.message.chat.id
        currentUser = backEnd.getUser(userId)
        if currentUser is None:
            currentUser = recoverUser(userId)
        if orderList.orderStatus is True:
            query.message.reply_text("Close the list before using this button")
            return
        return remindorder(update, context, index)

    if query.data[0:14] == "135SplitRemind":
        index = int(query.data[14:])
        orderList = backEnd.getSplit(index)
        if orderList is None:
            orderList = recoverSplit(index)
            if orderList is None:
                return
        userId = update.callback_query.message.chat.id
        currentUser = backEnd.getUser(userId)
        if currentUser is None:
            currentUser = recoverUser(userId)
        return remindsplit(update, context, index)

    if query.data[0:16] == '135SplitOpenList':
        index = int(query.data[16:])
        splitOrder = backEnd.getSplit(index)
        if splitOrder is None:
            splitOrder = recoverSplit(index)
            if splitOrder is None:
                return
        if splitOrder.orderStatus:
            query.message.reply_text("Order List is already Opened")
        # currentUser.listUpdate = update
        else:
            splitOrder.orderStatus = True
            firebase.db.child("splitLists").child(index).update({"orderStatus": True})
            userId = update.callback_query.message.chat.id
            currentUser = backEnd.getUser(userId)
            if currentUser is None:
                currentUser = recoverUser(userId)
            currentUser.listID = index
            return openSplitList(update, context, index)

    if query.data[0:7] == "135Paid":
        userId = update.callback_query.from_user.id
        if backEnd.getUser(userId) is None:
            tri = firebase.db.child("users").child(userId).child("creatorLists").get().val()
            if tri is None:
                return
            else:
                user = recoverUser(userId)
        index = int(query.data[7:])
        username = update.callback_query.from_user.username
        currentUser = backEnd.getUser(userId)
        currentUser.listID = index
        orderList = backEnd.getList(index)
        if orderList is None:
            orderList = recoverList(index)
            if orderList is None:
                return
        if len(orderList.orders) == 0:
            return
        elif orderList.ownerName == username:
            return
        elif orderList.paidStatus(username):
            return paid(update, context)
        else:
            return unpay(update, context)

    if query.data[0:14] == '135CheckRemind':
        userId = update.callback_query.from_user.id
        user = backEnd.getUser(userId)
        if user is None:
            query.message.reply_text("Oops something went wrong, try /create then click check again")
            return
        return remindall(update, context)

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
        print(userId)
        if backEnd.getUser(userId) is None:
            if isUserDatabase(userId):
                currentUser = recoverUser(userId)
            else:
                print("here")
                return
        currentList = backEnd.getSplit(index)
        currentUser = backEnd.getUser(userId)
        currentUser.listID = index
        currentUser.listUpdate = update
        if currentList is None:
            currentList = recoverSplit(index)
            if currentList is None:
                return
        return contribute(update, context, item, index)

    if query.data[0:14] == "135SplitUpdate":
        index = int(query.data[14:])
        splitOrder = backEnd.getSplit(index)
        userId = update.callback_query.from_user.id
        currentUser = backEnd.getUser(userId)
        if currentUser is None:
            currentUser = recoverUser(userId)
        currentUser.listID = index
        currentUser.listUpdate = update
        if splitOrder is None:
            splitOrder = recoverSplit(index)
            if splitOrder is None:
                return
        return updateSplitList(update, context)

    if query.data[0:12] == "135SplitPaid":
        userId = update.callback_query.from_user.id
        username = update.callback_query.from_user.username
        if backEnd.getUser(userId) is None:
            tri = firebase.db.child("users").child(userId).get().val()
            if tri is None:
                return
            else:
                user = recoverUser(userId)
        item = ''
        indexString = ''
        for i in range(len(query.data)):
            if ord(query.data[12 + i]) >= 48 and ord(query.data[12 + i]) <= 57:
                indexString = indexString + query.data[12 + i]
            else:
                item = item + query.data[13 + i:]
                break
        index = int(indexString)
        currentList = backEnd.getList(index)
        if currentList is None:
            currentList = recoverSplit(index)
            if currentList is None:
                return
        if currentList.ownerName == username:
            return
        elif currentList.paidStatus(username):
            print(currentList.orders)
            # try:
            return splitPaid(update, context, item, index)
            # except:
            #     return
        else:
            print(currentList.orders)
            try:
                return splitUnpay(update, context, item, index)
            except:
                return

    if query.data[0:6] == 'delete':
        andIndex = getAnd(query.data)
        userId = update.callback_query.message.chat.id
        user = backEnd.getUser(userId)
        if user is None:
            query.message.reply_text(CRASH_MESSAGE)
            return
        if not user.deletePart:
            return
        index = user.listID
        orderId = query.data[6:andIndex]
        listId = query.data[andIndex + 1:]
        orderList = backEnd.getList(index)
        orderName = orderList.getName(orderId)
        if user.Deleting and user.listID == int(listId):
            return deleteConfirm(query, context, orderName, orderId)
        else:
            return

    if query.data[0:4] == 'edit':
        andIndex = getAnd(query.data)
        userId = update.callback_query.message.chat.id
        user = backEnd.getUser(userId)
        if user is None:
            query.message.reply_text(CRASH_MESSAGE)
            return
        index = user.listID
        orderId = query.data[4:andIndex]
        listId = query.data[andIndex + 1:]
        orderList = backEnd.getList(index)
        orderName = orderList.getName(orderId)

        if user.Editing and user.listID == int(listId):
            user.editPart = True
            return editPrompt(query, context, orderName, orderId)
        else:
            return

    if query.data[0:4] == 'copy':
        andIndex = getAnd(query.data)
        userId = update.callback_query.message.chat.id
        user = backEnd.getUser(userId)
        if user is None:
            query.message.reply_text(CRASH_MESSAGE)
            return
        elif not user.copyPart:
            return
        index = user.listID
        orderId = query.data[4:andIndex]
        listId = query.data[andIndex + 1:]
        orderList = backEnd.getList(index)
        orderName = orderList.getName(orderId)
        if user.Copying and user.listID == int(listId):
            return copyOrder(query, context, orderName, orderId)
        else:
            return


def newOrder(update: Update, context: CallbackContext) -> None:
    # instantiate a user and set the users Ordering to True
    userId = update.message.chat.id
    user = backEnd.getUser(userId)
    user.Ordering = True
    # add the user to backend userList if not inside alr
    update.message.reply_text('What will the title of your Order List be?')


def updateList(update: Update, context: CallbackContext, index) -> None:
    orderList = backEnd.getList(index)

    keyboard = [
        [
            InlineKeyboardButton('Publish Order List',
                                 switch_inline_query=orderList.Title)
        ],
        [
            InlineKeyboardButton('Update', callback_data='135Update' + str(index))
        ],
        [
            InlineKeyboardButton('Remind', callback_data='135Remind' + str(index))
        ],
        [
            InlineKeyboardButton('Close Order', callback_data='135Close Order' + str(index)),
            InlineKeyboardButton('Open Order', callback_data='135Open Order' + str(index))
        ]
    ]
    try:
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.callback_query.edit_message_text(
            text=orderList.fullList(),
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    except:
        return


def orderList(update: Update, context: CallbackContext) -> None:
    userId = update.message.from_user.id
    user = backEnd.getUser(userId)
    # instantiate a OrderList and add it to backend
    global listId
    global backEndId
    now = datetime.now()
    stringNow = json.dumps(now, default=str)[1:20]
    Title = user.currentTitle
    phoneNum = user.currentNo
    ownerName = update.message.from_user.username
    orderingList = OrderList(listId, stringNow, backEndId, ownerName, phoneNum, Title)
    backEnd.OrderLists.append(orderingList)
    data = {"listId": listId, "backEndId": backEndId, "timing": stringNow,
            "OwnerName": update.message.from_user.username,
            "phoneNum": user.currentNo, "Title": user.currentTitle, "orderId": 0, "orderStatus": True}
    firebase.db.child("orderLists").child(listId).set(data)
    # add the orderList to the users creators list
    data = {"backEndId": backEndId, "title": user.currentTitle, "type": "order", "listId": listId, "timing": stringNow}
    user.creatorLists.append(data)
    firebase.db.child("users").child(userId).child("creatorLists").push(data)
    index = listId
    listId += 1
    backEndId += 1
    firebase.db.child("counters").update({"listId": listId})
    firebase.db.child("counters").update({"backEndId": backEndId})
    user.Ordering = False
    user.currentTitle = ""
    user.currentNo = ""

    keyboard = [
        [
            InlineKeyboardButton('Publish Order List',
                                 switch_inline_query=user.currentTitle)
        ],
        [
            InlineKeyboardButton('Update', callback_data='135Update' + str(index))
        ],
        [
            InlineKeyboardButton('Remind', callback_data='135Remind' + str(index))
        ],
        [
            InlineKeyboardButton('Close Order', callback_data='135Close Order' + str(index)),
            InlineKeyboardButton('Open Order', callback_data='135Open Order' + str(index))
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        text=backEnd.getList(index).fullList(),
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )


def inlineOrderList(update: Update, context: CallbackContext):
    userId = update.inline_query.from_user.id
    user = backEnd.getUser(userId)
    if user is None:
        dict = firebase.db.child("users").child(userId).child("creatorLists").get()
        backEnd.addUser(userId)
        user = backEnd.getUser(userId)
        for v in dict.each():
            user.creatorLists.append(v.val())

    results = []

    for x in range(len(user.creatorLists)):
        details = user.creatorLists[x]
        index = details['listId']
        title = details['title']
        backIndex = details['backEndId']
        if details['type'] == "order":
            orderlist = backEnd.getList(index)
            if orderlist is None:
                recoverList(index)
                if orderList is None:
                    return
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
                    description=details['timing'],
                    input_message_content=InputTextMessageContent(backEnd.getList(index).fullList()),
                    reply_markup=InlineKeyboardMarkup(ORDER_BUTTONS),
                    thumb_url="https://i.ibb.co/60fTBV9/ezorder-logo.jpg",
                )
            )
        else:
            splitList = backEnd.getSplit(index)
            if splitList is None:
                splitList = recoverSplit(index)
                if splitList is None:
                    return
            items = splitList.itemArray()
            itemsKey = []
            buttons = [itemsKey, [
                InlineKeyboardButton('Bot Chat', url=botURL)
            ]]
            for x in items:
                itemsKey.append(InlineKeyboardButton(x, callback_data="135Contribute" + str(index) + "/" + x))
            reply_markup = InlineKeyboardMarkup(buttons)
            results.append(
                InlineQueryResultArticle(
                    id=backIndex,
                    title=title,
                    description=splitList.timing,
                    input_message_content=InputTextMessageContent(backEnd.getSplit(index).contributorsList()),
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
    orderList = backEnd.getList(user.listID)
    backEndId = orderList.backEndId
    orderId = orderList.orderId
    data = {"orderId": orderId, "user": user_name, "order": added_order}
    orderList.orders.append(data)
    firebase.db.child("orderLists").child(user.listID).child("orders").push(data)
    orderList.orderId += 1
    firebase.db.child("orderLists").child(user.listID).update({"orderId": orderList.orderId})
    orderList.canUpdate = True
    if not user_name == orderList.ownerName:
        firebase.db.child("orderLists").child(user.listID).child("unpaid").child(user_name).push(data)
        if not user_name in orderList.unpaid:
            orderList.unpaid[user_name] = [data]
            orderList.unpaidUpdate[user_name] = user.personalUpdate
            firebase.db.child("orderLists").child(user.listID).child("unpaidUpdate") \
                .set({user_name: user.personalUpdate.to_json()})
        else:
            orderList.unpaid[user_name].append(data)
        # debtlist
        debtListData = {"listId": user.listID, "type": "order"}
        firebase.db.child("users").child(userId).child("debtList").child(backEndId).set(debtListData)
        user.debtList[backEndId] = debtListData

    text = orderList.fullList()
    orderList.addNewUpdate(user.listUpdate, user.listID)
    back = str(user.listID)
    ORDER_BUTTONS = [
        [
            InlineKeyboardButton('Add Order', callback_data='135Add Order' + back),
            InlineKeyboardButton('Edit Order', callback_data='135Edit Order' + back)
        ],
        [
            InlineKeyboardButton('Copy Order', callback_data='135Copy Order' + back),
            InlineKeyboardButton('Delete Order', callback_data='135Delete Order' + back)
        ],
        [
            InlineKeyboardButton('Bot Chat', url=botURL)
        ]
    ]
    update.message.reply_text("Your order has been added!")
    for value in orderList.updateList.values():
        value.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(ORDER_BUTTONS)
        )
    backEnd.getUser(userId).Adding = False
    return


def editingOrder(update: Update, context: CallbackContext) -> None:
    userId = update.message.from_user.id  # correct userID
    user_name = update.message.from_user.username
    currentUser = backEnd.getUser(userId)
    index = currentUser.listID
    orderList = backEnd.getList(index)
    orderId = currentUser.activeOrder
    currentUser.activeOrder = None
    editedOrder = update.message.text
    orderList.changeOrder(editedOrder, orderId)
    ed = firebase.db.child("orderLists").child(index).child("orders").get()
    for x in ed.each():
        if x.val()["orderId"] == int(orderId):
            save = x.key()
            firebase.db.child("orderLists").child(index).child("orders").child(save).update({"order": editedOrder})
    if not user_name == orderList.ownerName:
        edUnpaid = firebase.db.child("orderLists").child(index).child("unpaid").child(user_name).get()
        for x in edUnpaid.each():
            if x.val()["orderId"] == int(orderId):
                saveUnpaid = x.key()
                firebase.db.child("orderLists").child(index).child("unpaid").child(user_name). \
                    child(saveUnpaid).update(({"order": editedOrder}))
        for y in orderList.unpaid[user_name]:
            if y["orderId"] == int(orderId):
                y["order"] = editedOrder
        orderList.unpaidUpdate[user_name] = currentUser.personalUpdate
        firebase.db.child("orderLists").child(currentUser.listID).child("unpaidUpdate") \
            .set({user_name: currentUser.personalUpdate.to_json()})

    # order.peopleList.pop(listIndex)
    # order.orders.pop(listIndex)
    # if user_name != order.ownerName:
    #     order.unpaid.pop(user_name)
    # order.peopleList.append(user_name)
    # order.orders.append(editedOrder)
    # if user_name != order.ownerName:
    #     order.unpaid[user_name] = editedOrder
    text = orderList.fullList()
    orderList.addNewUpdate(currentUser.listUpdate, index)

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

    try:
        for value in orderList.updateList.values():
            value.callback_query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(ORDER_BUTTONS)
            )
            update.message.reply_text("Your Order has been Edited!")
    except:
        update.message.reply_text("Your Order was the same")
    currentUser.Editing = False
    currentUser.editPart = False


def editPrompt(update: Update, context: CallbackContext, order, orderId):
    userId = update.message.chat.id
    currentUser = backEnd.getUser(userId)
    currentUser.activeOrder = orderId
    update.message.reply_text("Your previous order was: \n" + order)
    update.message.reply_text("What is your new Order?")


def deleteOrder(update: Update, context: CallbackContext, orderId) -> None:
    user_name = f'{update.from_user.username}'
    userId = update.from_user.id  # correct userID
    currentUser = backEnd.getUser(userId)
    index = currentUser.listID
    orderList = backEnd.getList(index)
    backEndId = orderList.backEndId
    dels = firebase.db.child("orderLists").child(index).child("orders").get()

    orderList.getRid(orderId)
    for x in dels.each():
        if x.val()["orderId"] == int(orderId):
            save = x.key()
            firebase.db.child("orderLists").child(index).child("orders").child(save).remove()
    if not user_name == orderList.ownerName:
        delsUnpaid = firebase.db.child("orderLists").child(index).child("unpaid").child(user_name).get()
        for x in delsUnpaid.each():
            if x.val()["orderId"] == int(orderId):
                saveUnpaid = x.key()
                firebase.db.child("orderLists").child(index).child("unpaid").child(user_name). \
                    child(saveUnpaid).remove()
        for y in range(len(orderList.unpaid[user_name])):
            if orderList.unpaid[user_name][y]["orderId"] == int(orderId):
                orderList.unpaid[user_name].pop(y)
        orderList.unpaidUpdate[user_name] = currentUser.personalUpdate
        firebase.db.child("orderLists").child(currentUser.listID).child("unpaidUpdate") \
            .set({user_name: currentUser.personalUpdate.to_json()})
        currentUser.debtList.pop(backEndId)
        firebase.db.child("users").child(userId).child("debtList").child(backEndId).remove()

    text = orderList.fullList()

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

    update.message.reply_text("Your Order has been deleted!")
    orderList.addNewUpdate(currentUser.listUpdate, index)
    for value in orderList.updateList.values():
        value.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(ORDER_BUTTONS)
        )
    currentUser.Deleting = False
    currentUser.deleteConfirm = False
    currentUser.deletePart = False


def deleteConfirm(update: Update, context: CallbackContext, orderName, orderId):
    userId = update.message.chat.id
    user = backEnd.getUser(userId)
    user_name = f'{update.message.chat.username}'
    user.deleteConfirm = True
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="135YesDelete" + str(orderId)),
            InlineKeyboardButton("No", callback_data="135NoDelete" + str(orderId)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "Are you sure you want to delete your order from " + backEnd.getList(user.listID).Title + "?"
        + "\n\n" + orderName,
        reply_markup=reply_markup)


def copyOrder(update: Update, context: CallbackContext, orderName, orderId) -> None:
    user_name = f'{update.from_user.username}'
    userId = update.from_user.id
    currentUser = backEnd.getUser(userId)
    index = currentUser.listID
    orderList = backEnd.getList(index)
    backEndId = orderList.backEndId
    newId = orderList.orderId
    data = {"orderId": newId, "user": user_name, "order": orderName}
    orderList.orders.append(data)
    firebase.db.child("orderLists").child(currentUser.listID).child("orders").push(data)
    orderList.orderId += 1
    firebase.db.child("orderLists").child(currentUser.listID).update({"orderId": orderList.orderId})
    if not user_name == orderList.ownerName:
        firebase.db.child("orderLists").child(currentUser.listID).child("unpaid").child(user_name).push(data)
        if not user_name in orderList.unpaid:
            orderList.unpaid[user_name] = [data]
            orderList.unpaidUpdate[user_name] = currentUser.personalUpdate
            firebase.db.child("orderLists").child(currentUser.listID).child("unpaidUpdate") \
                .set({user_name: currentUser.personalUpdate.to_json()})
        else:
            orderList.unpaid[user_name].append(data)
        debtListData = {"listId": currentUser.listID, "type": "order"}
        firebase.db.child("users").child(userId).child("debtList").child(backEndId).set(debtListData)
        currentUser.debtList[backEndId] = debtListData

    text = orderList.fullList()
    orderList.addNewUpdate(currentUser.listUpdate, index)

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
    update.message.reply_text("You have added " + orderName + " as your new order!")
    for value in orderList.updateList.values():
        value.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(ORDER_BUTTONS)
        )
    currentUser.Copying = False
    currentUser.copyPart = False


def closedOrder(update: Update, context: CallbackContext, index) -> None:
    currentOrder = backEnd.getList(index)
    userId = update.callback_query.message.chat.id  # correct userID
    text = currentOrder.paymentList()
    # index = user.listID
    title = currentOrder.Title

    BUTTONS = [
        [
            InlineKeyboardButton('Paid', callback_data='135Paid' + str(index)),
        ],
        [
            InlineKeyboardButton("PayLah!", url="https://www.dbs.com.sg/personal/mobile/paylink"),
        ]
    ]
    update.callback_query.message.reply_text("Order List " + "'" + title + "'" + " is now closed")
    for value in currentOrder.updateList.values():
        value.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(BUTTONS)
        )


def openOrder(update: Update, context: CallbackContext, index) -> None:
    userId = update.callback_query.message.chat.id  # correct userID
    currentUser = backEnd.getUser(userId)
    currentOrder = backEnd.getList(index)
    text = currentOrder.fullList()
    title = currentOrder.Title

    BUTTONS = [
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

    update.callback_query.message.reply_text("Order List " + "'" + title + "'" + " is now opened")
    for value in currentOrder.updateList.values():
        value.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(BUTTONS)
        )


def paid(update: Update, context: CallbackContext) -> None:
    user_name = f'{update.callback_query.from_user.username}'
    userId = update.callback_query.from_user.id  # correct userID
    currentUser = backEnd.getUser(userId)
    index = currentUser.listID
    orderList = backEnd.getList(index)
    backEndId = orderList.backEndId

    orderList.unpaid.pop(user_name)
    firebase.db.child("orderLists").child(index).child("unpaid").child(user_name).remove()
    text = orderList.paymentList()

    currentUser.debtList.pop(backEndId)
    firebase.db.child("users").child(userId).child("debtList").child(backEndId).remove()

    BUTTONS = [
        [
            InlineKeyboardButton('Paid', callback_data='135Paid' + str(index)),
        ],
        [
            InlineKeyboardButton("PayLah!", url="https://www.dbs.com.sg/personal/mobile/paylink"),
        ]
    ]
    for value in orderList.updateList.values():
        value.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(BUTTONS)
        )


def unpay(update: Update, context: CallbackContext) -> None:
    user_name = f'{update.callback_query.from_user.username}'
    userId = update.callback_query.from_user.id  # correct userID
    currentUser = backEnd.getUser(userId)
    index = currentUser.listID
    orderList = backEnd.getList(index)
    # an array of orders of user_name
    userOrders = orderList.getOnlyOrder(user_name)
    orderList.unpaid[user_name] = userOrders
    backEndId = orderList.backEndId
    for x in userOrders:
        firebase.db.child("orderLists").child(index).child("unpaid").child(user_name).push(x)

    debtListData = {"listId": currentUser.listID, "type": "order"}
    firebase.db.child("users").child(userId).child("debtList").child(backEndId).set(debtListData)
    currentUser.debtList[backEndId] = debtListData

    text = orderList.paymentList()

    BUTTONS = [
        [
            InlineKeyboardButton('Paid', callback_data='135Paid' + str(index)),
        ],
        [
            InlineKeyboardButton("PayLah!", url="https://www.dbs.com.sg/personal/mobile/paylink"),
        ]
    ]
    for value in orderList.updateList.values():
        value.callback_query.edit_message_text(
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
            InlineKeyboardButton('Remind All', callback_data='135CheckRemind' + str(index))
        ]
    ]
    text = "Who owes you money 😤💵\n\n" + outstandingOrders(currentUser, user_name) + \
           "\nPeople you owe money to 🥺💵\n\n" + outstandingPayments(currentUser, user_name)
    update.message.reply_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(BUTTONS)
    )


def split(update: Update, context: CallbackContext) -> None:
    userId = update.message.chat.id
    user = backEnd.getUser(userId)
    user.Splitting = True
    update.message.reply_text("What will be the title of your Split List be?")


def splitList(update: Update, context: CallbackContext) -> None:
    userId = update.message.from_user.id
    user = backEnd.getUser(userId)
    global splitListId
    global backEndId
    now = datetime.now()
    stringNow = json.dumps(now, default=str)[1:20]
    Title = user.currentTitle
    phoneNum = user.currentNo
    ownerName = update.message.from_user.username
    splits = SplitList(splitListId, stringNow, backEndId, ownerName, phoneNum, Title)
    backEnd.SplitLists.append(splits)
    data = {"listId": splitListId, "backEndId": backEndId, "timing": stringNow,
            "OwnerName": update.message.from_user.username,
            "phoneNum": user.currentNo, "Title": user.currentTitle, "orderStatus": True}
    firebase.db.child("splitLists").child(splitListId).set(data)
    data = {"backEndId": backEndId, "title": user.currentTitle, "type": "split", "listId": splitListId,
            "timing": stringNow}
    user.creatorLists.append(data)
    firebase.db.child("users").child(userId).child("creatorLists").push(data)
    splits.makeOrdersDict(user.items, user.prices, splitListId)
    index = splitListId
    user.titleList.append(user.currentTitle)
    splitListId += 1
    backEndId += 1
    firebase.db.child("counters").update({"splitListId": splitListId})
    firebase.db.child("counters").update({"backEndId": backEndId})
    user.Splitting = False
    user.currentTitle = ""
    user.currentNo = ""
    user.items = []
    user.prices = []

    keyboard = [
        [
            InlineKeyboardButton('Publish Split List',
                                 switch_inline_query=Title)
        ],
        [
            InlineKeyboardButton('Update', callback_data='135SplitUpdate' + str(index))
        ],
        [
            InlineKeyboardButton('Remind', callback_data='135SplitRemind' + str(index))
        ],
        [
            InlineKeyboardButton('Close List', callback_data='135SplitCloseList' + str(index)),
            InlineKeyboardButton('Open List', callback_data='135SplitOpenList' + str(index))
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        text=backEnd.getSplit(index).contributorsList(),
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )


def contribute(update: Update, context: CallbackContext, item, index) -> None:
    user_name = f'{update.callback_query.from_user.username}'
    userId = update.callback_query.from_user.id  # correct userID
    currentUser = backEnd.getUser(userId)
    List = backEnd.getSplit(index)
    backEndId = List.backEndId
    contributorsArray = List.orders[item][1]
    unpaidArray = List.orders[item][2]
    unpaidUpdateArray = List.orders[item][3]
    # adding contributers into orders and database
    if user_name not in contributorsArray:
        contributorsArray.append(user_name)
        firebase.db.child("splitLists").child(index) \
            .child("orders").child(item).child("contributers").push({"username": user_name})

    else:
        contributorsArray.remove(user_name)
        orders = firebase.db.child("splitLists").child(index).child("orders").child(item) \
            .child("contributers").get()
        for ord in orders.each():
            if ord.val()["username"] == user_name:
                key = ord.key()
                firebase.db.child("splitLists").child(index).child("orders").child(item) \
                    .child("contributers").child(key).remove()

    # adding people into unpaid and database
    if List.ownerName != user_name:
        if user_name not in unpaidArray:
            unpaidArray.append(user_name)
            unpaidUpdateArray.append(currentUser.personalUpdate)
            data = {"user": user_name, "update": currentUser.personalUpdate.to_json()}
            firebase.db.child("splitLists").child(index) \
                .child("orders").child(item).child("unpaid").push(data)
            debtListData = {"listId": currentUser.listID, "type": "split"}
            firebase.db.child("users").child(userId).child("debtList").child(backEndId).set(debtListData)
            currentUser.debtList[backEndId] = debtListData

        else:
            unpaidArray.remove(user_name)
            unpaidUpdateArray.remove(currentUser.personalUpdate)
            orders = firebase.db.child("splitLists").child(index).child("orders").child(item) \
                .child("unpaid").get()
            for ord in orders.each():
                if ord.val()["user"] == user_name:
                    key = ord.key()
                    firebase.db.child("splitLists").child(index).child("orders").child(item) \
                        .child("unpaid").child(key).remove()

    items = List.itemArray()
    itemsKey = []
    buttons = [itemsKey, [
        InlineKeyboardButton('Bot Chat', url=botURL)
    ]]
    for x in items:
        itemsKey.append(InlineKeyboardButton(x, callback_data="135Contribute" + str(index) + "/" + x))
    reply_markup = InlineKeyboardMarkup(buttons)
    text = backEnd.getSplit(index).contributorsList()
    List.addNewUpdate(currentUser.listUpdate, currentUser.listID)
    for value in List.updateList.values():
        value.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup
        )


def updateSplitList(update: Update, context: CallbackContext) -> None:
    userId = update.callback_query.from_user.id
    user = backEnd.getUser(userId)
    index = int(user.listID)
    list = backEnd.getSplit(index)

    keyboard = [
        [
            InlineKeyboardButton('Publish Split List',
                                 switch_inline_query=list.Title)
        ],
        [
            InlineKeyboardButton('Update', callback_data='135SplitUpdate' + str(index))
        ],
        [
            InlineKeyboardButton('Remind', callback_data='135SplitRemind' + str(index))
        ],
        [
            InlineKeyboardButton('Close List', callback_data='135SplitCloseList' + str(index)),
            InlineKeyboardButton('Open List', callback_data='135SplitOpenList' + str(index))
        ]
    ]
    try:
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.callback_query.edit_message_text(
            text=list.contributorsList(),
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    except:
        return


def closedSplitList(update: Update, context: CallbackContext, index) -> None:
    userId = update.callback_query.message.chat.id  # correct userID
    user = backEnd.getUser(userId)
    splitIndex = index
    currList = backEnd.getSplit(splitIndex)
    text = currList.unpaidList()
    title = currList.Title
    items = currList.itemArray()
    itemsKey = []
    buttons = [itemsKey, [InlineKeyboardButton("PayLah!", url="https://www.dbs.com.sg/personal/mobile/paylink")]]
    for x in items:
        itemsKey.append(InlineKeyboardButton("Paid for " + x, callback_data="135SplitPaid" + str(splitIndex) + "/" + x))
    reply_markup = InlineKeyboardMarkup(buttons)
    update.callback_query.message.reply_text("Split List " + "'" + title + "'" + " is now closed")
    for value in currList.updateList.values():
        value.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup
        )


def openSplitList(update: Update, context: CallbackContext, index) -> None:
    userId = update.callback_query.message.chat.id  # correct userID
    currentUser = backEnd.getUser(userId)
    splitIndex = index
    currentList = backEnd.getSplit(splitIndex)
    text = currentList.contributorsList()
    title = currentList.Title
    items = currentList.itemArray()
    itemsKey = []
    buttons = [itemsKey, [
        InlineKeyboardButton('Bot Chat', url=botURL)
    ]]
    for x in items:
        itemsKey.append(InlineKeyboardButton(x, callback_data="135Contribute" + str(splitIndex) + "/" + x))
    reply_markup = InlineKeyboardMarkup(buttons)
    update.callback_query.message.reply_text("Split List " + "'" + title + "'" + "is now opened")
    for value in currentList.updateList.values():
        print(value.callback_query)
        value.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup
        )


def splitPaid(update: Update, context: CallbackContext, item, index) -> None:
    user_name = f'{update.callback_query.from_user.username}'
    userId = update.callback_query.from_user.id  # correct userID
    List = backEnd.getSplit(index)
    currItem = List.orders[item]
    unpaidList = currItem[2]
    unpaidUpdateList = currItem[3]
    counter = 0
    for x in unpaidList:
        if x == user_name:
            break
        counter += 1
    try:
        unpaidList.remove(user_name)
    except ValueError:
        return
    unpaidUpdateList.pop(counter)
    unpay = firebase.db.child("splitLists").child(index).child("orders").child(item).child("unpaid").get()
    for un in unpay.each():
        if un.val()["user"] == user_name:
            firebase.db.child("splitLists").child(index).child("orders") \
                .child(item).child("unpaid").child(un.key()).remove()
            break
    text = List.unpaidList()
    title = List.Title
    items = List.itemArray()
    itemsKey = []
    buttons = [itemsKey, [InlineKeyboardButton("PayLah!", url="https://www.dbs.com.sg/personal/mobile/paylink")]]
    for x in items:
        itemsKey.append(InlineKeyboardButton("Paid for " + x, callback_data="135SplitPaid" + str(index) + "/" + x))
    reply_markup = InlineKeyboardMarkup(buttons)

    for value in List.updateList.values():
        value.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup
        )


def splitUnpay(update: Update, context: CallbackContext, item, index) -> None:
    user_name = f'{update.callback_query.from_user.username}'
    userId = update.callback_query.from_user.id  # correct userID
    user = backEnd.getUser(userId)
    List = backEnd.getSplit(index)
    currItem = List.orders[item]
    unpaidList = currItem[2]
    unpaidUpdateList = currItem[3]
    unpaidList.append(user_name)
    unpaidUpdateList.append(user.personalUpdate)
    data = {"user": user_name, "update": user.personalUpdate.to_json()}
    firebase.db.child("splitLists").child(index).child("orders").child(item).child("unpaid").push(data)
    text = List.unpaidList()
    title = List.Title
    items = List.itemArray()
    itemsKey = []
    buttons = [itemsKey, [InlineKeyboardButton("PayLah!", url="https://www.dbs.com.sg/personal/mobile/paylink")]]
    for x in items:
        itemsKey.append(InlineKeyboardButton("Paid for " + x, callback_data="135SplitPaid" + str(index) + "/" + x))
    reply_markup = InlineKeyboardMarkup(buttons)

    for value in List.updateList.values():
        value.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup
        )


def remindall(update: Update, context: CallbackContext) -> None:
    userId = update.callback_query.from_user.id
    currentUser = backEnd.getUser(userId)
    remindeveryone(currentUser)
    update.callback_query.message.reply_text("They have all been reminded!")


def remindorder(update: Update, context: CallbackContext, index) -> None:
    userId = update.callback_query.from_user.id
    currentUser = backEnd.getUser(userId)
    order = backEnd.getList(index)
    if len(order.unpaid) != 0:
        currentUser.remindthisorder(order)
        update.callback_query.message.reply_text("Everyone that owes you money on " + order.Title +
                                                 " has been reminded")
    else:
        update.callback_query.message.reply_text("No one owes you money on " + order.Title + "!")


def remindsplit(update: Update, context: CallbackContext, index) -> None:
    userId = update.callback_query.from_user.id
    currentUser = backEnd.getUser(userId)
    splitlist = backEnd.getSplit(index)
    if splitlist.isDebt():
        currentUser.remindthissplit(splitlist)
        update.callback_query.message.reply_text("Everyone that owes you money on " + splitlist.Title +
                                                 " has been reminded")
    else:
        update.callback_query.message.reply_text("No one owes you money on " + splitlist.Title + "!")


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
    try:
        global listId
        global splitListId
        global backEndId
        listId = firebase.db.child("counters").get().val()["listId"]
        splitListId = firebase.db.child("counters").get().val()["splitListId"]
        backEndId = firebase.db.child("counters").get().val()["backEndId"]
    except TypeError:
        data = {"listId": 0, "splitListId": 0, "backEndId": 0}
        firebase.db.child("counters").set(data)

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
