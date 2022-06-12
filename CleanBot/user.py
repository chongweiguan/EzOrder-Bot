class User:
    def __init__(self, id):
        self.id = id
        self.Adding = False

    def isAdding(self):
        return self.Adding

