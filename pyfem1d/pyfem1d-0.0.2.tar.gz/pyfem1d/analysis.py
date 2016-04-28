import sys, os
import pyfem1d.pyfem1d_cmd as cmd_
import numpy as np
import collections
from pyfem1d.umat import *
from pyfem1d.load import *
from numpy import zeros, dtype, float64
from subprocess import call


class Analysis:
    def __init__(self):
        self.cmdShell = cmd_.Pyfem1dShell(self)

        self.input_file = None
        self.output_file = None
        self.logFile = None
        self.stress_file = None
        self.displacement_file = None
        self.plot_file = None
        self.interactive = False
        # self.gui = False
        self.o_node = None
        self.o_elem = None

        self.umat_dict = {}
        self.load_dict = {}

        self.current_umat_key = None
        self.current_load_key = None

        self.umat = None
        self.load = None

        self.bctype = None
        self.abspath = os.path.dirname(os.path.abspath(__file__))
        self.workingDirectory = None

        self.number_of_elements = None
        self.timestep = None
        self.maximum_time = None

    def header(self):
        header = ""

        header += format_if_not_none(" Input file    : ", self.input_file)
        header += format_if_not_none(" Output file   : ", self.output_file)
        header += format_if_not_none(" Stress file   : ", self.stress_file)
        header += format_if_not_none(" Disp. file    : ",
                                     self.displacement_file)

        header += format_if_not_none(" Number of Elements    nelem = ",
                                     self.number_of_elements)
        header += format_if_not_none(" Time step size           dt = ",
                                     self.timestep)
        header += format_if_not_none(" Duration               tmax = ",
                                     self.maximum_time)
        header += format_if_not_none(" Boundary Condition   bctype = ",
                                     self.bctype)

        header += format_if_not_none(" Umat : ", self.umat)
        header += format_if_not_none(" Load : ", self.load)

        return header

    def printHeader(self):
        """Prints program header with version"""
        print("pyfem1d - 1d finite elements for testing material formulations")
        #print(self.header())

    def add_umats(self, path):
        self.umat_dict.update(deploy_umats(path))

    def add_loads(self, path):
        self.load_dict.update(deploy_loads(path))

    def set_umat(self, key):
        self.umat = self.umat_dict[key]
        self.current_umat_key = key

    def set_umat_parameters(self, parameters):
        self.umat.parameter_values = parameters
        self.umat_dict[self.current_umat_key].parameter_values = parameters

    def set_load(self, key):
        self.load = self.load_dict[key]
        self.current_load_key = key

    def set_load_parameters(self, parameters):
        self.load.parameter_values = parameters
        self.load_dict[self.current_load_key].parameter_values = parameters

    def plotToWindow(self, stress_file=None):
        if not stress_file:
            stress_file = self.stress_file
        commands = ""
        commands += "set terminal X11 size 1300 400;"
        commands += "set key rmargin;"
        commands += "set multiplot;"
        commands += "set lmargin at screen 0.025;"
        commands += "set rmargin at screen 0.325;"
        commands += "set xlabel \"Time\";"
        commands += "set ylabel \"Strain\";"
        commands += "plot \"%s\" u 1:2 w l;" % stress_file
        commands += "set lmargin at screen 0.35;"
        commands += "set rmargin at screen 0.65;"
        commands += "set ylabel \"Stress\";"
        commands += "plot \"%s\" u 1:3 w l;" % stress_file
        commands += "set lmargin at screen 0.675;"
        commands += "set rmargin at screen 0.975;"
        commands += "set xlabel \"Strain\";"
        commands += "plot \"%s\" u 2:3 w l;" % stress_file
        commands += "unset multiplot;"

        call(["gnuplot", "-p", "-e", commands])

