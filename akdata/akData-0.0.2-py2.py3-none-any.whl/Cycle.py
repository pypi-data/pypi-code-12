
class Cycle(object):
    """
    An object with a next method that will cycle through a list of items with each call.
    """
    def __init__(self,items):
        self.items=items
        self.index=0
        self.itemsLength=len(items)


    def next(self):
        i=self.items[self.index%self.itemsLength]
        self.index+=1
        return i
