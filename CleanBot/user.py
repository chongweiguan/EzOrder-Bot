from OrderList import OrderList


class User:
    def __init__(self, userId):
        self.userId = userId
        self.memberLists = {}
        self.creatorLists = []
        self.titleList = []
        self.listID = 0
        self.activeOrder = None
        self.listUpdate = ''
        self.personalUpdate = ''
        self.currentTitle = ""
        self.currentNo = ""
        self.items = []
        self.prices = []
        self.addingCommand = False
        self.editingCommand = False
        self.Adding = False
        self.Ordering = False
        self.Deleting = False
        self.Editing = False
        self.Copying = False
        self.Splitting = False
        self.addingPrice = False

    def isAdding(self):
        return self.Adding

    def getunpaidupdateList(self):
        updatearray = []
        for i in range(len(self.creatorLists)):
            list = self.creatorLists[i]
            if list.type == "order":
                if len(self.creatorLists[i].unpaid) != 0:
                    updatearray.append

    def remindeveryonetest(self):
        for i in range(len(self.creatorLists)):
            list = self.creatorLists[i]
            if list.type == "order":
                if len(self.creatorLists[i].unpaid) != 0:
                    for key in self.creatorLists[i].unpaid:
                        text = "just a reminder to transfer " + self.creatorLists[i].ownerName + ": for these orders:\n\n" + \
                               self.creatorLists[i].Title + "\n"
                        order = self.creatorLists[i].unpaid[key]
                        memberUpdate = self.creatorLists[i].unpaidUpdate[key]
                        for j in range(len(order)):
                            text = text + str(j+1) + ")" + order[j].orderName + "\n"
                        memberUpdate[0].message.reply_text(text)

            if list.isDebt():
                personunpaiditems = {}
                for key in list.items.keys():
                    peopleupdatelist = list.getpersonalupdatearray(key)
                    for i in range(len(peopleupdatelist)):
                        if peopleupdatelist[i] in personunpaiditems:
                            personunpaiditems[peopleupdatelist[i]].append(key)
                        else:
                            personunpaiditems[peopleupdatelist[i]] = []
                            personunpaiditems[peopleupdatelist[i]].append(key)

                for key in personunpaiditems:
                    text = "just a reminder to transfer " + self.creatorLists[
                        i].ownerName + ": for the following items:\n\n" + \
                           self.creatorLists[i].Title + "\n"
                    for i in range(len(personunpaiditems[key])):
                        text = text + personunpaiditems[key][i] + "\n"
                    key.message.reply_text(text)


    def remindthisorder(self, list):
        for key in list.unpaid:
            text = "just a reminder to transfer " + list.ownerName + ": for these orders:\n\n" + \
                   list.Title + ":\n"
            order = list.unpaid[key]
            memberUpdate = list.unpaidUpdate[key]
            for j in range(len(order)):
                text = text + str(j + 1) + ")" + order[j].orderName + "\n"
            memberUpdate[0].message.reply_text(text)

    def remindthissplit(self, list):
        personunpaiditems = {}
        for key in list.items.keys():
            peopleupdatelist = list.getpersonalupdatearray(key)
            for i in range(len(peopleupdatelist)):
                if peopleupdatelist[i] in personunpaiditems:
                    personunpaiditems[peopleupdatelist[i]].append(key)
                else:
                    personunpaiditems[peopleupdatelist[i]] = []
                    personunpaiditems[peopleupdatelist[i]].append(key)

        for key in personunpaiditems:
            text = "just a reminder to transfer " + self.creatorLists[i].ownerName + ": for the following items:\n\n" + \
                   self.creatorLists[i].Title + ":\n"
            for i in range(len(personunpaiditems[key])):
                text = text + str(i + 1) + ")" + personunpaiditems[key][i] + "\n"
            key.message.reply_text(text)



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
                    text = text + orderLists[i].ownerName + " for " + orderLists[i].Title + "\n" + \
                           orderLists[i].getCheckOrder(name)
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

    def orderStatus(self):
        if self.Adding == True:
            return "Adding"
        elif self.Editing == True:
            return "Editing"
        elif self.Copying == True:
            return "Copying"
        elif self.Deleting == True:
            return "Deleting"