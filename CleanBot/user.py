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
        self.currentTitle = ""
        self.currentNo = ""
        self.items = []
        self.prices = []
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
        self.addingPrice = False

    def isAdding(self):
        return self.Adding

    def outstandingOrders(self):
        text = ""
        for i in range(len(self.creatorLists)):
            list = self.creatorLists[i]
            if list.type == "order":
                if len(self.creatorLists[i].unpaid) != 0:
                    text = text + self.creatorLists[i].getCheckList() + "\n"
            else:
                #go through each item
                if list.isDebt():
                    text = text + list.Title + "\n"
                    for j, k in list.items.items():
                        if len(k[2]) != 0:
                            text = text + list.getCheckList(j, k[2])
                    text = text + "\n"
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
            list = orderLists[i]
            if list.type == "order":
                if name in orderLists[i].unpaid.keys():
                    text = text + orderLists[i].ownerName + " for " + orderLists[i].Title + "\n" + orderLists[i].getOrder(name)
            else:
                if list.isOwe(name):
                    text = text + list.ownerName + " for " + list.Title + "\n"
                    for k, v in list.items.items():
                        if name in v[2]:
                            text = text + list.outOrder(name, k)

        return text

    def isRepeated(self, item):
        for x in self.items:
            if item in self.items:
                return True
        return False