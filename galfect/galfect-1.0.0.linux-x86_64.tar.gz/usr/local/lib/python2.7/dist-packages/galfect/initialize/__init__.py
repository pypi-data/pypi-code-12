import os
import os.path as op
import shutil

class GalfectInitialize(object):
    def __init__(self, loc):
        self.loc = loc
        if op.exists(loc):
            shutil.rmtree(loc)

    def run(self):
        jsdir = op.join(self.loc, "js")
        if not op.exists(jsdir):
            os.makedirs(jsdir)
        filedir, ext = op.split(__file__)
        packagedir = op.abspath(op.join(filedir, '..', '..'))
        shutil.copy(op.join(packagedir, "index.html"), self.loc)
        datadirs = ["bootstrap", "css"]
        for d in datadirs:
            shutil.copytree(
                op.join(packagedir, d),
                op.join(self.loc, d)
            )
