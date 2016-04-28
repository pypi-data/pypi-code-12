import helper

class Umat:
    parameter_values = []
    parameter_names = []

    def __init__(self):
        pass

    def initial_cond(self, n_elem):
        pass

    def update(self):
        pass

    def stress_tangent(self, dt, n, eps):
        raise Exception("Stress-tangent function of umat not defined")

    def set_parameter_values(self, values):
        pass

    def __repr__(self):
        result = ""
        result += type(self).__name__ + "("
        for n, (name, val) in enumerate(zip(self.parameter_names, self.parameter_values)):
            result += name+"="+str(val)
            if n != len(self.parameter_names)-1:
                result += ", "
        result += ")"
        return result

def deploy_umats(path):
    return helper.deploy_objects(path, Umat)
