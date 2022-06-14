from OrderList import OrderList


class User:
    def __init__(self, userId):
        self.userId = userId
        self.memberLists = {}
        self.creatorLists = []
        self.titleList = []
        self.listID = 0
        self.listUpdate = ''
        self.Adding = False
        self.Ordering = False
        self.addingCommand = False
        self.Deleting = False
        self.deletingCommand = False

    def isAdding(self):
        return self.Adding
