from . import _registerdata

allsamples = _registerdata._runit()

for _s in allsamples:
    exec(_s+'=allsamples[_s]')
