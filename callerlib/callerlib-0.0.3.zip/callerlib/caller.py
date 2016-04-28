from . import settings
from callerlib import CallerLib

if __name__ == '__main__':
    CallerLib(settings.RF_HOST, settings.RF_PORT, settings.SIP_HOST, settings.SIP_PORT)
