"""
eep string search and replace module
"""


class Searcher(object):
    """
    Main searcher class
    """

    def __init__(self, text):
        """
        Initialize eep searcher with given text
        """

        self.text = text
        self.point = 0
        self.mark = 0

    def __repr__(self):
        """
        String representation
        """

        return self.text

    def jump(self, chars):
        """
        Jump point with given number of chars (+ve/-ve)
        """

        self.goto(self.point + chars)

    def goto(self, point):
        """
        Set point to given value
        """

        if point == "end":
            self.point = len(self.text)
        elif point == "start":
            self.point = 0
        else:
            self.point = min(max(0, point), len(self.text))

    def insert(self, snippet):
        """
        Insert given snippet at current point
        """

        self.text = self.text[:self.point] + snippet + self.text[self.point:]
        self.jump(len(snippet))

    def swap_markers(self):
        """
        Swap mark and point
        """

        tmp = self.mark
        self.mark = self.point
        self.point = tmp

    def replace(self, replacement):
        """
        Replace region between current mark and point
        Keep point at its previous relative position
        """

        swapped = False
        region = [self.mark, self.point]
        if self.mark > self.point:
            self.swap_markers()
            swapped = True

        self.text = self.text[:self.mark] + replacement + self.text[
            self.point:]
        self.point = self.mark + len(replacement)
        if swapped:
            self.swap_markers()

    def erase(self):
        """
        Erase region between current mark and point
        """

        self.replace("")

    def search_forward(self, substr):
        """
        Search forward from current point and bind region
        starting with mark, ending with point
        """

        search_mark = self.text.find(substr, self.point)
        if search_mark == -1:
            return False
        else:
            self.mark = search_mark
            self.point = self.mark + len(substr)
            return True

    def search_backward(self, substr):
        """
        Search backward from current point and bind region
        starting with point, ending with mark
        """

        search_mark = self.text.rfind(substr, 0, self.point)
        if search_mark == -1:
            return False
        else:
            self.point = search_mark
            self.mark = self.point + len(substr)
            return True
