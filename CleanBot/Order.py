class Order:
    def __init__(self, orderId, user):
        self.orderId = orderId
        self.user = user
        self.orderName = ""

    def getOrd(self):
        return "" + self.user + " - " + self.orderName

