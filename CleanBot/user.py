from OrderList import OrderList
import backEnd

class User:
    def __init__(self, userId):
        self.userId = userId
        self.debtList = {}
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
        self.deleteConfirm = False
        self.editPart = False
        self.deletePart = False
        self.copyPart = False
        self.remindConfirm = False

    def isAdding(self):
        return self.Adding

    def getunpaidupdateList(self):
        updatearray = []
        for i in range(len(self.creatorLists)):
            list = self.creatorLists[i]
            if list.type == "order":
                if len(self.creatorLists[i].unpaid) != 0:
                    updatearray.append

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

    def remindthisorder(self, list):
        for key in list.unpaid:
            text = "Just a reminder to transfer " + list.ownerName + ": for these orders:\n\n" + \
                   list.Title + ":\n"
            order = list.unpaid[key]
            memberUpdate = list.unpaidUpdate[key]
            for j in range(len(order)):
                text = text + str(j + 1) + ")" + order[j]["order"] + "\n"
            memberUpdate.message.reply_text(text)

    def remindthissplit(self, list):
        personunpaiditems = {}
        for key in list.orders.keys():
            peopleupdatelist = list.orders[key][3]
            for i in range(len(peopleupdatelist)):
                if peopleupdatelist[i] in personunpaiditems:
                    personunpaiditems[peopleupdatelist[i]].append(key)
                else:
                    personunpaiditems[peopleupdatelist[i]] = []
                    personunpaiditems[peopleupdatelist[i]].append(key)

        for key in personunpaiditems:
            text = "Just a reminder to transfer " + list.ownerName + ": for the following items:\n\n" + \
                   list.Title + ":\n"
            for i in range(len(personunpaiditems[key])):
                text = text + str(i + 1) + ")" + personunpaiditems[key][i] + "\n"
            key.message.reply_text(text)
