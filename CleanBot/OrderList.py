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
        self.unpaid = {}
        self.type = "order"
        self.groupChatListUpdate = ''
        self.orderStatus = True
        self.addOrder = False
        self.editOrder = False
        self.copyOrder = False
        self.deleteOrder = False
        self.canUpdate = False

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
            text = text + "\n" + keys[i] + " - " + vals[i] + "\n"
        return text

    def fullList(self):
        warning = "If this is your first time using the bot, before doing anything, click the bot chat button " + \
                  "followed by the Start button. Then head back to this chat to start using the buttons below!!\n\n"
        text = warning + "Collating orders for " + self.Title + "! \nPayLah to " + self.phoneNum + "\n\n\nOrders:"
        for i in range(len(self.peopleList)):
            text = text + "\n" + self.peopleList[i] + " - " + self.orders[i]

        return text

    def paymentList(self):
        text = "Order closed! \nTransfer " + self.phoneNum + " for " + \
               self.Title + "! \n\n\nOrders will be removed once you click the Paid button: "
        for k, v in self.unpaid.items():
            text += "\n" + k + " - " + v

        return text

    def getOrder(self, name):
        for i in range(len(self.peopleList)):
            if name == self.peopleList[i]:
                return "" + self.peopleList[i] +" - " + self.orders[i]
        return "no such order"

    def getOnlyOrder(self, name):
        for i in range(len(self.peopleList)):
            if name == self.peopleList[i]:
                return self.orders[i]
        return "no such order"

    def paidStatus(self, username):
        if username in self.unpaid:
            return True
        else:
            return False

    def addNewUpdate(self, update):
        if update.chat_instance not in self.updateList:
            self.updateList[update.chat_instance] = update


