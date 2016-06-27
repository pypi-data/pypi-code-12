import os
import datetime


def getTime():
	"""Return a readable date string

    Return:
        string with time with format Hour:Minute:Second

	Notes about time: 
	    - 'Readable' times use datetime and follow the format returned by this function
	    - 'API' times use int(time.time())
	    - Python unix time is in seconds, but Javascript and other languages use milliseconds
	"""
	return datetime.datetime.now().strftime('%H:%M:%S')


class Logger():
    """Class for logging
    
    Args:
        currentWorkingDirectory: string in reference to your Current Working Directory, ie. os.path.dirname(os.path.abspath(__file__))
        scriptLogDescription: string in reference to the name of your script, ie. 'AS' (for script api_server.py)
        enableLogging: boolean to enable logging to stdout
    """
    def __init__(self, scriptLogDescription, currentWorkingDirectory, enableLogging=True):
        self.currentWorkingDirectory = currentWorkingDirectory
        self.scriptLogDescription = scriptLogDescription
        self.enableLogging = enableLogging
    
    def log(self, msg, toFile=False):
        """Print some text with readable timestamp

        Args:
            msg: string to print
            toFile: boolean to write to log file in same directory
        """
        line = '[%s] %s: %s' %(getTime(), self.scriptLogDescription, msg)
        if self.enableLogging:
            print line
        if toFile:
            fp = '%s\%s.log' %(self.currentWorkingDirectory, self.scriptLogDescription) 
            with open(fp, 'a') as f:
                f.write(line)
                f.write('\r\n')