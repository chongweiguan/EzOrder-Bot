class backEnd:
    def __init__(self, OrderLists, CheckLists, SplitList):
        self.OrderLists = OrderLists
        self.CheckLists = CheckLists
        self.SplitLists = SplitList
        self.Ordering = False
        self.Checking = False
        self.Splitting = False
        self.Adding = False

    def getOrderIndex(self, title):
        for i in range(len(self.OrderLists)):
            if title == self.OrderLists[i].Title:
                return i
        return len(self.OrderLists)
