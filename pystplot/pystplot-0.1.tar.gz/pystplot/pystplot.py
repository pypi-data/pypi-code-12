import json
import webbrowser
import html_writer

PLOT_FILE = "output.html"

class PlotInfo:
    def __init__(self, name = 'container'):
        self._lines = []
        self.width = 600
        self.height = 400
        self.container_id = name

    def append_line(self, line_object):
        self._lines.append(line_object)

    def get_line_list(self):
        return self._lines

    def get_plot_size(self):
        return {'width': self.width, 'height' : self.height}

    def get_container_info(self):
        return_dict = {'width': self.width,
                       'height' : self.height,
                       'container_id': self.container_id,
                       'plot_list_as_string': self.get_plot_list_as_string()}
        return return_dict

    def get_plot_list_as_string(self):
        return json.dumps(self.get_line_list())


def create_subplot_name( index, rows, cols):
    return 'subplot_'+str(rows) + '_' + str(rows) + '_' + str(index)

def create_subplot(index, rows, cols):
    subplot_name = create_subplot_name(index, rows, cols)
    return PlotInfo(subplot_name)

def create_subplots(rows, cols):
    return [create_subplot(index, rows, cols) for index in range(rows * cols)]


class FigureInfo:
    def __init__(self, rows = 1, cols = 1):
        self._plots = create_subplots(rows, cols)
        self._rows = rows
        self._cols = cols

    def get_plot_info_at(self, index):
        return self._plots[index]

    def get_plot_info_at_subplot(self, subplot_index):
        if(subplot_index) > 0:
            return self._plots[index-1]
        return None

    def rows(self):
        return self._rows

    def cols(self):
        return self._cols

    def no_plots(self):
        return self._rows*self._cols

    def get_plot(self, index):
        return self._plots[index]


fig_info = FigureInfo()
current_plot = 0
do_subplot = False

def subplot(rows, cols, index):
    global do_subplot
    global fig_info
    global current_plot
    current_plot = index - 1
    if not do_subplot:
        fig_info = FigureInfo(rows, cols)
        do_subplot = True

def plot(x_list, y_list, property_string='-'):
    global fig_info
    data_list = html_writer.data_to_flotr_format(x_list, y_list)
    line_object = html_writer.flotr_line_object(data_list, property_string)
    fig_info.get_plot(current_plot).append_line(line_object)

def show():
    html_writer.make_html_file(fig_info, PLOT_FILE)
    webbrowser.open(PLOT_FILE)
