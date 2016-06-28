"""
This module contains a dock manager widget and all the classes needed to make
it work.

"""
import logging

from PyQt5 import QtCore, QtWidgets


class VButton(QtWidgets.QPushButton):
    def __init__(self, text, parent, area):
        super(VButton, self).__init__(parent)
        self.area = area
        self.setText(text)
        self.setFlat(True)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.setCheckable(True)
        self.setIconSize(QtCore.QSize(16, 16))

    def _on_clicked(self):
        self.clearFocus()

    def paintEvent(self, *args):
        painter = QtWidgets.QStylePainter(self)
        if self.area == QtCore.Qt.LeftDockWidgetArea:
            painter.rotate(-90)
            painter.translate(-self.height(), 0)
        else:
            painter.rotate(90)
            painter.translate(0, -self.width())
        painter.drawControl(QtWidgets.QStyle.CE_PushButton,
                            self.get_style_options())

    def sizeHint(self):
        size = super(VButton, self).sizeHint()
        size.transpose()
        return size

    def get_style_options(self):
        options = QtWidgets.QStyleOptionButton()
        options.initFrom(self)
        size = options.rect.size()
        size.transpose()
        options.rect.setSize(size)
        if self.isFlat():
            options.features |= QtWidgets.QStyleOptionButton.Flat
        if self.menu():
            options.features |= QtWidgets.QStyleOptionButton.HasMenu
        if self.autoDefault() or self.isDefault():
            options.features |= QtWidgets.QStyleOptionButton.AutoDefaultButton
        if self.isDefault():
            options.features |= QtWidgets.QStyleOptionButton.DefaultButton
        if self.isDown() or (self.menu() and self.menu().isVisible()):
            options.state |= QtWidgets.QStyle.State_Sunken
        if self.isChecked():
            options.state |= QtWidgets.QStyle.State_On
        if not self.isFlat() and not self.isDown():
            options.state |= QtWidgets.QStyle.State_Raised
        options.text = self.text()
        options.icon = self.icon()
        options.iconSize = self.iconSize()
        return options


class HButton(QtWidgets.QPushButton):
    def __init__(self, text, parent):
        super(HButton, self).__init__(parent)
        self.setText(text)
        self.setFlat(True)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.setCheckable(True)
        self.setIconSize(QtCore.QSize(16, 16))


class DockWidgetSideBar(QtWidgets.QToolBar):
    qss = """QToolBar{
    padding: 2px;
    spacing: 6px;
}
QPushButton {
    background-color: transparent;
    border: 1px transparent;
    padding: 5px;
    border-top: 3px transparent black;
    border-radius: 3px;
    outline: none;
}

QPushButton:on {
    background-color: %s;
    color: %s;
    outline: none;
}

QPushButton:hover {
    border: 1px solid %s;
    outline: none;
}"""

    def setup_stylesheet(self):
        self.color = QtWidgets.qApp.palette().highlight().color()
        self.text_color = QtWidgets.qApp.palette().highlightedText().color()
        self.color_hover = self.palette().highlight().color()
        self.setStyleSheet(self.qss % (
            self.color.name(), self.text_color.name(),
            self.color_hover.name()))

    def __init__(self, parent):
        super(DockWidgetSideBar, self).__init__(parent)
        # if a stylesheet has been applied, then the palette color won't be
        # set before the control has returned to the main loop, so we just
        # set the stylesheet on the next loop
        QtCore.QTimer.singleShot(1, self.setup_stylesheet)
        self._insert_widget_action = None
        self.area = None
        self.setMovable(False)
        self.setFloatable(False)
        self._actions = {}
        self.dock_widgets = []
        self.hide()

    def add_dock_widget(self, dock_widget, area, special=False):
        if dock_widget in self._actions:
            return
        title = dock_widget.windowTitle().replace('&', '')
        title = '&%s' % title
        if self.orientation() == QtCore.Qt.Vertical:
            bt = VButton(title, self, area)
        else:
            bt = HButton(title, self)
        bt.setChecked(dock_widget.isVisible())
        dock_widget.visibilityChanged.connect(bt.setChecked)
        bt.toggled.connect(dock_widget.setVisible)
        bt.setIcon(dock_widget.windowIcon())
        if hasattr(self, 'empty_action'):
            if special:
                action = self.addWidget(bt)
                if 'events' in title.lower():
                    self._insert_widget_action = action
            else:
                # put at the beginning
                action = self.insertWidget(self.empty_action, bt)
        else:
            action = self.addWidget(bt)
        self.dock_widgets.append(dock_widget)
        self._actions[dock_widget] = action
        assert isinstance(dock_widget, QtWidgets.QDockWidget)
        dock_widget.visibilityChanged.connect(self._on_dock_visiblity_changed)
        self.show()
        dock_widget.button = bt
        dock_widget.button.action = action

    def remove_dock_widget(self, dock_widget):
        try:
            self.removeAction(self._actions[dock_widget])
            self._actions.pop(dock_widget)
            dock_widget.visibilityChanged.disconnect(
                self._on_dock_visiblity_changed)
            self.dock_widgets.remove(dock_widget)
        except (KeyError, ValueError, RuntimeError):
            _logger().debug('failed to remove dock widget')
        if not self.dock_widgets:
            self.hide()
        else:
            self.show()

    def _on_dock_visiblity_changed(self, visible):
        pass
        if visible and self.area == QtCore.Qt.BottomToolBarArea:
            for dw in self.dock_widgets:
                if dw != self.sender():
                    dw.hide()

    def add_widget(self, widget, first=False, with_separator=True):
        if first:
            action = self.insertWidget(self.actions()[0], widget)
            if with_separator:
                self.insertSeparator(self.actions()[0])
        else:
            if self._insert_widget_action:
                action = self.insertWidget(self._insert_widget_action, widget)
                if with_separator:
                    self.insertSeparator(self._insert_widget_action)
            else:
                action = self.addWidget(widget)
                # if with_separator:
                #     self.addSeparator()
        return action


