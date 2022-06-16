class OrderList:

    def __init__(self, listId):
        self.listId = listId
        self.ownerName = ""
        self.phoneNum = ""
        self.Title = ""
        self.peopleList = []
        self.orders = []
        self.unpaid = {}
        self.groupChatListUpdate = ''
        self.addOrder = False
        self.editOrder = False
        self.copyOrder = False
        self.deleteOrder = False

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
        text = "Collating orders for " + self.Title + "! \nPayLah to " + self.phoneNum + "\n\n\nOrders:"
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


