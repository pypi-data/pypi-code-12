
import sys
import os

from PySide.QtGui import (QWidget, QDialog, QListWidget, QListWidgetItem,
                                QVBoxLayout, QStackedWidget, QListView,
                                QHBoxLayout, QDialogButtonBox, QCheckBox,
                                QMessageBox, QLabel, QLineEdit, QSpinBox,
                                QPushButton, QFontComboBox, QGroupBox,
                                QComboBox, QColor, QGridLayout, QTabWidget,
                                QRadioButton, QButtonGroup, QSplitter,
                                QStyleFactory, QScrollArea,QApplication,QIcon,
                                QDoubleSpinBox,QSplashScreen, QPixmap, 
                                QStatusBar, QMainWindow )
from PySide.QtCore import Qt, QSize, SIGNAL, SLOT, Slot, QThread


class NoDefault:
    pass


class ConfiguratorWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        # Destroying the C++ object right after closing the dialog box,
        # otherwise it may be garbage-collected in another QThread
        # (e.g. the editor's analysis thread in Spyder), thus leading to
        # a segmentation fault on UNIX or an application crash on Windows
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.statusBar().showMessage('Ready')

        self.saveButton = QPushButton(self.tr("Save"))
        self.saveButton.setDefault(True)
        self.quitButton = QPushButton(self.tr("Quit"))
        self.quitButton.setAutoDefault(False)
        buttonBox = QDialogButtonBox()
        buttonBox.addButton(self.saveButton,
                            QDialogButtonBox.ActionRole)
        buttonBox.addButton(self.quitButton, QDialogButtonBox.RejectRole)
        self.connect(self.saveButton, SIGNAL('clicked()'), self.save_file)
        self.connect(self.quitButton, SIGNAL('clicked()'), self.close)

        """
        bbox = QDialogButtonBox(QDialogButtonBox.Apply
                                |QDialogButtonBox.Cancel)
        self.apply_btn = bbox.button(QDialogButtonBox.Apply)
        self.connect(bbox, SIGNAL("accepted()"), SLOT("accept()"))
        self.connect(bbox, SIGNAL("rejected()"), SLOT("reject()"))
        self.connect(bbox, SIGNAL("clicked(QAbstractButton*)"),
                     self.button_clicked)
        """
        self.lineedits = {}
        self.comboboxes = {}
        self.spinboxes = {}
        self.availability_label = None

        self.job_name_widget = self.create_lineedit('Job Name', 'job_name')
        self.job_script_widget = self.create_lineedit('Job Script',
                                                      'job_script')
        self.job_output_widget = self.create_lineedit('Job Output',
                                                      'job_output')
        self.project_name_widget = self.create_lineedit('Project/Account',
                                                        'project_name')
        self.queue_widget = self.create_combobox('Queue', [], 'queues')
        self.availability_label = QLabel('Available:')
        self.num_tasks_widget = self.create_spinbox('Number tasks',
                                                    '', 'ntasks',
                                                    NoDefault, 1, 1, 1,
                                                    'total number of tasks')
        self.task_per_node_widget = self.create_spinbox('Task per node',
                                                        '', 'task_per_node',
                                                        NoDefault, 1, 2, 1,
                                                        'tasks per node')
        self.runtime_widget = self.create_spinbox('Runtime', 'hrs', 'runtime',
                                                  NoDefault, 1, 36, 1,
                                                  'runtime in hrs')
        self.app_script_widget = self.create_combobox('Application Script',
                                                    [('mycluster-zcfd.bsh','mycluster-zcfd.bsh'),
                                                     ('mycluster-paraview.bsh','mycluster-paraview.bsh'),
                                                     ('mycluster-fluent.bsh','mycluster-fluent.bsh')],
                                                    'app_script')

        # hsplitter = QSplitter()
        # hsplitter.addWidget(self.pages_widget)

        btnlayout = QHBoxLayout()
        btnlayout.addStretch(1)
        btnlayout.addWidget(buttonBox)

        vlayout = QVBoxLayout()
        # vlayout.addWidget(hsplitter)

        vlayout.addWidget(self.job_name_widget)
        vlayout.addWidget(self.job_script_widget)
        vlayout.addWidget(self.job_output_widget)
        vlayout.addWidget(self.project_name_widget)
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.queue_widget)
        hlayout.addWidget(self.availability_label)
        vlayout.addLayout(hlayout)
        vlayout.addWidget(self.num_tasks_widget)
        vlayout.addWidget(self.task_per_node_widget)
        vlayout.addWidget(self.runtime_widget)
        vlayout.addWidget(self.app_script_widget)
        vlayout.addSpacing(10)
        vlayout.addLayout(btnlayout)

        self.widget = QWidget()
        self.widget.setLayout(vlayout)

        self.setCentralWidget(self.widget)

        # self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle("MyCluster Job Configurator")

        self.lineedits['job_name'].textChanged.connect(self.job_name_changed)
        self.lineedits['job_script'].textChanged.connect(self.job_script_changed)
        self.lineedits['job_name'].setText('myjob')
        self.lineedits['project_name'].setText('default')
        #self.lineedits['app_script'].setText('myscript.bsh')
        self.comboboxes['app_script'].setEditable(True)
        self.comboboxes['app_script'].lineEdit().editingFinished.connect(self.check_app_script)

        from mycluster import mycluster
        mycluster.init()

        self.init_queue_info()

    def save_file(self):
        from mycluster import mycluster
        if mycluster.scheduler:
            index = self.comboboxes['queues'].currentIndex()
            data = self.comboboxes['queues'].itemData(index)
            jobqueue = data.split(' ')[0]

            index = self.comboboxes['app_script'].currentIndex()
            data = self.comboboxes['app_script'].itemData(index)
            app_script = data.split(' ')[0]

            # Add checks

            mycluster.create_submit(jobqueue,
                                    script_name=self.lineedits['job_script'].text()+'.job',
                                    my_script=app_script,
                                    my_name=self.lineedits['job_name'].text(),
                                    my_output=self.lineedits['job_output'].text()+'.out',
                                    num_tasks=self.spinboxes['ntasks'].value(),
                                    project_name=self.lineedits['project_name'].text(),
                                    wall_clock=self.spinboxes['runtime'].value(),
                                    tasks_per_node=self.spinboxes['task_per_node'].value(),)

    def init_queue_info(self):
        from mycluster import mycluster
        if mycluster.scheduler:
            for q in mycluster.queues():
                # nc = mycluster.scheduler.node_config(q)
                tpn = mycluster.scheduler.tasks_per_node(q)
                avail = mycluster.scheduler.available_tasks(q)
                self.comboboxes['queues'].addItem(q+' max task: '+str(avail['max tasks']),
                                                  q+' '+str(avail['max tasks'])+' '+str(tpn)+ ' '+str(avail['available']))

        self.comboboxes['queues'].currentIndexChanged.connect(self.queue_changed)
        self.queue_changed()

    def queue_changed(self):
        if self.comboboxes['queues'].count():
            index = self.comboboxes['queues'].currentIndex()
            data = self.comboboxes['queues'].itemData(index)
            self.spinboxes['ntasks'].setMaximum(int(data.split(' ')[1]))
            self.spinboxes['task_per_node'].setMaximum(int(data.split(' ')[2]))
            self.spinboxes['task_per_node'].setValue(int(data.split(' ')[2]))
            self.availability_label.setText('Available: ' +
                                            data.split(' ')[3] + ' tasks')

    def job_name_changed(self, text):
        # print 'job name changed'
        self.lineedits['job_script'].setText(text)
        self.lineedits['job_output'].setText(text)

    def job_script_changed(self, text):
        # Check for file exist
        if os.path.isfile(text + '.job'):
            self.statusBar().showMessage('Warning file: ' +
                                         text + '.job already exists')
        else:
            self.statusBar().showMessage('Ready')

    def check_app_script(self):
        text = self.comboboxes['app_script'].lineEdit().text()
        if not os.path.isfile(text):
            self.statusBar().showMessage('Warning file: ' +
                                         text + ' does not exists')
        else:
            self.statusBar().showMessage('Ready')
        pass

    def show_and_raise(self):
        self.show()
        self.raise_()

    def button_clicked(self, button):
        if button is self.apply_btn:
            # Apply button was clicked
            pass

    def create_lineedit(self, text, option, default=NoDefault,
                        tip=None, alignment=Qt.Horizontal):
        label = QLabel(text)
        label.setWordWrap(True)
        edit = QLineEdit()
        layout = QVBoxLayout() if alignment == Qt.Vertical else QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(edit)
        layout.setContentsMargins(0, 0, 0, 0)
        if tip:
            edit.setToolTip(tip)
        self.lineedits[option] = edit
        widget = QWidget(self)
        widget.setLayout(layout)
        return widget

    def create_spinbox(self, prefix, suffix, option, default=NoDefault,
                       min_=None, max_=None, step=None, tip=None):
        if prefix:
            plabel = QLabel(prefix)
        else:
            plabel = None
        if suffix:
            slabel = QLabel(suffix)
        else:
            slabel = None
        spinbox = QSpinBox()
        if min_ is not None:
            spinbox.setMinimum(min_)
        if max_ is not None:
            spinbox.setMaximum(max_)
        if step is not None:
            spinbox.setSingleStep(step)
        if tip is not None:
            spinbox.setToolTip(tip)
        self.spinboxes[option] = spinbox
        layout = QHBoxLayout()
        for subwidget in (plabel, spinbox, slabel):
            if subwidget is not None:
                layout.addWidget(subwidget)
        layout.addStretch(1)
        layout.setContentsMargins(0, 0, 0, 0)
        widget = QWidget(self)
        widget.setLayout(layout)
        return widget

    def create_combobox(self, text, choices, option, default=NoDefault,
                        tip=None):
        """choices: couples (name, key)"""
        label = QLabel(text)
        combobox = QComboBox()
        if tip is not None:
            combobox.setToolTip(tip)
        # combobox.setEditable(True)
        for name, key in choices:
            combobox.addItem(name, key)  # to_qvariant(key))
        self.comboboxes[option] = combobox
        layout = QHBoxLayout()
        for subwidget in (label, combobox):
            layout.addWidget(subwidget)
        layout.addStretch(1)
        layout.setContentsMargins(0, 0, 0, 0)
        widget = QWidget(self)
        widget.setLayout(layout)
        return widget


def _resourcepath(directory):
    '''Returns the path to the resource directory inside the package'''
    modulename = os.path.abspath(__file__)
    return os.path.join(os.path.dirname(modulename), directory)


def main():
    app = QApplication(sys.argv)
    import qdarkstyle
    # setup stylesheet
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    pixmap = QPixmap(os.path.join(_resourcepath('images'), "splash.png"))
    splash = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint)
    splash.setMask(pixmap.mask())
    splash_font = splash.font()
    splash_font.setPixelSize(14)
    splash.setFont(splash_font)
    splash.show()
    splash.showMessage('Initialising...',
                       Qt.AlignBottom | Qt.AlignLeft |
                       Qt.AlignAbsolute,
                       Qt.white)
    app.processEvents()
    """
    for count in range(1, 6):
        splash.showMessage('Processing {0}...'.format(count),
                           Qt.AlignBottom | Qt.AlignLeft,
                           Qt.white)
        QApplication.processEvents()
        QThread.msleep(1000)
    """
    frame = ConfiguratorWindow()

    frame.show_and_raise()
    splash.finish(frame)
    sys.exit(app.exec_())
