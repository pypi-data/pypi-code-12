#!/usr/bin/python3
# -*- coding: utf-8 -*-

import math

class TableHelper:
    def __init__(self, width=80):
        self.width = width
        self.headers = []
        self.data_set = []
        self.column_width = 0

    def add_column(self, title):
        self.headers.append(title)

    def display(self):
        pass

    def print_header(self):
        column_width = ((self.width ) / len(self.headers))
        print(column_width)
        column_width = int(column_width)
        print("+" + str((self.width) * "-") + "+")
        for header in self.headers:
            print("|" + header.center(column_width), end='')
        print("|")
        print("+" + str((self.width) * "-") + "+")


    def add_column(self, title):
        self.headers.append(title)
        if self.width % len(self.headers) != 0:
            self.width += len(self.headers) - (self.width % len(self.headers))
        self.column_width = int(self.width / len(self.headers))

    def set_data(self, dataset):
        self.data_set = dataset
        for line in self.data_set:
            if len(line) < len(self.headers):
                for i in range(0, len(self.headers) - len(line)):
                    line.append(" ")

    def display(self):
        self.print_header()
        for line in self.data_set:
            self.print_data_line(line)

    def print_data_line(self, data_line):
        for item in data_line:
            print("|" + str(item).center(self.column_width-1), end="")
        print(" |")
        self.print_line_separator()

    def print_header(self):
        self.print_line_separator()
        self.print_data_line(self.headers)

    def print_line_separator(self):
        print("+" + str(self.width * "-") + "+")