#set output "| ps2pdf -dCompatibilityLevel=1.4 -dPDFSETTINGS=/prepress - "+self.ofilebase+"_plot.pdf;\

    def plotPdf(self, stress_file, plot_file):
        # if not stress_file:
        #     stress_file = self.stress_file

        # if not plot_file:
        #     plot_file = self.plot_file

        print("Plotting to file %s" % plot_file)

        commands = ""
        commands += "set term pdf enhanced font \"Helvetica,10\";"
        commands += "set output \"%s\";" % plot_file
        commands += "set lmargin;"
        commands += "set rmargin;"
        commands += "set grid;"
        commands += "unset key;"
        commands += "set xlabel \"Time\";"
        commands += "set ylabel \"Strain\";"
        commands += "plot \"%s\" u 1:2 w l lt 1;" % stress_file
        commands += "set ylabel \"Stress\";"
        commands += "plot \"%s\" u 1:3 w l lt 1;" % stress_file
        commands += "set xlabel \"Strain\";"
        commands += "plot \"%s\" u 2:3 w l lt 1;" % stress_file

        call(["gnuplot", "-p", "-e", commands])

    def startShell(self):
        self.cmdShell.cmdloop()

    def setRuntimeParameters(self):
        self.o_node = self.number_of_elements + 1  #node to be written to the output
        self.o_elem = self.number_of_elements  #element to be written to the output
        self.number_of_elements = self.number_of_elements
        self.neq = self.number_of_elements + 1
        self.nnode = self.number_of_elements + 1
        self.t = 0

        if isinstance(self.bctype, collections.Iterable):
            self.bctype = 0

    def solve(self):
        '''Solution function'''

        if not self.umat:
            raise Exception("No umat function specified")

        if not self.load:
            raise Exception("No load function specified")

        if not self.maximum_time:
            raise Exception("No end time specified")

        if not self.number_of_elements:
            raise Exception("No number of elements specified")

        if not self.timestep:
            raise Exception("No timestep specified")

        self.setRuntimeParameters()
        output = open(self.output_file, 'w')

        #self.update()

        print(self.header())
        output.write(self.header())
        #self.printheader(ofile=output)

        neq = self.number_of_elements + 1
        #Initialize the system matrices
        self.init_system()
        #Set time to zero
        self.t = 0.
        #Generate nodes &  initialize solution vector
        dl = 1 / self.number_of_elements
        u = zeros((self.neq, 1))
        x = zeros((self.nnode, 1))
        #u= zeroflt(self.neq,1)
        #x= zeroflt(self.nnode,1)
        for i in range(int(self.nnode)):
            x[i] = (i - 1) * dl

        # open files for output at the selected node and element
        outd = open(self.displacement_file, 'w')
        outs = open(self.stress_file, 'w')

        # Simulation loop

        self.umat.initial_cond(self.number_of_elements)
        # if self.umat.initcond():
        #     self.umat.initcond()(self.number_of_elements)

        while self.t <= self.maximum_time + self.timestep:

            load = self.load.value(self.t)
            if self.verbose:
                print('   Compute solution at t= %6.4f, load= %6.4f' %
                      (self.t, load))

            # Newton iterations
            res = 1
            niter = 0
            nitermax = 50
            while res > 1.e-10 and niter < nitermax:
                #Calculate the residual vector and stiffness matrix
                #and update the history variables
                self.comp_stiffness(u)
                #impose boundary conditions
                if self.bctype == 0:
                    self.kg[:][0] = 0.
                    self.kg[0][:] = 0.
                    self.kg[0][0] = 1.
                    self.fg[-1] -= load
                    self.fg[0] = 0.
                elif self.bctype == 2:
                    du = load - u[-1]
                    for i in range(int(neq)):
                        self.fg[i] -= self.kg[i][-1] * du
                    self.kg[:][0] = 0.
                    self.kg[0][:] = 0.
                    self.kg[-1][:] = 0
                    self.kg[:][-1] = 0
                    self.kg[0][0] = 1.
                    self.kg[-1][neq - 1] = 1.
                    self.fg[0] = 0.
                    self.fg[-1] = -1 * du
                elif self.bctype == 1:
                    self.kg[:][0] = 0.
                    self.kg[0][:] = 0.
                    self.kg[0][0] = 1.
                    self.fg[1:-1] -= load * dl
                    self.fg[-1] = self.fg[-1] - load * dl / 2
                    self.fg[0] = 0
                else:
                    raise Exception('Error: Undefined bc type identifier: ' +
                                    self.bctype)
                #calculate the residual
                res = np.linalg.norm(self.fg, 2)
                if self.verbose:
                    print('  >> iter %2i, res = %10.5e' % (niter, res))
                #solve the system
                kginv = np.linalg.inv(self.kg)
                dg = np.dot(kginv, self.fg)
                #update nodal displacements
                u -= dg
                niter += 1
            # Print results
            #if self.verbose:
            output.write('\n Solution at t=%6.4f, load= %6.4f\n' %
                         (self.t, load))
            output.write('  Nodal solutions\n')
            output.write('  Node   x-coord.     u\n')
            for i in range(int(neq)):
                output.write(' %4i    %6.4e   %6.4e\n' % (i, x[i], u[i]))
            output.write('\n  Element solutions\n')
            output.write('  Element   Strain       Stress\n')
            for i in range(int(self.number_of_elements)):
                output.write(' %4i       %6.4e   %6.4e\n' %
                             (i, self.eps[i], self.sig[i]))
            outd.write(' %6.4e   %6.4e\n' % (self.t, u[self.o_node - 1]))
            outs.write(' %6.4e   %6.4e   %6.4e\n' %
                       (self.t, self.eps[self.o_elem - 1],
                        self.sig[self.o_elem - 1]))

            # Update History
            # if self.umat.update():
            # self.umat.update()()
            self.umat.update()

            self.t += self.timestep

        print('Finished solution')
        outd.close()
        outs.close()
        output.close()

    def init_system(self):
        self.fg = zeros((self.neq, 1))
        self.kg = zeros((self.neq, self.neq))
        self.eps = zeros((self.number_of_elements, 1))
        self.sig = zeros((self.number_of_elements, 1))
        self.aa = zeros((self.number_of_elements, 1))
        #self.fg=zeroflt(self.neq,1)
        #self.kg=zeroflt(self.neq,self.neq)
        #self.eps=zeroflt(self.number_of_elements,1)
        #self.sig=zeroflt(self.number_of_elements,1)
        #self.aa=zeroflt(self.number_of_elements,1)
        self.dl = 1 / float(self.number_of_elements)

    def comp_stiffness(self, u):
        '''Compute stiffness matrix and residual vector,
        and update history variables'''
        offs = 0
        self.fg[:] = 0.
        self.kg[:][:] = 0.
        dN = zeros((2, 1))
        #dN=zeroflt(2,1)
        # Assembly: loop over elements
        for n in range(int(self.number_of_elements)):
            dN[0] = -1 / self.dl
            dN[1] = -1 * dN[0]
            #compute element strain
            epsl = (u[n + 1] - u[n]) / self.dl
            # Calculate the stress, modulus and update history at the Gauss point

            sigl, aal = self.umat.stress_tangent(self.timestep, n, epsl)

            #store the stresses and moduli
            self.eps[n] = epsl
            self.sig[n] = sigl
            self.aa[n] = aal
            #loop over element dofs: element stiffness and internal force vector
            #fe = zeroflt(2,1)
            #ke = zeroflt(2,2)
            fe = zeros((2, 1))
            ke = zeros((2, 2))
            for i in range(2):
                fe[i] += dN[i] * sigl * self.dl
                #\int B^{T}\sigma dV
                for j in range(2):
                    ke[i][j] += dN[i] * aal * dN[
                        j] * self.dl  #\int B^{T} E B dV

            #assemble global matrices
            for i in range(2):
                self.fg[i + offs] += fe[i]
                for j in range(2):
                    self.kg[i + offs][j + offs] += ke[i][j]
            offs += 1


def format_if_not_none(prefix, var):
    return prefix + (str(var) if var else "None") + "\n"