class DockWidgetsManager(QtCore.QObject):
    def __init__(self, main_window):
        super().__init__()
        self._managers = {}
        self.main_window = main_window
        bar = DockWidgetSideBar(main_window)
        bar.setObjectName('dockManagerLeft')
        bar.setWindowTitle(_('Dock manager left'))
        main_window.addToolBar(QtCore.Qt.LeftToolBarArea, bar)
        bar.area = QtCore.Qt.LeftDockWidgetArea
        self._managers[bar.area] = bar

        bar = DockWidgetSideBar(main_window)
        bar.setObjectName('dockManagerRight')
        bar.setWindowTitle(_('Dock manager right'))
        main_window.addToolBar(QtCore.Qt.RightToolBarArea, bar)
        bar.area = QtCore.Qt.RightToolBarArea
        self._managers[bar.area] = bar

        bar = DockWidgetSideBar(main_window)
        bar.setObjectName('dockManagerBottom')
        bar.setWindowTitle(_('Dock manager bottom'))
        main_window.addToolBar(QtCore.Qt.BottomToolBarArea, bar)
        bar.area = QtCore.Qt.BottomDockWidgetArea
        empty = QtWidgets.QWidget()
        empty.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                            QtWidgets.QSizePolicy.Preferred)
        bar.empty_action = bar.addWidget(empty)
        self._managers[bar.area] = bar

    def add_dock_widget(self, dock_widget, area, special):
        _logger().debug('adding %r to %r', dock_widget, area)
        if area in [QtCore.Qt.LeftDockWidgetArea, QtCore.Qt.RightToolBarArea]:
            dock_widget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea |
                                        QtCore.Qt.RightDockWidgetArea)
        elif area in [QtCore.Qt.BottomDockWidgetArea,
                      QtCore.Qt.TopToolBarArea]:
            area = QtCore.Qt.BottomDockWidgetArea
            dock_widget.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)
        assert isinstance(dock_widget, QtWidgets.QDockWidget)
        dock_widget.dockLocationChanged.connect(
            self._on_dock_location_changed)
        self._managers[area].add_dock_widget(
            dock_widget, area, special=special)

    def add_bottom_widget(self, widget, with_separator, first):
        manager = self._managers[QtCore.Qt.BottomDockWidgetArea]
        return manager.add_widget(widget, first, with_separator)

    def remove_dock_widget(self, dock_widget):
        _logger().debug('removing dock widget: %r' % dock_widget.windowTitle())
        for manager in self._managers.values():
            try:
                manager.remove_dock_widget(dock_widget)
            except KeyError:
                _logger().warn('failed to remove dock widget %r', dock_widget)

    def _on_dock_location_changed(self, area):
        dock = self.sender()
        _logger().debug('dock widget location changed: %r - %r', dock, area)
        if area == QtCore.Qt.LeftDockWidgetArea:
            self._managers[QtCore.Qt.RightToolBarArea].remove_dock_widget(dock)
            self._managers[QtCore.Qt.LeftDockWidgetArea].add_dock_widget(
                dock, area)
        elif area == QtCore.Qt.RightDockWidgetArea:
            self._managers[QtCore.Qt.LeftDockWidgetArea].remove_dock_widget(
                dock)
            self._managers[QtCore.Qt.RightToolBarArea].add_dock_widget(
                dock, area)

    def dock_widgets(self):
        ret_val = []
        for manager in self._managers.values():
            ret_val += manager.dock_widgets
        return ret_val

    def update_style(self):
        for bar in self._managers.values():
            bar.setup_stylesheet()


def _logger():
    return logging.getLogger(__name__)
