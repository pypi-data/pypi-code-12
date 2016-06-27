
import sys
import logging
import argparse
import apscheduler
import inspect
from apscheduler.schedulers.background import BackgroundScheduler

from Gecko import Gecko 
import GeckoIO

parser = argparse.ArgumentParser()
parser.add_argument(
    "application",
    help="Directory that contains your application"
)
    
parser.add_argument(
    '-v', '--verbose',
    help="Verbose logging",
    action="store_const", dest="loglevel", const=logging.INFO,
    default=logging.WARNING
)

args = parser.parse_args()

logger = logging.getLogger('gecko')
logger.setLevel(args.loglevel)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


'''
aps = logging.getLogger()
aps.setLevel(logging.DEBUG)
aps.addHandler(ch)
'''









def main():

    scheduler = BackgroundScheduler()
    scheduler.start()
    # Check if arg was passed
    app = args.application
    try:
        app = __import__(app)
    except ImportError as e:
        # Check if the folder exists, if it does, add __init__ (if it doesn't exist)
        # and try again
        # Display error message
        logger.error("Specified app does not exist: " + str(e))
        return
   
    
    gecko = Gecko()
    
    # make sure app has sensors
    try:
        x = app.sensors
    except AttributeError as e:
        logger.error("App does not contain sensors.py file.")
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
    logger.info(sensors)
    for sensorname, sensor in sensors.iteritems():
        s = sensor()
        logger.info("Found sensor...")
        logger.info("    Name:        " + s.__class__.__name__)
        logger.info("    Description: " + s.description)
        logger.info("    Report rate: " + str(s.report_rate) + " seconds.")
        # add job for each sensor
        scheduler.add_job(sensor.getVal, 'interval', args = [s, gecko], seconds=sensor.report_rate, max_instances=3 )

    logger.info("Done adding sensors")

    import time
    while (True):
        time.sleep(1)




if __name__ == "__main__":
    main()