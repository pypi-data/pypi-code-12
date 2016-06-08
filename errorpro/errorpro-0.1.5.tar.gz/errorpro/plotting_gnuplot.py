import shlex, subprocess
import tempfile
from IPython.display import Image

# TODO: adjust everything to new structure

def plot(data_sets, functions, save=None, xrange=None, yrange=None, x_label="", y_label=""):

    gp = Gnuplot(data_sets, functions, xrange, yrange, x_label, y_label)

    tmp_folder = tempfile.gettempdir()

    if save is None:
        gp.save("",tmp_folder)
    else:
        gp.save(save, ".")

    return Image(gp.image_file)

# TODO Gnuplot class doesn't make sense anymore

class Gnuplot():
    def __init__(self, data_sets, functions, xrange, yrange, x_label, y_label):
        self.data_sets = data_sets
        self.functions = functions
        self.xrange = xrange
        self.yrange = yrange
        self.x_label = x_label
        self.y_label = y_label
        self.image_file = None

    def save(self, prefix, directory):

        plotfile = '_gp.plt'
        outputfile = '_gp.png'
        datafile_base = '_data'

        # code for gnuplot.plt
        code = r'''
reset
%(output)s
%(x_label)s
%(y_label)s
%(xrange)s
%(yrange)s
%(var_defs)s
%(functions)s
%(plot)s
'''
        var_defs_str = ""
        functions_str = ""
        plot_str = "plot "
        first_plot = True

        # labels
        x_label = ""
        y_label = ""
        if self.x_label:
            x_label = "set xlabel '"+self.x_label+"'"
        if self.y_label:
            y_label = "set ylabel '"+self.y_label+"'"

        # ranges
        xrange = ""
        yrange = ""
        if not self.xrange is None:
            xrange = "set xrange [%s:%s]" % (self.xrange[0], self.xrange[1])
        if not self.yrange is None:
            yrange = "set yrange [%s:%s]" % (self.yrange[0], self.yrange[1])

        # plot functions
        function_counter = 0
        for f in self.functions:
            # write all values to gnuplot variables
            fname = "f"+str(function_counter)
            for var in f["term"].free_symbols:
                if not var == f["x"]:
                    var_defs_str += var.name + " = " + str(var.value) + "\n"

            # write functions
            functions_str += fname+"("+f["x"].name+")"+" = " + str(f["term"]) + "\n"

            # write plot commands
            if not first_plot:
                plot_str+=", "
            plot_str += fname+"(x)"

            # add title
            if f["title"]:
                plot_str += " title '"+f["title"]+"'"

            first_plot = False
            function_counter += 1

        # plot data sets
        data_set_counter = 0
        for data_set in self.data_sets:

            # create data-string
            data = ""
            for line in range(0,len(data_set["x_values"])):
                data += str(data_set["x_values"][line]) + " "
                data += str(data_set["y_values"][line]) + " "
                if not data_set["x_errors"] is None:
                    data += str(data_set["x_errors"][line]) + " "
                if not data_set["y_errors"] is None:
                    data += str(data_set["y_errors"][line]) + " "
                data += "\n"

            # write to file
            datafile = datafile_base + str(data_set_counter)
            with open(directory + "/" + prefix + datafile,'w') as handle:
                handle.write(data)

            # write plot commands
            if not first_plot:
                plot_str+=", "
            plot_str += "'" + directory + "/" + prefix + datafile +"'"
            if not data_set["x_errors"] is None and not data_set["y_errors"] is None:
                plot_str += " with xyerrorbars"
            elif not data_set["x_errors"] is None:
                plot_str += " with xerrorbars"
            elif not data_set["y_errors"] is None:
                plot_str += " with yerrorbars"

            # add title
            if data_set["title"]:
                plot_str += " title '"+data_set["title"]+"'"

            first_plot = False
            data_set_counter += 1

        output_str = "set term pngcairo enhanced\nset output '"+ directory + "/" + prefix + outputfile + "'"

        with open(directory + "/" + prefix + plotfile,'w') as handle:
            handle.write(code % {"output":output_str, "xrange":xrange, "yrange":yrange, "x_label":x_label, "y_label": y_label, "var_defs": var_defs_str, "functions": functions_str, "plot": plot_str})

        proc=subprocess.Popen(shlex.split("gnuplot '"+ directory + "/" + prefix + plotfile+"'"))
        proc.communicate()

        self.image_file = directory + "/" + prefix + outputfile
