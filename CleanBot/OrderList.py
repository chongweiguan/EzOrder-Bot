class OrderList:

    def __init__(self, listId, phoneNum, Title, peopleList, orders):
        self.listId = listId
        self.phoneNum = phoneNum
        self.Title = Title
        self.peopleList = peopleList
        self.orders = orders
        self.addOrder = False
        self.editOrder = False
        self.copyOrder = False
        self.deleteOrder = False

    def addName(self, name):
        self.peopleList.append(name)

    def addOrder(self, order):
        self.orders.append(order)

    def fullList(self):
        text = "Collating orders for " + self.Title + "! \nPayLah to " + self.phoneNum + "\n\n\nOrders:"
        for i in range(len(self.peopleList)):
            text = text + "\n" + self.peopleList[i] + " - " + self.orders[i]

        return text

    # function that takes in a userId and returns whether that user.adding is true or false
    # def checkAdding(self, id):
    #     if id in self.usersList == False:
    #         return False
    #     elif not self.usersList[id].Adding:
    #         return False
    #     else:
    #         return True
