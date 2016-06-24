
from myapp import sensors
import sys
import logging

import apscheduler

logger = logging.getLogger('gecko')


import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler

from Gecko import Gecko
import GeckoIO

import inspect



def main():
    scheduler = BackgroundScheduler()
    scheduler.start()
    app = sys.argv[1]
    try:
        app = __import__(app)
    except ImportError:
        # Display error message
        logging.error("Specified app does not exist")
        return

    gecko = Gecko()

    # make sure app has sensors
    try:
        x = app.sensors
    except AttributeError as e:
        logging.error("App does not contain sensors.py file.")
        return
    
    things = app.sensors
    sensors = {}
    
    # Find all classes the subclass GeckoIO.I_O.Input
    for k, v in things.__dict__.items():
        a = inspect.isclass(v)
        if a:
            b = issubclass(v, GeckoIO.I_O.Input)
            sensors[k] = v
            pass

    for sensorname, sensor in sensors.iteritems():
        s = sensor()
        logger.info("Found sensor...")
        logger.info("    Name:        " + s.__class__.__name__)
        logger.info("    Description: " + s.description)
        logger.info("    Report rate: " + str(s.report_rate) + " seconds.")
        # add job for each sensor
        #scheduler.add_job(sensor.getVal, 'interval', args = [s, gecko], seconds=sensor.report_rate)

    logger.info("Done adding sensors")




    



if __name__ == "__main__":
    main()