class OrderList:

    def __init__(self, listId, timing, backEndId):
        self.listId = listId
        self.backEndId = backEndId
        self.timing = timing[1:20]
        self.ownerName = ""
        self.phoneNum = ""
        self.Title = ""
        self.peopleList = []
        #chat instance key, update value
        self.updateList = {}
        self.orders = []
        self.orderSummary = {}
        self.unpaid = {}
        self.type = "order"
        self.groupChatListUpdate = ''
        self.orderStatus = True
        self.addOrder = False
        self.editOrder = False
        self.copyOrder = False
        self.deleteOrder = False
        self.canUpdate = False
        self.counter = 0

    def addName(self, name):
        self.peopleList.append(name)

    def addOrder(self, order):
        self.orders.append(order)

    def getIndex(self, name):
        for i in range(len(self.peopleList)):
            if name == self.peopleList[i]:
                return i

    def getCheckList(self):
        text = self.Title
        keys = []
        vals = []
        for key in self.unpaid.keys():
            keys.append(key)
        for val in self.unpaid.values():
            vals.append(val)
        for i in range(len(keys)):
            for x in range(len(vals[i])):
                text = text + "\n" + keys[i] + " - " + vals[i][x].orderName
        return text

    def fullList(self):
        warning = "If this is your first time using the bot, before doing anything, click the bot chat button " + \
                  "followed by the Start button. Then head back to this chat to start using the buttons below!!\n\n"
        text = warning + "Collating orders for " + self.Title + "! \nTransfer to " + self.phoneNum + "\n\n\nOrders:"
        for i in range(len(self.peopleList)):
            text = text + "\n" + str(i + 1) + ") " + self.peopleList[i] + " - " + self.orders[i].orderName

        return text

    def paymentList(self):
        text = "Order closed! \nTransfer " + self.phoneNum + " for " + \
               self.Title + "! \n\n\nOrders will be removed once you click the Paid button: "
        for k, v in self.unpaid.items():
            for x in v:
                text += "\n" + k + " - " + x.orderName
        return text

    def getCheckOrder(self, name):
        text = ""
        orderArray = self.unpaid[name]
        if orderArray is None:
            return "no such order"
        for x in orderArray:
            text += name + " - " + x.orderName + "\n"
        return text

    def getOrder(self, name):
        text = ""
        orderArray = self.orderSummary[name]
        if orderArray is None:
            return "no such order"
        for x in orderArray:
            text += name + " - " + x.orderName + "\n"
        return text


    def getOnlyOrder(self, name):
        for i in range(len(self.peopleList)):
            if name == self.peopleList[i]:
                return self.orderSummary[name]
        return "no such order"

    def paidStatus(self, username):
        if username in self.unpaid:
            return True
        else:
            return False

    def addNewUpdate(self, update):
        if update.chat_instance not in self.updateList:
            self.updateList[update.chat_instance] = update

    def checkItems(self, item):
        for k in self.items.keys():
            if item == k:
                return True
        return False

    def giveIndex(self):
        self.counter += 1
        return self.counter

    def indivOrders(self, user_name):
        text = ""
        orderArray = self.orderSummary[user_name]
        for x in orderArray:
            text += "Order " + str(x.orderId) + ": " + x.orderName + "\n"
        return text

    def getTheOrder(self, orderId):
        for x in self.orders:
            if x.orderId == orderId:
                return x
        else:
            return "order does not exist"

