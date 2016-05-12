class SelectionBox:

    def __init__(self, canvas):
        self.canvas = canvas
        self.id = 0
        self.coords0 = None

    def delete(self):
        if self.id:
            self.canvas.delete(self.id)
            self.id = 0
            self.coords0 = None

    def new(self, x, y):
        self.delete()
        self.id = self.canvas.create_rectangle(x, y, x + 1, y + 1)
        self.coords0 = [x, y]

    @property
    def coords(self):
        return self.canvas.coords(self.id)

    def update(self, x, y):
        coords = self.coords0 + [x, y]
        self.canvas.coords(self.id, *coords)
