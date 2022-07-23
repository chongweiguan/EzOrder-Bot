import firebase
class SplitList:

    def __init__(self, listId, timing, backEndId, ownerName, phoneNum, Title):
        self.listId = listId
        self.backEndId = backEndId
        self.ownerName = ownerName
        self.phoneNum = phoneNum
        self.Title = Title
        self.groupChatUpdate = ''
        # key is item, value is [price, contributors, unpaid]
        self.updateList = {}
        self.orders = {}
        self.type = "split"
        self.timing = timing[1:20]
        self.addPrice = False
        #to indicate whether list is open or close
        self.orderStatus = True

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

    def contributorsArray(self, key):
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
        if numofPeople == 0:
            return "0"
        return round(cost/numofPeople, 2)


    def unpaidList(self):
        text = "Split List is closed!\nTransfer " + self.phoneNum + ' for ' + self.Title

        keys = []
        vals = []
        for key in self.orders.keys():
            keys.append(key)
        for val in self.orders.values():
            vals.append(val)
        for i in range(len(keys)):
            numofContributors = len(vals[i][1])
            cost = float(vals[i][0])
            splitPrice = self.splitPrice(cost, numofContributors)
            text = text + "\n\n$" + str(splitPrice) + " for " + keys[i] + ":\n"
            for j in range(len(vals[i][2])):
                text = text + vals[i][2][j] + "\n"
        text = text + "\n"
        return text

    def isEmpty(self):
        for x in self.orders.values():
            if not len(x[1]) == 0:
                return False
        return True

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
        for k in self.orders.values():
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

    #from orders take all the items out
    def itemArray(self):
        items = []
        for key in self.orders.keys():
            items.append(key)
        return items

    #fulllist split list version
    def contributorsList(self):
        text = "Please indicate the items that you will be contributing for '" + \
            self.Title + "'!\n\n"

        keys = []
        vals = []
        for key in self.orders.keys():
            keys.append(key)
        for val in self.orders.values():
            vals.append(val)

        for i in range(len(keys)):

            text = text + keys[i] + " $" + vals[i][0] +":\n"
            for j in range(len(vals[i][1])):
                text = text + vals[i][1][j] + "\n"
            text = text + "\n"

        text = text + "\n"
        return text

    def makeOrdersDict(self, userItems, userPrices, splitId):
        for (x, y) in zip(userItems, userPrices):
            self.orders[x] = [y, [], [], []]
            print(self.orders)
            firebase.db.child("splitLists").child(splitId).child("orders").child(x).set({"price": y})

    def addNewUpdate(self, update, index):
        if update.callback_query.chat_instance not in self.updateList:
            self.updateList[update.callback_query.chat_instance] = update
            firebase.db.child("splitLists").child(index).child("updateList")\
                .set({update.callback_query.chat_instance: update.to_json()})

    def paidStatus(self, username):
        for x in self.orders.values():
            if username in x[2]:
                return True
        return False