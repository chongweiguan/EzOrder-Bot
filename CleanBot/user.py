from OrderList import OrderList


class User:
    def __init__(self, userId):
        self.userId = userId
        self.memberLists = {}
        self.creatorLists = []
        self.titleList = []
        self.Adding = False
        self.Ordering = False
        self.addingCommand = False

    def isAdding(self):
        return self.Adding
