from pyfem1d.load import Load
from math import sin, pi


class Triangle(Load):
    parameter_values = [25, 0.008]
    parameter_names = ['loading_per', 'magnitude']

    def value(self, t):
        tper = self.parameter_values[0]
        magn = self.parameter_values[1]
        tloc = t
        while tloc > tper:
            tloc = tloc - tper
        qper = tper / 4.
        if tloc <= qper:
            load = tloc
        elif tloc > qper and tloc <= 2. * qper:
            load = qper - (tloc - qper)
        elif tloc > 2. * qper and tloc <= 3. * qper:
            load = -1. * (tloc - 2. * qper)
        elif tloc > 3. * qper and tloc <= tper:
            load = -1. * qper + (tloc - 3. * qper)
        return load * magn


class Sine(Load):
    parameter_values = [25., 0.008]
    parameter_names = ['loading_per', 'magnitude']

    def value(self, t):
        return self.parameter_values[1] * sin(t / self.parameter_values[0] *
                                              2. * pi)


class Creep(Load):
    parameter_values = [0, 10, 0.008]
    parameter_names = ['start', 'end', 'magnitude']

    def value(t):
        if t <= self.parameter_values[1] and t >= self.parameter_values[0]:
            return self.parameter_values[2]
        else:
            return 0


class Heaviside(Load):
    parameter_values = [0.008]
    parameter_names = ['magnitude']

    def value(t):
        magn = self.parameter_values[0]
        return magn


class Proportional(Load):
    parameter_values = [0.008]
    parameter_names = ['magnitude']

    def value(t):
        magn = self.parameter_values[0]
        return magn * t
