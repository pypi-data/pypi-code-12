#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
Generator of histology report

"""
import logging
logger = logging.getLogger(__name__)

import os
import sys
import argparse
import numpy as np

from imtools import misc
import csv

import pandas as pd
import datetime

# used by gui dialog
# TODO - remove unneded imports
from PyQt4 import QtCore
from PyQt4.QtCore import pyqtSignal, QObject, QRunnable, QThreadPool, Qt
from PyQt4.QtGui import QMainWindow, QWidget, QDialog, QLabel, QFont,\
    QGridLayout, QFrame, QPushButton, QSizePolicy, QProgressBar, QSpacerItem,\
    QCheckBox, QLineEdit, QApplication, QHBoxLayout, QFileDialog, QMessageBox
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import io3d

class HistologyReport:

    def __init__(self, hist_length_range=None, hist_radius_range=None):
        self.data = None
        self.stats = None
        self.hist_length_range = hist_length_range 
        self.hist_radius_range = hist_radius_range 

    def importFromYaml(self, filename):
        data = misc.obj_from_file(filename=filename, filetype='yaml')
        self.data = self.fixData(data)

    def fixData(self, data):
        """
        fix older versions
        """
        if 'General' in data.keys():
            data['general'] = data.pop('General')
        if 'Graph' in data.keys():
            gr =  data.pop('Graph')
            data['graph'] = {'microstructure': gr}

        try:
            data['general']['used_volume_mm3']
            data['general']['used_volume_px']
        except:
            data['general']['used_volume_mm3'] = data['general']['volume_mm3']
            data['general']['used_volume_px'] = data['general']['volume_px']
        try:
            data['general']['surface_density']
        except:
            data['general']['surface_density'] = None
        return data

    def writeReportToYAML(self, filename='hist_report.yaml'):
        logger.debug('write report to yaml')
        misc.obj_to_file(self.stats, filename=filename, filetype='yaml')

    # def prepareReportInformation(self):
    #     data_m = self.stats['Report']['Main']
    #     data_o = self.stats['Report']['Other']
    #     data_g = self.data['general']
    #     # Main
    #     # subdict from
    #     req_keys = ['Vessel volume fraction (Vv)',
    #                 'Surface density (Sv)',
    #                 'Length density (Lv)',
    #                 'Tortuosity', 'Nv', 'Vref']
    #     report_data = extract_subdict(data_m, req_keys)
    #
    #     report_data.update(
    #         extract_subdict(data_o, ["Avg length mm", 'Total length mm','Avg radius mm'])
    #     )
    #     # Other
    #     report_data['Radius histogram values'] = data_o['Radius histogram'][0]
    #     report_data['Radius histogram bins'] = data_o['Radius histogram'][1]
    #     report_data['Radius histogram values'] = data_o['Length histogram'][0]
    #     report_data['Radius histogram bins'] = data_o['Length histogram'][1]
    #     report_data['shape_px'] = "x".join(map(str, data_g['shape_px'])),
    #     report_data['voxelsize_mm'] = "x".join(map(str, data_g['voxel_size_mm'])),
    #     report_data['datetime'] = str(datetime.datetime.now()),
    #     return report_data

    def writeReportToCSV(self, filename='hist_report.csv'):
        """
        obsolete function
        :param filename:
        :return:
        """
        logger.debug('write report to csv')
        data = self.stats['Report']

        with open(filename, 'wb') as csvfile:
            writer = csv.writer(
                csvfile,
                delimiter=';',
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL
            )
            # Main
            writer.writerow([data['Main']['Vessel volume fraction (Vv)']])
            writer.writerow([data['Main']['Surface density (Sv)']])
            writer.writerow([data['Main']['Length density (Lv)']])
            writer.writerow([data['Main']['Tortuosity']])
            writer.writerow([data['Main']['Nv']])
            writer.writerow([data['Main']['Vref']])
            # Other
            writer.writerow([data['Other']['Avg length mm']])
            writer.writerow([data['Other']['Total length mm']])
            writer.writerow([data['Other']['Avg radius mm']])
            writer.writerow(data['Other']['Radius histogram'][0])
            writer.writerow(data['Other']['Radius histogram'][1])
            writer.writerow(data['Other']['Length histogram'][0])
            writer.writerow(data['Other']['Length histogram'][1])
            
    def addResultsRecord(self, label='_LABEL_', datapath="_GENERATED_DATA_", recordfilename='statsRecords.csv'):
        # TODO remove label from function declaration
        logger.debug("Adding Results record to file: "+recordfilename+".*")
        cols = ['label', 'Vv', 'Sv', 'Lv', 'Tort', 'Nv', 'Vref', 'shape', 'voxelsize', 'datetime', 'path',
                'Avg length mm',
                'Total length mm',
                'Avg radius mm',
                'Radius histogram values',
                'Radius histogram bins',
                'Length histogram values',
                'Length histogram bins',
                ]

        data_r_m = self.stats['Report']['Main']
        data_g = self.data['general']
        data_o = self.stats['Report']['Other']
        newrow = [[
            data_r_m['label'], # label,
            data_r_m['Vessel volume fraction (Vv)'],
            data_r_m['Surface density (Sv)'],
            data_r_m['Length density (Lv)'],
            data_r_m['Tortuosity'],
            data_r_m['Nv'],
            data_r_m['Vref'],
            "x".join(map(str, data_g['shape_px'])),
            "x".join(map(str, data_g['voxel_size_mm'])),
            str(datetime.datetime.now()),
            datapath,
            data_o['Avg length mm'],
            data_o['Total length mm'],
            data_o['Avg radius mm'],
            data_o['Radius histogram'][0],
            data_o['Radius histogram'][1],
            data_o['Length histogram'][0],
            data_o['Length histogram'][1],
        ]]
        # data['label']
        df = pd.DataFrame(newrow, columns=cols)
        
        filename = recordfilename
        append = os.path.isfile(filename)
        with open(filename, 'a') as f:
            if append:
                logger.debug('append to file ' + filename)
                df.to_csv(f, header=False)
            else:
                logger.debug('write to file ' + filename)
                df.to_csv(f)

    def generateStats(self, binNum=40):
        # TODO - upravit dokumentaci
        """
        Funkce na vygenerování statistik.

        | Avg length mm: průměrná délka jednotlivých segmentů
        | Avg radius mm: průměrný poloměr jednotlivých segmentů
        | Total length mm: celková délka cév ve vzorku
        | Radius histogram: pole čísel, kde budou data typu:
        |    v poloměru od 1 do 5 je ve vzorku 12 cév, od 5 do 10 je jich 36,
        |    nad 10 je jich 12.
        |    Využijte třeba funkci np.hist()
        | Length histogram: obdoba předchozího pro délky
        """
        # set default label
        report_o = {'label':''}
        report_o.update(self.data['general'])
        self.data['general'] = report_o

        stats = {
            'Main': {
                'Vessel volume fraction (Vv)': '-',
                'Surface density (Sv)': '-',
                'Length density (Lv)': '-',
                'Tortuosity': '-',
                'Nv': '-',
                'Vref': '-',
                # 'label': ''
            },
            'Other': {
                'Avg length mm': '-',
                'Total length mm': '-',
                'Avg radius mm': '-',
                'Radius histogram': None,
                'Length histogram': None
            }
        }

        # Get other stats
        radius_array = []
        length_array = []
        for tree_part in self.data['graph']:
            for key in self.data['graph'][tree_part]:
                # from PyQt4.QtCore import pyqtRemoveInputHook; pyqtRemoveInputHook(); import ipdb; ipdb.set_trace()  # noqa BREAKPOINT 
                length_array.append(self.data['graph'][tree_part][key]['lengthEstimation'])
                radius_array.append(self.data['graph'][tree_part][key]['radius_mm'])

        num_of_entries = len(length_array)
        stats['Other']['Total length mm'] = sum(length_array)
        stats['Other']['Avg length mm'] = stats[
            'Other']['Total length mm'] / float(num_of_entries)
        stats['Other']['Avg radius mm'] = sum(
            radius_array) / float(num_of_entries)

        radiusHistogram = np.histogram(radius_array, bins=binNum)
        stats['Other']['Radius histogram'] = [
            radiusHistogram[0].tolist(), radiusHistogram[1].tolist()]
        lengthHistogram = np.histogram(length_array, bins=binNum)
        stats['Other']['Length histogram'] = [
            lengthHistogram[0].tolist(), lengthHistogram[1].tolist()]

        # get main stats
        stats['Main']['Vref'] = float(self.data['general']['used_volume_mm3'])
        tortuosity_array = []
        for key in self.data['graph']['microstructure']:
            tortuosity_array.append(self.data['graph']['microstructure'][key]['tortuosity'])
        num_of_entries = len(tortuosity_array)
        stats['Main']['Tortuosity'] = sum(
            tortuosity_array) / float(num_of_entries)
        stats['Main']['Length density (Lv)'] = float(
            stats['Other']['Total length mm']) / float(
                self.data['general']['used_volume_mm3'])
        stats['Main']['Vessel volume fraction (Vv)'] = self.data[
            'general']['vessel_volume_fraction']
        stats['Main']['Surface density (Sv)'] = self.data[
            'general']['surface_density']
        stats['Main']['Nv'] = self.data['general']['Nv']
        stats['Main']['label'] = self.data['general']['label']

        # save stats
        self.stats = {'Report': stats}
        logger.debug('Main stats: ' + str(stats['Main']))


class HistologyReportDialog(QDialog):
    def __init__(self, mainWindow=None, histologyAnalyser=None, stats=None):
        """
        histologyAnalyser or stats parameter is required
        """
        self.mainWindow = mainWindow
        self.ha = histologyAnalyser
        self.recordAdded = False

        self.hr = HistologyReport(self.ha.hr_hist_length_range, self.ha.hr_hist_radius_range)
        if stats is None:
            self.hr.data = self.ha.stats
        else:
            self.hr.data = stats
        # add comment tag

        self.hr.generateStats()


        QDialog.__init__(self)
        self.initUI()

        if self.mainWindow is None:
            self.mainWindow = self
            self.resize(800, 600)

        self.mainWindow.setStatusBarText('Finished')

    def setStatusBarText(self,text=""):
        logger.info(text)

    def __on_changed_label(self, str_agg):
        self.hr.stats['Report']['Main']['label'] = str(str_agg)

    def initUI(self):
        self.ui_gridLayout = QGridLayout()
        self.ui_gridLayout.setSpacing(15)

        rstart = 0

        font_info = QFont()
        font_info.setBold(True)
        font_info.setPixelSize(20)
        label = QLabel('Finished')
        label.setFont(font_info)

        self.ui_gridLayout.addWidget(label, rstart + 0, 0, 1, 1)
        rstart +=1

        ### histology report
        report = self.hr.stats['Report']
        report_m = report['Main']
        report_o = report['Other']

        report_label_main = QLabel('Vessel volume fraction (Vv): \t'+str(report_m['Vessel volume fraction (Vv)'])+' [-]\n'
                                +'Surface density (Sv): \t'+str(report_m['Surface density (Sv)'])+' [mm-1]\n'
                                +'Length density (Lv): \t'+str(report_m['Length density (Lv)'])+' [mm-2]\n'
                                +'Tortuosity: \t\t'+str(report_m['Tortuosity'])+' [length/distance]\n'
                                +'Nv: \t\t'+str(report_m['Nv'])+' [mm-3]'
                                )
        report_label_main.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        report_label_other = QLabel('Total vessel length: \t'+str(report_o['Total length mm'])+' [mm]\n'
                                +'Average vessel length: \t'+str(report_o['Avg length mm'])+' [mm]\n'
                                +'Average vessel radius: \t'+str(report_o['Avg radius mm'])+' [mm]\n'
                                +'Vref: \t\t'+str(report_m['Vref'])+' [mm3]'
                                )
        report_label_other.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        # mili -> mikro (becouse mili has to much 0)
        histogram_radius = self.HistogramMplCanvas(report_o['Radius histogram'][0],
                                        (np.array(report_o['Radius histogram'][1])*1000).tolist(),
                                        title='Radius histogram',
                                        xlabel="Blood-vessel radius ["+r'$\mu$'+"m]",
                                        ylabel="Count"
                                        )
        histogram_length = self.HistogramMplCanvas(report_o['Length histogram'][0],
                                        (np.array(report_o['Length histogram'][1])*1000).tolist(),
                                        title='Length histogram',
                                        xlabel="Blood-vessel length ["+r'$\mu$'+"m]",
                                        ylabel="Count"
                                        )

        self.ui_gridLayout.addWidget(report_label_main, rstart + 0, 0, 1, 2)
        self.ui_gridLayout.addWidget(report_label_other, rstart + 0, 2, 1, 2)
        self.ui_gridLayout.addWidget(histogram_radius, rstart + 1, 0, 1, 4)
        self.ui_gridLayout.addWidget(histogram_length, rstart + 2, 0, 1, 4)
        rstart +=3

        ### buttons
        btn_yaml = QPushButton("Write details to YAML", self)
        btn_yaml.clicked.connect(self.writeDetailedYAML)
        btn_csv = QPushButton("Write details to CSV", self)
        btn_csv.clicked.connect(self.writeDetailedCSV)
        btn_rep_yaml = QPushButton("Write report to YAML", self)
        btn_rep_yaml.clicked.connect(self.writeReportYAML)
        # btn_rep_csv = QPushButton("Write report to CSV", self)
        # btn_rep_csv.clicked.connect(self.btnWriteReportCSV)
        btn_add_row_csv= QPushButton("Write report row to CSV", self)
        btn_add_row_csv.clicked.connect(self.btnAddResultRecordCSV)

        btn_labeled_skeleton = QPushButton("Save labeled skeleton", self)
        btn_labeled_skeleton.clicked.connect(self.btnWriteLabeledSkeleton)
        btn_segmentation= QPushButton("Save segmentation", self)
        btn_segmentation.clicked.connect(self.btnWriteSegmentation)


        # label / comment
        ui_comment_label = QLabel('Label/Comment')
        ui_comment = QLineEdit()
        ui_comment.setText(str(self.hr.stats['Report']['Main']['label']))
        ui_comment.textChanged.connect(self.__on_changed_label)
        self.ui_gridLayout.addWidget(ui_comment_label, rstart + 0, 0)
        self.ui_gridLayout.addWidget(ui_comment, rstart + 1, 0)

        self.ui_gridLayout.addWidget(btn_yaml, rstart + 0, 1)
        self.ui_gridLayout.addWidget(btn_csv, rstart + 1, 1)
        self.ui_gridLayout.addWidget(btn_rep_yaml, rstart + 0, 2)
        self.ui_gridLayout.addWidget(btn_add_row_csv, rstart + 1, 2)
        # self.ui_gridLayout.addWidget(btn_rep_csv, rstart + 1, 1)
        self.ui_gridLayout.addWidget(btn_labeled_skeleton, rstart + 1, 3)
        self.ui_gridLayout.addWidget(btn_segmentation, rstart + 0, 3)
        rstart +=1

        ### Stretcher
        self.ui_gridLayout.addItem(QSpacerItem(0,0), rstart + 0, 0,)
        self.ui_gridLayout.setRowStretch(rstart + 0, 1)
        rstart +=1

        ### Setup layout
        self.setLayout(self.ui_gridLayout)
        self.show()
        
    def getSavePath(self, ofilename="stats", extension="yaml"):
        logger.debug("GetSavePathDialog")
        
        filename = str(QFileDialog.getSaveFileName( self,
        "Save file",
        "./"+ofilename+"."+extension,
        filter="*."+extension))
        
        return filename

    def btnWriteSegmentation(self):
        logger.info("Writing segmentation")
        filename = self.getSavePath("segmentation", "dcm")
        if filename is None or filename == "":
            logger.debug("File save canceled")
            return

        self.mainWindow.setStatusBarText('Saving segmentation image')
        self.ha.save_segmentation(filename)
        # awriter.save_skeleton(filename)

        # self.ha.writeStatsToYAML(filename)
        self.mainWindow.setStatusBarText('Ready')

    def btnWriteLabeledSkeleton(self):
        logger.info("Writing skeleton")
        filename = self.getSavePath("labeled_skeleton", "dcm")
        if filename is None or filename == "":
            logger.debug("File save canceled")
            return
        
        self.mainWindow.setStatusBarText('Saving labeled skeleton image')
        self.ha.save_labeled_skeleton(filename)
            # awriter.save_skeleton(filename)

        # self.ha.writeStatsToYAML(filename)
        self.mainWindow.setStatusBarText('Ready')
        
        # if not self.recordAdded:
        #     self.addResultsRecordWithOthers()

    def btnAddResultRecordCSV(self):
        # TODO change filename
        filename = self.getSavePath("statsRecords", "csv")
        if filename is None or filename == "":
            logger.debug("File save cenceled")
            return
        self.mainWindow.setStatusBarText('Statistics - writing CSV file')
        self.addResultsRecord(recordfilename=filename)
        self.mainWindow.setStatusBarText('Ready')


    def writeDetailedYAML(self):
        """
        write detailed information about every edge into file
        :return:
        """
        logger.info("Writing statistics YAML file")
        filename = self.getSavePath("hist_stats", "yaml")
        if filename is None or filename == "":
            logger.debug("File save cenceled")
            return
        
        self.mainWindow.setStatusBarText('Statistics - writing YAML file')
        self.ha.writeStatsToYAML(filename)
        self.mainWindow.setStatusBarText('Ready')
        
        if not self.recordAdded:
            self.addResultsRecordWithOthers()

    def writeDetailedCSV(self):
        """
        write detailed information about every edge into file
        :return:
        """
        logger.info("Writing statistics CSV file")
        filename = self.getSavePath("hist_stats", "csv")
        if filename is None or filename == "":
            logger.debug("File save cenceled")
            return
        
        self.mainWindow.setStatusBarText('Statistics - writing CSV file')
        self.ha.writeStatsToCSV(filename)
        self.mainWindow.setStatusBarText('Ready')
        
        if not self.recordAdded:
            self.addResultsRecordWithOthers()

    def writeReportYAML(self):
        logger.info("Writing report YAML file")
        filename = self.getSavePath("hist_report", "yaml")
        if filename is None or filename == "":
            logger.debug("File save cenceled")
            return
        
        self.mainWindow.setStatusBarText('Report - writing YAML file')
        self.hr.writeReportToYAML(filename)
        self.mainWindow.setStatusBarText('Ready')
        
        if not self.recordAdded:
            self.addResultsRecordWithOthers()

    def btnWriteReportCSV(self):
        logger.info("Writing report CSV file")
        filename = self.getSavePath("hist_report", "csv")
        if filename is None or filename == "":
            logger.debug("File save cenceled")
            return
        
        self.mainWindow.setStatusBarText('Report - writing CSV file')
        self.hr.writeReportToCSV(filename)
        self.mainWindow.setStatusBarText('Ready')
        
        if not self.recordAdded:
            self.addResultsRecordWithOthers()

    def addResultsRecord(self, recordfilename='statsRecords.csv'):
        # Add results Record
        # if not self.recordAdded:
        label = "GUI mode"
        if self.mainWindow.inputfile is None or self.mainWindow.inputfile == "":
            self.hr.addResultsRecord(label=label, recordfilename=recordfilename)
        else:
            self.hr.addResultsRecord(label=label, datapath=self.mainWindow.inputfile, recordfilename=recordfilename)

    def addResultsRecordWithOthers(self):
        """
        This is obsolete
        :param recordfilename:
        :return:
        """
        # TODO remove this function
        # Add results Record
        # if not self.recordAdded:
        self.addResultsRecord()
        self.recordAdded = True

    class HistogramMplCanvas(FigureCanvas):
        def __init__(self, histogramNumbers, histogramBins, title='', xlabel='', ylabel=''):
            self.histNum =  histogramNumbers
            self.histBins = histogramBins
            self.text_title = title
            self.text_xlabel = xlabel
            self.text_ylabel = ylabel

            # init figure
            fig = Figure(figsize=(5, 2.5))
            self.axes = fig.add_subplot(111)

            # We want the axes cleared every time plot() is called
            self.axes.hold(False)

            # plot data
            self.compute_initial_figure()

            # init canvas (figure -> canvas)
            FigureCanvas.__init__(self, fig)
            #self.setParent(parent)

            # setup
            fig.tight_layout()
            FigureCanvas.setSizePolicy(self,
                                       QSizePolicy.Expanding,
                                       QSizePolicy.Expanding)
            FigureCanvas.updateGeometry(self)

        def compute_initial_figure(self):
            # width of bar
            width = self.histBins[1] - self.histBins[0]

            # start values of bars
            pos = np.round(self.histBins,2)
            pos = pos[:-1]  # end value is redundant

            # heights of bars
            height = self.histNum

            # plot data to figure
            self.axes.bar(pos, height=height, width=width, align='edge')

            # set better x axis size
            xaxis_min = np.round(min(self.histBins),2)
            xaxis_max = np.round(max(self.histBins),2)
            self.axes.set_xlim([xaxis_min,xaxis_max])

            # better x axis numbering
            spacing = width*4
            start = xaxis_min + spacing
            end = xaxis_max + (spacing/10.0)

            xticks_values = np.arange(start,end, spacing)
            xticks_values = np.round(xticks_values, 2)
            xticks = [xaxis_min] + xticks_values.tolist()

            self.axes.set_xticks(xticks)

            # labels
            if self.text_title is not '':
                self.axes.set_title(self.text_title)
            if self.text_xlabel is not '':
                self.axes.set_xlabel(self.text_xlabel)
            if self.text_ylabel is not '':
                self.axes.set_ylabel(self.text_ylabel)

def extract_subdict(adict, keys):
    return {k:adict[k] for k in keys if k in adict}

if __name__ == "__main__":
    # input parser
    parser = argparse.ArgumentParser(
        description='Histology analyser reporter'
    )
    parser.add_argument(
        '-i', '--inputfile',
        default="hist_stats.yaml",
        help='input file, yaml file'
    )
    parser.add_argument(
        '-o', '--outputfile',
        default='hist_report',
        help='output file, yaml,csv file (without file extension)'
    )
    parser.add_argument(
        '--gui', action='store_true',
        help='Run in GUI mode')
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='Debug mode')
    args = parser.parse_args()
    
    logging.basicConfig()
    logger = logging.getLogger()
    logger.setLevel(logging.WARNING)

    if args.debug:
        logger.setLevel(logging.DEBUG)

    # get report
    hr = HistologyReport()
    hr.importFromYaml(args.inputfile)
    
    if args.gui:
        app = QApplication(sys.argv)
        HistologyReportDialog(stats = hr.data)
        sys.exit(app.exec_())
    else:
        hr.generateStats()
        # save report to files
        hr.writeReportToYAML(args.outputfile)
        hr.writeReportToCSV(args.outputfile)
