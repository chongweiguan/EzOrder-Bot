from user import User

class backEnd:
    def __init__(self):
        self.OrderLists = []
        self.CheckLists = []
        self.SplitLists = []
        self.userLists = {}
        self.Ordering = False
        self.Checking = False
        self.Splitting = False
        self.Adding = False

    def getOrderIndex(self, title):
        for i in range(len(self.OrderLists)):
            if title == self.OrderLists[i].Title:
                return i
        return len(self.OrderLists)

    def getSplitIndex(self, title):
        for i in range(len(self.SplitLists)):
            if title == self.SplitLists[i].Title:
                return i
        return len(self.SplitLists)

    def listType(self, title):
        for i in range(len(self.SplitLists)):
            if title == self.SplitLists[i].Title:
                return "split"
        for j in range(len(self.OrderLists)):
            if title == self.OrderLists[j].Title:
                return "order"
        return len(self.OrderLists)

    def addUser(self, userId):
        if userId not in self.userLists:
            self.userLists[userId] = User(userId)

    def latestList(self, userId):
        user = self.userLists[userId]
        length = len(user.creatorLists)
        return user.creatorLists[length - 1]

    def getUser(self, userId):
        if userId not in self.userLists:
            return None
        else:
            return self.userLists[userId]

    def isUser(self, userId):
        return userId in self.userLists


    def getCreatorIndex(self, userID):
        for i in range(len(self.CreatorList)):
            if userID == self.CreatorList[i].id:
                return i
