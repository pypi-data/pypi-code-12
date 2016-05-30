#!/usr/bin/python
# -*- coding: utf-8 -*-
# File: stats.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Stats service

import pygal
from pygal import Config

from .service import Service


class Stats(Service):
    def initialize(self):
        self.get_services()

    def get_html(self, filename):
        fin = open(filename, 'r')
        html = fin.read()
        fin.close()

        return html


    def get_services(self):
        self.sap = self.app.get_service('SAP')

    def build_pie_maincomp(self):
        stats  = self.sap.get_stats()
        CHART_FILE = self.app.get_var('TMP', 'local') + 'chart.svg'
        config = Config()
        config.show_legend = True
        config.print_values = True
        config.print_values_position = 'top'
        config.print_labels = True
        #~ config.dynamic_print_values = True
        config.human_readable = True
        config.fill = True
        #~ chart = pygal.XY(config)
        pie_chart = pygal.HorizontalBar(config)
        pie_chart.title = 'Main components used'
        for key in stats['maincomp']:
            value = stats['maincomp'][key]
            label = "%s (%d)" % (key, value)
            pie_chart.add(label, value)
        pie_chart.render_to_file(CHART_FILE)

        return self.get_html(CHART_FILE)


    def build_pie_categories(self):
        stats  = self.sap.get_stats()
        CHART_FILE = self.app.get_var('TMP', 'local') + 'chart.svg'
        config = Config()
        config.show_legend = True
        config.print_values = True
        config.print_values_position = 'top'
        config.print_labels = True
        #~ config.dynamic_print_values = True
        config.human_readable = True
        config.fill = True
        #~ chart = pygal.XY(config)
        pie_chart = pygal.HorizontalBar(config)
        pie_chart.title = 'By categories'
        for key in stats['cats']:
            value = stats['cats'][key]
            label = "%s (%d)" % (key, value)
            pie_chart.add(label, value)
        pie_chart.render_to_file(CHART_FILE)

        return self.get_html(CHART_FILE)
