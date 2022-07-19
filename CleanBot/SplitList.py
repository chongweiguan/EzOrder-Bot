class SplitList:

    def __init__(self, listId, timing, backEndId):
        self.listId = listId
        self.backEndId = backEndId
        self.ownerName = ""
        self.phoneNum = ""
        self.Title = ""
        self.groupChatUpdate = ''
        # key is item, value is [price, contributors, unpaid]
        self.items = {}
        self.type = "split"
        self.timing = timing[1:20]
        self.addPrice = False
        self.orderStatus = True
        self.canUpdate = False

    def makeItemsDict(self, userItems, userPrices):
        for (x, y) in zip(userItems, userPrices):
            self.items[x] = [y, [], [], []]

    def addItem(self, item):
        price = ""
        contributors = []
        unpaid = []
        unpaidupdate = []
        self.items[item] = [price,contributors, unpaid, unpaidupdate]

    def contributorsList(self):
        text = "Please indicate the items that you will be contributing for '" + \
            self.Title + "'!\n\n"

        keys = []
        vals = []
        for key in self.items.keys():
            keys.append(key)
        for val in self.items.values():
            vals.append(val)

        for i in range(len(keys)):
            text = text + keys[i] + " $" + self.getPrice(keys[i]) +":\n"
            for j in range(len(vals[i][1])):
                text = text + vals[i][1][j] + "\n"
            text = text + "\n"

        text = text + "\n"
        return text

    def itemArray(self):
        items = []
        for key in self.items.keys():
            items.append(key)
        return items

    def contributorsArray(self,key):
        people = []
        for val in self.items[key][1]:
            people.append(val)
        return people

    def unpaidArray(self, key):
        people = []
        for val in self.items[key][2]:
            people.append(val)
        return people

    def getpersonalupdatearray(self, item):
        return self.items[item][3]

    def getLatestItem(self):
        itemsArray = self.itemArray()
        length = len(itemsArray)
        itemKey = itemsArray[length - 1]
        return self.items[itemKey]

    def getPrice(self, key):
        item = self.items[key]
        return item[0]

    def splitPrice(self, cost, numofPeople):
        if numofPeople == 0:
            return "0"
        return round(cost/numofPeople, 2)


    def unpaidList(self):
        text = "Split List is closed!\nTransfer " + self.phoneNum + ' for ' + self.Title

        keys = []
        vals = []
        for key in self.items.keys():
            keys.append(key)
        for val in self.items.values():
            vals.append(val)
        for i in range(len(keys)):
            numofContributors = len(self.contributorsArray(keys[i]))
            cost = float(self.getPrice(keys[i]))
            #ALLS GOOD TILL HERE
            splitPrice = self.splitPrice(cost, numofContributors)
            text = text + "\n\n$" + str(splitPrice) + " for " + keys[i] + ":\n"
            for j in range(len(vals[i][2])):
                text = text + vals[i][2][j] + "\n"
        text = text + "\n"
        return text

    def isEmpty(self):
        firstValue = list(self.items.values())[0]
        contributors = firstValue[1]
        return not contributors

    def getOrder(self, name, item):
    # iterate through the key first
        for i in self.items.keys():
            if i == item:
                for j in self.items[item][1]:
                    if name == j:
                        return "" + name + " - " + item + "\n"
                    else:
                        return "No user"
            else:
                return "No item"

    def getCheckList(self, item, unpaid):
        text = ""
        for i in unpaid:
            text = text + i + " - " + item + "\n"
        return text

    #check if this split list has any item with a debt
    def isDebt(self):
        for k in self.items.values():
            if len(k[2]) != 0:
                return True
            else:
                return False

    #check if name argument owes any money in the split list
    def isOwe(self, name):
        for k in self.items.values():
            for x in k[2]:
                if x == name:
                    return True
        return False

    def outOrder(self, name, item):
        return "" + name + " - " + item + "\n"