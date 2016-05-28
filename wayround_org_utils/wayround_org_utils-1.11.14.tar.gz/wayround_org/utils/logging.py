
import logging

LEVEL_NAMES = []
for i in list(logging._nameToLevel.keys()):
    LEVEL_NAMES.append(i.upper())

del i
