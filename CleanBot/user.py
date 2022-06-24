from OrderList import OrderList


class User:
    def __init__(self, userId):
        self.userId = userId
        self.memberLists = {}
        self.creatorLists = []
        self.titleList = []
        self.listID = 0
        self.listUpdate = ''
        self.personalUpdate = ''
        self.Adding = False
        self.Ordering = False
        self.addingCommand = False
        self.Deleting = False
        self.deletingCommand = False
        self.Editing = False
        self.editingCommand = False
        self.Copying = False
        self.copyingCommand = False
        self.Splitting = False

    def isAdding(self):
        return self.Adding

    def outstandingOrders(self):
        text = ""
        for i in range(len(self.creatorLists)):
            if len(self.creatorLists[i].unpaid) != 0:
                text = text + self.creatorLists[i].getCheckList() + "\n"
        return text

    def outstandingPayments(self, name):
        text = ""
        orderIndexes = []
        orderLists = []
        for key in self.memberLists.keys():
            orderIndexes.append(int(key))
        for val in self.memberLists.values():
            orderLists.append(val)
        for i in range(len(orderLists)):
            if name in orderLists[i].unpaid.keys():
                text = text + orderLists[i].ownerName + " for " + orderLists[i].Title + "\n" + orderLists[i].getOrder(name)

        return text


