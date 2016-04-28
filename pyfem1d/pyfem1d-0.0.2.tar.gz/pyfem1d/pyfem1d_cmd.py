import cmd
import sys
import os
# import pyfem1d.tkgui

class Pyfem1dShell(cmd.Cmd):
    intro = 'Type help or ? to list commands.\n'
    prompt = 'pyfem1d>> '
    file = None

    def __init__(self,parent):
        cmd.Cmd.__init__(self)
        #super(Pyfem1dShell, self).__init__()
        self.analysis = parent

    def do_verbose(self, arg):
        '''Enable verbose output'''
        self.analysis.verbose = True
        #print(arg)

    # def do_gui(self, arg):
    #     '''Start graphical user interface'''
    #     pyfem1d.tkgui.startGui(self.analysis)

    def do_dt(self, arg):
        '''Set timestep size: dt value'''
        val, errormsg = parse_line(arg, type = float, n_args = 1)
        if not errormsg:
            self.analysis.timestep = val[0]
        else:
            print(errormsg)

    def do_nelem(self, arg):
        '''Set total number of elements with nelem(value)'''
        val, errormsg = parse_line(arg, type = int, n_args = 1)
        if not errormsg:
            self.analysis.number_of_elements = val[0]
        else:
            print(errormsg)

    def do_tmax(self, arg):
        '''Set maximum time tmax(value)'''
        val, errormsg = parse_line(arg, type = float, n_args = 1)
        if not errormsg:
            self.analysis.maximum_time = val[0]
        else:
            print(errormsg)

    def do_bctype(self, arg):
        '''Set bc type with bctype(val), can be 0,1,2'''
        val, errormsg = parse_line(arg, type = int, n_args = 1)
        if not errormsg:
            if val[0] == 0 or val[0] == 1 or val[0] == 2:
                self.analysis.bctype = val[0]
            else:
                print("Error: bctype can only be one of 0, 1 and 2")
        else:
            print(errormsg)


    def do_solve(self, arg):
        '''Start solution with solve()'''
        try:
            self.analysis.solve()
        except Exception as e:
            print(e)

    def do_plot(self, arg):
        '''Plot the output stress file using gnuplot. optional argument: stress_file'''
        val, errormsg = parse_line(arg, type = str)
        if len(val) == 0:
            stress_file = self.analysis.stress_file
        elif len(val) == 1:
            stress_file = val[0]
        else:
            print("Error: plot cannot receive more than 1 arguments")

        self.analysis.plotToWindow(stress_file=stress_file)

    def do_plotpdf(self, arg):
        '''Plot the output stress file to a pdf file using gnuplot. optional arguments: plot_file stress_file'''
        val, errormsg = parse_line(arg, type = str)
        if len(val) == 0:
            plot_file = self.analysis.plot_file
            stress_file = self.analysis.stress_file
        elif len(val) == 1:
            plot_file = val[0]
            stress_file = self.analysis.stress_file
        elif len(val) == 2:
            plot_file = val[0]
            stress_file = val[1]
        else:
            print("Error: plot cannot receive more than 2 arguments")

        self.analysis.plotPdf(stress_file=stress_file, plot_file=plot_file)

    def do_pwd(self, arg):
        'Prints current working directory'
        print(self.analysis.workingDirectory)

    #def do_cd(self, arg):
        #'Changes current working directory'

    def do_addumats(self, arg):
        '''Add umat material: addumat exampleMaterial.py'''
        val, errormsg = parse_line(arg, type = str, n_args = 1)
        if not errormsg:
            try:
                path = os.path.join(self.analysis.workingDirectory, val[0])
                self.analysis.add_umats(path)
            except Exception as e:
                print(e)
        else:
            print(errormsg)

    def do_addloads(self, arg):
        '''Add loading function: addloading exampleLoading.py'''
        val, errormsg = parse_line(arg, type = str, n_args = 1)
        if not errormsg:
            try:
                path = os.path.join(self.analysis.workingDirectory, val[0])
                self.analysis.add_loads(path)
            except Exception as e:
                print(e)
        else:
            print(errormsg)


    def do_load(self, arg):
        '''Set load function: load triangle '''
        val, errormsg = parse_line(arg, type = str, n_args = "1+")
        if not errormsg:
            self.analysis.set_load(val[0])
            if len(val) > 1:
                parameters = tuple(map(float, val[1:]))
                self.analysis.set_load_parameters(parameters)
        else:
            print(errormsg)

    def do_listumats(self, arg):
        '''List all umats with the parameters and their values'''
        for key, umat in self.analysis.umat_dict.items():
            print(umat)

    def do_listloads(self, arg):
        '''List all loading functions with the parameters and their values'''
        for key, load in self.analysis.load_dict.items():
            print(load)

    def do_vars(self, arg):
        '''List all variable values and current functions'''
        print(self.analysis.header())


    def do_umat(self, arg):
        '''Set umat function: umat maxwell '''
        val, errormsg = parse_line(arg, type = str, n_args = "1+")

        if not errormsg:
            try:
                self.analysis.set_umat(val[0])
                if len(val) > 1:
                    parameters = tuple(map(float, val[1:]))
                    self.analysis.set_umat_parameters(parameters)
            except Exception as e:
                print(e)
        else:
            print(errormsg)

    def do_run(self, arg):
        val, errormsg = parse_line(arg, type = str, n_args = 1)
        if not errormsg:
            try:
                self.analysis.cmdShell.execFile(val[0])
            except Exception as e:
                print(e)
        else:
            print(errormsg)

    def do_q(self, arg):
        '''End session'''
        self.close()
        return True

    def do_EOF(self,arg):
        '''End session'''
        self.close()
        return True

    # ----- record and playback -----
    #def do_record(self, arg):
        #'Save future commands to filename:  RECORD rose.cmd'
        #self.file = open(arg, 'w')
    #def do_playback(self, arg):
        #'Playback commands from a file:  PLAYBACK rose.cmd'
        #self.close()
        #with open(arg) as f:
            #self.cmdqueue.extend(f.read().splitlines())

    def precmd(self, line):
        # line = line.lower()
        if self.file and 'playback' not in line:
            print(line, file=self.file)
        return line

    def close(self):
        if self.file:
            self.file.close()
            self.file = None

    def execFile(self, filename):
        f = open( filename, "r" )
        array = []
        for line in f:
            array.append( line )
        f.close()
        for i,j in enumerate(array):
            try:
                line = cleanLine(j)
                if(line):
                    #print("Executing: "+line)
                    self.onecmd(line)
            except Exception as err:
                print(err)


def cleanLine(line):
    return line.split('#')[0].strip()

def parse_line(arg, n_args = None, type=int):
    'Convert a series of zero or more numbers to an argument tuple'
    result = tuple(map(type, arg.split()))
    if isinstance(n_args, str):
        if n_args[-1] == "+":
            min_limit = int(n_args[:-1])
            if len(result) < min_limit:
                errormsg = "expected minimum "+str(min_limit)+" arguments, received "+str(len(result))
            else:
                errormsg = None
    elif isinstance(n_args, int):
        if n_args and len(result) != n_args:
            errormsg = "expected "+str(n_args)+" arguments, received "+str(len(result))
        else:
            errormsg = None
    else:
        errormsg = None
    return result, errormsg

