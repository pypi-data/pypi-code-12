from pyfem1d import helper

class Load:
    parameter_names = []
    parameter_values = []

    def __init__(self):
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


def deploy_loads(path):
    return helper.deploy_objects(path, Load)
