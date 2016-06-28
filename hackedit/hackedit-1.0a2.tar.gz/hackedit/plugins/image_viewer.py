"""
This plugin adds an image view to the IDE.
"""
import mimetypes

from PyQt5 import QtCore, QtGui, QtWidgets

from hackedit.api import plugins


# add missing image mimetypes
mimetypes.add_type('image/bmp', '.bmp')
mimetypes.add_type('image/x-icon', '.ico')


class ImageViewer(plugins.EditorPlugin):
    """
    This plugin add image viewing capabilities to the IDE.
    """
    @staticmethod
    def get_editor_class():
        return _ImageViewer


class _Viewer(QtWidgets.QScrollArea):
    """
    Combines a QLabel and QScrollArea to display an image.
    Adapted from http://qt.developpez.com/doc/4.7/widgets-imageviewer/
    """
    def __init__(self):
        super().__init__()
        self.scaleFactor = 0.0
        self.imageLabel = QtWidgets.QLabel()
        # self.imageLabel.setBackgroundRole(QtGui.QPalette.Base)
        self.imageLabel.setSizePolicy(
            QtWidgets.QSizePolicy.Ignored,
            QtWidgets.QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        self.setBackgroundRole(QtGui.QPalette.Dark)
        self.setWidget(self.imageLabel)
        self.center_label()

    def zoom_in(self):
        self.scale_image(1.25)

    def zoom_out(self):
        self.scale_image(0.8)

    def normal_size(self):
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0

    def fit_to_window(self):
        fit_to_window = self.fitToWindowAct.isChecked()
        self.setWidgetResizable(fit_to_window)
        if not fit_to_window:
            self.normalSize()
        self.updateActions()

    def scale_image(self, factor):
        self.scaleFactor *= factor
        self.imageLabel.resize(
            self.scaleFactor * self.imageLabel.pixmap().size())

        self._adjust_scrollbar(self.horizontalScrollBar(), factor)
        self._adjust_scrollbar(self.verticalScrollBar(), factor)

        self.center_label()
        QtCore.QTimer.singleShot(33, self.center_label)
        QtCore.QTimer.singleShot(66, self.center_label)

    def center_label(self):
        img_size = self.imageLabel.size()
        sa_size = self.size()
        x = (sa_size.width() - img_size.width()) / 2
        if x < 0:
            x = 0.0
        y = (sa_size.height() - img_size.height()) / 2
        if y < 0:
            y = 0.0
        if x or y:
            self.imageLabel.move(x, y)

    def paintEvent(self, event):
        self.center_label()
        super().paintEvent(event)

    def wheelEvent(self, event):
        super().wheelEvent(event)
        self.center_label()

    @staticmethod
    def _adjust_scrollbar(scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value() +
                           ((factor - 1) * scrollBar.pageStep()/2)))


class _FileLoader:
    """
    Mimics the FileManager API of pyqode.
    """
    def __init__(self, viewer, infos):
        self.viewer = viewer
        self.infos = infos
        self.path = ''

    def open(self, path, **__):
        def sizeof_fmt(num, suffix='B'):
            """
            Returns human readable size

            Taken from:

            http://stackoverflow.com/questions/1094841/reusable-library-to-get-
            human-readable-version-of-file-size
            """
            for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
                if abs(num) < 1024.0:
                    return "%3.2f%s%s" % (num, unit, suffix)
                num /= 1024.0
            return "%.2f%s%s" % (num, 'Yi', suffix)

        self.path = path
        image = QtGui.QImage(path)
        if image.isNull():
            QtWidgets.QMessageBox.information(
                self.viewer, _("Image viewer"),
                _("Failed to load image %r.") % path)
            return

        self.viewer.imageLabel.setPixmap(QtGui.QPixmap.fromImage(image))
        self.viewer.scaleFactor = 1.0
        self.viewer.center_label()
        self.viewer.normal_size()

        w, h = image.size().width(), image.size().height()
        size = sizeof_fmt(image.byteCount())
        ext = QtCore.QFileInfo(path).suffix().upper()
        depth = image.depth()

        self.infos.setText(_('%dx%d %s (%d-bit color) %s') %
                           (w, h, ext, depth, size))

    def save(self, *_):
        pass


class _ImageViewer(QtWidgets.QWidget):
    """
    Mimics the CodeEdit interface to display image files.
    """
    mimetypes = [
        'image/png',
        'image/tiff',
        'image/gif',
        'image/bmp',
        'image/x-icon',
        'image/jpeg',
        'image/tga',
        'image/x-targa'
    ]

    # compatibility with pyqode.core.api.CodeEdit
    dirty_changed = QtCore.pyqtSignal(bool)
    dirty = False

    def __init__(self, parent=None, **__):
        super().__init__(parent)
        self.title = ''
        # Setup viewer
        self._viewer = _Viewer()
        # Setup toolbar widget
        self._toolbar = QtWidgets.QWidget()
        hlayout = QtWidgets.QHBoxLayout()
        self._bt_zoom_in = QtWidgets.QPushButton()
        self._bt_zoom_in.setIcon(QtGui.QIcon.fromTheme('zoom-in'))
        self._bt_zoom_in.setToolTip(_('Zoom in'))
        self._bt_zoom_in.clicked.connect(self._viewer.zoom_in)
        hlayout.addWidget(self._bt_zoom_in)
        self._bt_zoom_out = QtWidgets.QPushButton()
        self._bt_zoom_out.setIcon(QtGui.QIcon.fromTheme('zoom-out'))
        self._bt_zoom_out.setToolTip(_('Zoom out'))
        self._bt_zoom_out.clicked.connect(self._viewer.zoom_out)
        hlayout.addWidget(self._bt_zoom_out)
        self._bt_zoom_original = QtWidgets.QPushButton()
        self._bt_zoom_original.setIcon(QtGui.QIcon.fromTheme('zoom-original'))
        self._bt_zoom_original.setToolTip(_('Original size'))
        self._bt_zoom_original.clicked.connect(self._viewer.normal_size)
        hlayout.addWidget(self._bt_zoom_original)
        hlayout.addSpacerItem(QtWidgets.QSpacerItem(
            20, 20, QtWidgets.QSizePolicy.Expanding))
        self._infos = QtWidgets.QLabel()
        hlayout.addWidget(self._infos)
        self._toolbar.setLayout(hlayout)

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(self._toolbar)
        vlayout.addWidget(self._viewer)
        self.setLayout(vlayout)
        self.file = _FileLoader(self._viewer, self._infos)

    def setDocumentTitle(self, title):
        # compatibility with pyqode.core.api.CodeEdit
        self.title = title

    def documentTitle(self):
        # compatibility with pyqode.core.api.CodeEdit
        return self.title

    def horizontalScrollBar(self):
        # compatibility with pyqode.core.api.CodeEdit
        return self._viewer.horizontalScrollBar()

    def wheelEvent(self, *args):
        pass

    def split(self):
        viewer = _ImageViewer()
        viewer.file.open(self.file.path)
        return viewer
