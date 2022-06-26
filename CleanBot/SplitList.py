class SplitList:

    def __init__(self, listId, timing, backEndId):
        self.listId = listId
        self.backEndId = backEndId
        self.ownerName = ""
        self.phoneNum = ""
        self.Title = ""
        self.groupChatUpdate = ''
        self.items = {}
        self.timing = timing[1:20]
        self.addPrice = False
        self.orderStatus = True
        self.canUpdate = False

    def addItem(self, item):
        price = ""
        contributors = []
        unpaid = []
        unpaid.append("")
        self.items[item] = [price,contributors,unpaid]

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

    def unpaidArray(self,key):
        people = []
        for val in self.items[key][2]:
            people.append(val)
        return people

    def getLatestItem(self):
        itemsArray = self.itemArray()
        length = len(itemsArray)
        itemKey = itemsArray[length - 1]
        return self.items[itemKey]

    def getPrice(self, key):
        item = self.items[key]
        return item[0]

    def splitPrice(self, cost, numofPeople):
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
            cost = int(self.getPrice(keys[i]))
            #ALLS GOOD TILL HERE
            splitPrice = self.splitPrice(cost, numofContributors)
            text = text + "\n\n$" + str(splitPrice) + " for " + keys[i] + ":"
            for j in range(len(vals[i][2])):
                text = text + vals[i][2][j] + "\n"
        text = text + "\n"
        return text

    def isEmpty(self):
        firstValue = list(self.items.values())[0]
        contributors = firstValue[1]
        return not contributors


