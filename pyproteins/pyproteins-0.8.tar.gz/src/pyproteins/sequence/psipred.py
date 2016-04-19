import os
import re

# Not intended to make psipred calls
# Simple parser



# for now we only parse the horiz file
def parse(folder=None):
    data = {'Conf':'', 'Pred':'', 'AA':''}

    for file in os.listdir(folder):
        if file.endswith("horiz"):
            print folder + '/' + file
            with open(folder + '/' + file, 'r') as f:
                for l in f:
                    m = re.match('^[\s]*(Conf|Pred|AA):[\s]+([\S]+)[\s]*$', l)
                    if m:
                        data[m.group(1)] += m.group(2)

    return Container(conf=data['Conf'], pred=data['Pred'], aa=data['AA'])


class Container(object):
    def __init__(self, **kwargs):
        self.regKeys = ['conf', 'pred', 'aa']
        for key in self.regKeys:
            if key in kwargs:
                setattr(self, key, kwargs[key])

    def __repr__(self):
        string = ''
        for key in self.regKeys:
            if hasattr(self, key):
                string += key + ':' + getattr(self, key) + '\n'
        return string
