import firebase
class OrderList:

    def __init__(self, listId, timing, backEndId, ownerName, phoneNum, Title):
        self.listId = listId
        self.backEndId = backEndId
        self.timing = timing[1:20]
        self.ownerName = ownerName
        self.phoneNum = phoneNum
        self.Title = Title
        self.orderId = 0
        #chat instance key, update value
        self.updateList = {}
        self.orders = []
        self.unpaid = {}
        self.unpaidUpdate = {}
        self.type = "order"
        self.orderStatus = True
        self.canUpdate = False
        self.counter = 0


    def getCheckList(self):
        text = ""
        index = 1
        for x,y in self.unpaid.items():
            for v in y:
                text += "\n" + str(index) + ") " + x + " - " + v["order"]
                index += 1
        return text

    def fullList(self):
        warning = "If this is your first time using the bot, before doing anything, click the bot chat button " + \
                  "followed by the Start button. Then head back to this chat to start using the buttons below!!\n\n"
        text = warning + "Collating orders for " + self.Title + "! \nTransfer to " + self.phoneNum + "\n\n\nOrders:"
        for i in range(len(self.orders)):
            text = text + "\n" + str(i + 1) + ") " + self.orders[i]["user"] + " - " + self.orders[i]["order"]
        return text

    def paymentList(self):
        text = "Order closed! \nTransfer " + self.phoneNum + " for " + \
               self.Title + "! \n\n\nOrders will be removed once you click the Paid button: "
        for k, v in self.unpaid.items():
            for x in v:
                text += "\n" + k + " - " + x["order"]
        return text

    def getCheckOrder(self, name):
        text = ""
        orderArray = self.unpaid[name]
        if orderArray is None:
            return "no such order"
        for x in orderArray:
            text += name + " - " + x.orderName + "\n"
        return text

    def getOrder(self, name):
        try:
            self.orders[0]
        except KeyError:
            return "no such order"


    def getOnlyOrder(self, name):
        arr = []
        for x in self.orders:
            if x["user"] == name:
                arr.append(x)
        return arr

    def paidStatus(self, username):
        if username in self.unpaid:
            return True
        else:
            return False

    def addNewUpdate(self, update, index):
        if update.callback_query.chat_instance not in self.updateList:
            self.updateList[update.callback_query.chat_instance] = update
            firebase.db.child("orderLists").child(index).child("updateList")\
                .set({update.callback_query.chat_instance: update.to_json()})

    def checkItems(self, item):
        for k in self.items.keys():
            if item == k:
                return True
        return False

    def giveIndex(self):
        self.counter += 1
        return self.counter

    #takes in username and return a text with all the users order
    def indivOrders(self, user_name):
        text = ""
        orderArray = self.orderArray(user_name)
        for x in range(len(orderArray)):
            text += str(x + 1) + ": " + orderArray[x] + "\n"
        return text

    def getTheOrder(self, orderId):
        for x in self.orders:
            if x.orderId == orderId:
                return x
        else:
            return "order does not exist"

    #takes in an order and return the index in the order list array
    def getArrayIndex(self, order):
        for x in range(len(self.orders)):
            if self.orders[x] == order:
                return x + 1

    #takes in an orderId retrun the Order with that id
    def getOrderID(self, id):
        for x in self.orders:
            if x.orderId == int(id):
                return x

    #takes in a username and return boolean value of whether the user's order is in the list
    def isOrder(self, username):
        for x in self.orders:
            if x["user"] == username:
                return True
        return False

    #takes in a username and return an array of users order
    def orderArray(self, username):
        ret = []
        for x in self.orders:
            if x["user"] == username:
                ret.append(x["order"])
        return ret

    def idArray(self, username):
        ret = []
        for x in self.orders:
            if x["user"] == username:
                ret.append(x["orderId"])
        return ret

    #takes in an orderId and return order name
    def getName(self, orderId):
        for x in self.orders:
            if x["orderId"] == int(orderId):
                return x["order"]

    #takes in a new order and change it with the old one
    def changeOrder(self, edited, orderId):
        for x in self.orders:
            if x["orderId"] == int(orderId):
                x["order"] = edited

    def getRid(self, orderId):
        counter=0
        for x in self.orders:
            if x["orderId"] == int(orderId):
                self.orders.pop(counter)
            counter+=1

