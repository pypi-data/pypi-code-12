import numpy as np
from pyfem1d.umat import Umat


class LinearElastic(Umat):
    parameter_values = [100]
    parameter_names = ['elastic_mod']

    def stress_tangent(self, dt, n, eps):
        #Get the material variables
        E = self.parameter_values[0]
        #Calculate the stress and consistent modulus
        sigl = E * eps  #linear elasticity
        aal = E
        return sigl, aal


class NonlinearElastic(Umat):
    # parameter_values = [100, 0.03]
    parameter_values = [100, 0.0001]
    parameter_names = ['elastic_mod', 'sat_rate']

    def stress_tangent(self, dt, n, eps):
        E = self.parameter_values[0]
        eta = self.parameter_values[1]

        #Calculate the stress and consistent modulus
        sigl = E * eta * (1 - np.exp(-1 * eps / eta))  #nonlin elasticity
        aal = E * np.exp(-1 * eps / eta)
        return sigl, aal


class Maxwell(Umat):

    parameter_values = [100, 1500]
    parameter_names = ['elastic_mod', 'viscosity']

    def __init__(self):
        self.h1 = []
        self.hn = []

    def initial_cond(self, asdf):
        self.h1 = np.zeros((asdf, 1), dtype=np.float64)
        self.hn = np.zeros((asdf, 1), dtype=np.float64)
        self.nelem = asdf

    def update(self):
        temp = self.h1[:]
        self.h1 = self.hn[:]
        self.hn = temp[:]

    def stress_tangent(self, dt, n, eps):
        #Get the material variables
        E = self.parameter_values[0]
        eta = self.parameter_values[1]
        alphan = self.hn[n]
        #Calculate the stress and consistent modulus
        alpha = (alphan + eps * dt * E / eta) / (1 + dt * E / eta)
        sigl = E * (eps - alpha)
        aal = E / (1 + dt * E / eta)

        self.h1[n] = alpha

        return sigl, aal


class StandardLinearSolid(Umat):
    parameter_values = [1000, 4000, 20000]
    parameter_names = ['E0', 'E1', 'viscosity']

    def __init__(self):
        self.h1 = []
        self.hn = []

    def initial_cond(self, asdf):
        self.h1 = np.zeros((asdf, 1), dtype=np.float64)
        self.hn = np.zeros((asdf, 1), dtype=np.float64)
        self.nelem = asdf

    def update(self):
        global h1, hn
        temp = self.h1[:]
        self.h1 = self.hn[:]
        self.hn = temp[:]

    def stress_tangent(self, dt, n, eps):
        #Get the material variables
        E0 = self.parameter_values[0]
        E1 = self.parameter_values[1]
        eta = self.parameter_values[2]
        alphan = self.hn[n]

        #Calculate the stress and consistent modulus
        alpha = (alphan + eps * dt * E1 / eta) / (1 + dt * E1 / eta)

        sigl = E0 * eps + E1 * (eps - alpha)
        aal = E0 + E1 / (1 + dt * E1 / eta)  #
        #Update history
        self.h1[n] = alpha

        return sigl, aal


class StandardLinearSolid2(Umat):

    parameter_values = [1000, 4000, 20000]
    parameter_names = ['E0', 'E1', 'viscosity']

    #step size for the five-point stencil
    fs = 0.001
    tol = 1e-10
    offset = 0.1

    def __init__(self):
        self.h1 = []
        self.hn = []

    def initial_cond(self, asdf):
        self.h1 = np.zeros((asdf, 1), dtype=np.float64)
        self.hn = np.zeros((asdf, 1), dtype=np.float64)
        self.nelem = asdf

    def update(self, ):
        temp = self.h1[:]
        self.h1 = self.hn[:]
        self.hn = temp[:]

    # Constitutive equations

    def sigel1(self, strain):  #elastic stress
        result = strain * self.parameter_values[1]
        return result

    def sigel0(self, strain):  #elastic stress
        result = strain * self.parameter_values[0]
        return result

    def epsvisdot(self, stress):  # viscous strain derivative
        result = stress / self.parameter_values[2]
        return result

    def sig(self, eps, alpha):  #total stress
        result = self.sigel0(eps) + self.sigel1(eps - alpha)
        return result

    # Secand iteration

    def nextstep(self, hist, dt, eps):
        dummy = [hist - self.offset, hist]
        #using the secant method
        #print '     ++++++++++++++++'
        while True:
            temp2 = dummy[1] - self.residual(dummy[1], hist, dt, eps) * (
                dummy[1] - dummy[0]) / (self.residual(dummy[1], hist, dt, eps)
                                        - self.residual(dummy[0], hist, dt,
                                                        eps))
            dummy[0] = dummy[1]
            dummy[1] = temp2
            err = abs(dummy[0] - dummy[1])

            #print '     >>>>> Secant_err: %10.5e' %(err)
            if err < self.tol: break
        return dummy[1]

    # RESIDUAL
    def residual(self, next_, now, dt, eps):
        result = next_ - now - dt * self.epsvisdot(self.sigel1(eps - next_))
        return result

    # Five point stencil

    #def fivepoint(f,*p):
    #return (-1*f(p[0]+2*fs,p[1:])+8*f(p[0]+fs,p[1:])-8*f(p[0]-fs,p[1:])+f(p[0]-2*fs,p[1:]))/(12*fs)

    def stress_tangent(self, dt, n, eps):
        alphan = self.hn[n]

        #CALCULATE THE NEXT VISCOUS STRAIN
        alpha = self.nextstep(alphan, dt, eps)

        #calculate the stress and the consistent modulus
        sigl = self.sig(eps, alpha)
        #aal  = fivepoint(sig,eps,alpha)
        aal = (-1 * self.sig(eps + 2 * self.fs, alpha) + 8 * self.sig(
            eps + self.fs, alpha) - 8 * self.sig(eps - self.fs, alpha) +
               self.sig(eps - 2 * self.fs, alpha)) / (12 * self.fs)
        #Update history
        self.h1[n] = alpha

        return sigl, aal
