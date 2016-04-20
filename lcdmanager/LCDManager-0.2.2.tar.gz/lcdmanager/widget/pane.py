#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Widget - pane"""
from builtins import range  # pylint: disable=I0011,W0622
import lcdmanager.abstract.widget as widget
import lcdmanager.manager as manager


class Pane(widget.Widget):
    """Pane widget"""
    def __init__(self, pos_x, pos_y, name=None, visibility=True):
        widget.Widget.__init__(self, pos_x, pos_y, name, visibility)
        self.widgets = []

    def render(self):
        """return view array"""
        output = []
        for item in self.widgets:
            if not item.visibility:
                continue
            view = item.render()
            offset_y = item.position['y']
            for line in view:
                if offset_y >= len(output):
                    for _ in range(0, offset_y - len(output) + 1):
                        output.append('')

                if len(output[offset_y]) >= item.position['x']:
                    output[offset_y] = \
                        output[offset_y][0:item.position['x']] + line
                else:
                    output[offset_y] = output[offset_y] + \
                        line.rjust(
                            item.position['x'] +
                            len(line) - len(output[offset_y]),
                            manager.TRANSPARENCY
                        )

                offset_y += 1

        return self._crop_to_display(output)

    def add_widget(self, item):
        """add widget to pane"""
        self.widgets.append(item)
        self.recalculate_width()
        self.recalculate_height()

    def get_widget(self, name):
        """get widget from pane or None"""
        for item in self.widgets:
            if item.name == name:
                return item

        return None

    def recalculate_width(self):
        """recalculate width"""
        if self.autowidth:
            self.width = self._calculate_width()
            self.autowidth = True

    def recalculate_height(self):
        """recalculate height"""
        if self.autoheight:
            self.height = self._calculate_height()
            self.autoheight = True

    def _calculate_width(self):
        """calculate longest row in dictionary"""
        return max([item.width + item.position['x'] for item in self.widgets])

    def _calculate_height(self):
        """calculate height"""
        return max([item.height + item.position['y'] for item in self.widgets])

    def _crop_to_display(self, output):
        """prepare text to display by cropping it"""
        rows = [label[0:self.width].ljust(
            self.width, manager.TRANSPARENCY) for label in output]
        for _ in range(len(rows), self.height):
            rows.append(manager.TRANSPARENCY.ljust(self.width))

        return rows
