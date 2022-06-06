class OrderList:
    def __init__(self, phoneNum, Title, peopleList, orderList):
        self.phoneNum = phoneNum
        self.Title = Title
        self.peopleList = peopleList
        self.orders = orderList
        self.addOrder = False
        self.editOrder = False
        self.copyOrder = False
        self.deleteOrder = False

    def addName(self, name):
        self.peopleList.append(name)

    def addOrder(self, order):
        self.orders.append(order)

    def fullList(self):
        text ="Collating orders for " + self.Title + "! \nPayLah to " + self.phoneNum + "\n\n\nOrders:"
        for i in range(len(self.peopleList)):
            text = text + "\n" + self.peopleList[i] + " - " + self.orders[i]

        return text

