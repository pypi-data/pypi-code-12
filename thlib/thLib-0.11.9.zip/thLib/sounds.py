'''
Python module to read, play, and write sound data.
For flexibility, FFMPEG is used for non-WAV files.

You can obtain it for free from
    http://ffmpeg.org
    
Mac users using Anaconda should follow the instructions on
        https://anaconda.org/soft-matter/ffmpeg
    Otherwise, the tups under
        https://github.com/fluent-ffmpeg/node-fluent-ffmpeg/wiki/Installing-ffmpeg-on-Mac-OS-X
    seemed to work. Binaries are also available from
        - http://www.evermeet.cx/ffmpeg/ffmpeg-2.1.4.7z
        - http://www.evermeet.cx/ffplay/ffplay-2.1.4.7z

Note that FFMPEG must be installed externally!
Please install ffmpeg/ffplay in the following directory:

    - Windows:  "C:\\\\Program Files\\\\ffmpeg\\\\bin\\\\"
    - Mac:  	"/usr/local/bin/" (is already included in the default paths of the Mac terminal.)
    - Linux:	"/usr/bin/"

Compatible with Python 2.x and 3.x

'''

'''
Date:   April 2016
Ver:    1.12
Author: thomas haslwanter

Changes: 1.2 replaced Qt with wxpython, because of timer problems
Changes: 1.3 put ui into thLib; allow "cancel" for "writeWav"
Changes: 1.4 Use FFMPEG for conversion from miscellaneous inputs to ".wav", and FFPLAY to play files non-Windows platforms
Changes: 1.5 replace ui with a version that only uses Tkinter, make it compatible with Python 3.x
Changes: 1.6 if FFMPEG is not found in the default location, the user can locate it interactively.
Changes: 1.7 should make it compatible with Linux and Mac.
Changes: 1.8 fix writing/playing for self-generated data
Changes: 1.9 System identifier for linux corrected; for stereo sounds, both channels are now returned
Changes: 1.10 System identifier for linux corrected (hopefully properly this time)
Changes: 1.11 Playing on linux fixed
Changes: 1.12 setData did not work correctly for sound-formats different from np.int16

'''

import numpy as np
import os
import sys
from scipy.io.wavfile import read, write
import tempfile
from subprocess import call
import json

# The following construct is required since I want to run the module as a script
# inside the thLib-directory
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.realpath(os.path.dirname(__file__))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from thLib import ui   # from thLib

if sys.platform=='win32':
    import winsound
    
# "ffmpeg" has to be installed externally, into the location listed below
# You can obtain it for free from http://ffmpeg.org

    config_file = 'CSS.json'
    try:
        # Get the configuration from the default config file
        with open(config_file, 'r') as inFile:
            info = json.load(inFile)
            ffmpeg = info['ffmpeg']
            ffplay = info['ffplay']
            
    except IOError:
        # If the file does not exist, get the data interactively
        ffmpeg, path = ui.getfile(FilterSpec='*.exe', DialogTitle='Select "ffmpeg.exe": ', 
                                 DefaultName=r'C:\ffmpeg\bin\ffmpeg.exe')
        ffplay, path = ui.getfile(FilterSpec='*.exe', DialogTitle='Select "ffplay.exe"',
                                  DefaultName= r'C:\ffmpeg\bin\ffplay.exe')
        
        # Set the variables
        ffmpeg = os.path.join(path, ffmpeg)
        ffplay = os.path.join(path, ffplay)
        
        # Save them to the default config file
        info = {'ffmpeg':ffmpeg, 'ffplay': ffplay}
        try:
            with open(config_file, 'w') as outFile:
                json.dump(info, outFile)
                print('Config information written to {0}'.format(os.path.abspath(config_file)))
        except PermissionError as e:
            curDir = os.path.abspath(os.curdir)
            print('Current directory: {0}'.format(curDir))
            print('Error: {0}'.format(e))
else:
    ffmpeg = 'ffmpeg'
    ffplay = 'ffplay'
    
class Sound:
    '''
    Class for working with sound in Python.
    
    A Sound object can be initialized
        - by giving a filename
        - by providing "int16" data and a rate
        - without giving any parameter; in that case the user is prompted
          to select an infile

    Parameters
    ----------
    inFile : string
        path- and file-name of infile, if you get the sound from a file.
    inData: array
        manually generated sound data; requires "inRate" to be set, too.
    inRate: integer
        sample rate; required if "inData" are entered.

    Returns
    -------
    None :
        No return value. Initializes the Sound-properties.

    Notes
    -----
    For non WAV-files, the file is first converted to WAV using
    FFMPEG, and then read in. A warning is generated, to avoid
    unintentional deletion of existing WAV-files.
    
    SoundProperties:
        - source
        - data
        - rate
        - numChannels
        - totalSamples
        - duration
        - bitsPerSample

    Examples
    --------
    >>> from thLib.sounds import Sound
    >>> mySound1 = Sound()
    >>> mySound2 = Sound('test.wav')
    >>>
    >>> rate = 22050
    >>> dt = 1./rate
    >>> freq = 440
    >>> t = np.arange(0,0.5,dt)
    >>> x = np.sin(2*np.pi*freq * t)
    >>> amp = 2**13
    >>> sounddata = np.int16(x*amp)
    >>> mySound3 = Sound(inData=sounddata, inRate=rate)

    '''
    
    def __init__(self, inFile = None, inData = None, inRate = None):
        '''Initialize a Sound object '''
        
        if inData is not None:
            if inRate is None:
                print('Set the "rate" to the default value (8012 Hz).')
                rate = 8012.0
            self.setData(inData, inRate)
        else: 
            if inFile is None:
                inFile = self._selectInput()
                if inFile == 0:
                    return
            try:
                self.source = inFile
                self.readSound(self.source)
            except FileNotFoundError as err:
                print(err)
                inFile = self._selectInput()
                self.source = inFile
                self.readSound(self.source)
        
    def readSound(self, inFile):
        '''
        Read data from a sound-file.

        Parameters
        ----------
        inFile : string
            path- and file-name of infile

        Returns
        -------
        None :
            No return value. Sets the property "data" of the object.

        Notes
        -----
        * For non WAV-files, the file is first converted to WAV using
          FFMPEG, and then read in.

        Examples
        --------
        >>> mySound = Sound()
        >>> mySound.readSound('test.wav')

        '''
        
        # Python can natively only read "wav" files. To be flexible, use "ffmpeg" for conversion for other formats
        if not os.path.exists(inFile):
            print('{0} does not exist!'.format(inFile))
            raise FileNotFoundError
       
        (root, ext) = os.path.splitext(inFile)
        if ext[1:].lower() != 'wav':
            outFile = root + '.wav'
            cmd = [ffmpeg, '-i', inFile, outFile, '-y']
            call(cmd)
            print('Infile converted from ' + ext + ' to ".wav"')
            
            inFile = outFile
            self.source = outFile

        self.rate, self.data = read(inFile)
        self._setInfo()
        print('data read in!')
    
    def play(self):
        '''
        Play a sound-file.

        Parameters
        ----------
        None : 

        Returns
        -------
        None :
            

        Notes
        -----
        On "Windows" the module "winsound" is used; on other
        platforms, the sound is played using "ffplay" from FFMPEG.

        Examples
        --------
        >>> mySound = Sound()
        >>> mySound.readSound('test.wav')
        >>> mySound.play()

        '''

        try:
            if self.source == None:
                tmpFile = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                tmpFile.close()
                self.writeWav(tmpFile.name)
                if sys.platform=='win32':
                    winsound.PlaySound(tmpFile.name, winsound.SND_FILENAME)
                else:
                    cmd = [ffplay, '-autoexit', '-nodisp', '-i', tmpFile.name]
                    call(cmd)
            elif os.path.exists(self.source):
                print('Playing ' + self.source)
                if sys.platform=='win32':
                    winsound.PlaySound(str(self.source), winsound.SND_FILENAME)
                else:
                    cmd = [ffplay, '-autoexit', '-nodisp', '-i', self.source]
                    call(cmd)
        except SystemError:
            print('If you don''t have FFMPEG available, you can e.g. use installed audio-files. E.g.:')
            print('import subprocess')
            print('subprocess.call([r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe", r"C:\Music\14_Streets_of_Philadelphia.mp3"])')
            
    def setData(self, data, rate):
        ''' Set the properties of a Sound-object. '''

        # If the data are in another format, e.g. "float", convert
        # them to integer and scale them to a reasonable amplitude
        if not type(data[0]) == np.int16:
            defaultAmp = 2**13
            # Watch out with integer artefacts!
            data = np.int16(data * (defaultAmp / np.max(data)))
            
        self.data = data
        self.rate = rate
        self.source = None
        self._setInfo()

    def writeWav(self, fullOutFile = None):            
        '''
        Write sound data to a WAV-file.

        Parameters
        ----------
        fullOutFile : string
            Path- and file-name of the outfile. If none is given,
            the user is asked interactively to choose a folder/name
            for the outfile.

        Returns
        -------
        None :
            

        Examples
        --------
        >>> mySound = Sound()
        >>> mySound.readSound('test.wav')
        >>> mySound.writeWav()

        '''

        if fullOutFile is None:
            (outFile , outDir) = ui.savefile(DialogTitle='Write sound to ...', FilterSpec='*.wav')            
            if outFile == 0:
                print('Output discarded.')
                return 0
            else:
                fullOutFile = os.path.join(outDir, outFile)
        else:
            outDir = os.path.abspath(os.path.dirname(fullOutFile))
            outFile = os.path.basename(fullOutFile)
        #        fullOutFile = tkFileDialog.asksaveasfilename()

        write(str(fullOutFile), int(self.rate), self.data)
        print('Sounddata written to ' + outFile + ', with a sample rate of ' + str(self.rate))
        print('OutDir: ' + outDir)

        return fullOutFile
    
    def info(self):
        '''
        Return information about the sound.

        Parameters
        ----------
        None : 

        Returns
        -------
        source : name of inFile
        rate :   sampleRate
        numChannels : number of channels
        totalSamples : number of total samples
        duration : duration [sec]
        bitsPerSample : bits per sample
            
        Examples
        --------
        >>> mySound = Sound()
        >>> mySound.readSound('test.wav')
        >>> info = mySound.info()
        >>> (source, rate, numChannels, totalSamples, duration, bitsPerSample) = mySound.info()

        '''
        
        return (self.source,
                self.rate,
                self.numChannels,
                self.totalSamples,
                self.duration,
                self.dataType)

    def summary(self):
        '''
        Display information about the sound.

        Parameters
        ----------
        None : 

        Returns
        -------
        None :
            
        Examples
        --------
        >>> mySound = Sound()
        >>> mySound.readSound('test.wav')
        >>> mySound.summary()

        '''
        
        import yaml
        
        (source, rate, numChannels, totalSamples, duration, dataType) = self.info()
        info = {'Source':source,
                'SampleRate':rate,
                'NumChannels':numChannels,
                'TotalSamples':totalSamples,
                'Duration':duration,
                'DataType':dataType}
        print(yaml.dump(info, default_flow_style=False))
        
    def _setInfo(self):
        '''Set the information properties of that sound'''
            
        if len(self.data.shape)==1:
            self.numChannels = 1
            self.totalSamples = len(self.data)
        else:
            self.numChannels = self.data.shape[1]
            self.totalSamples = self.data.shape[0]
            
        self.duration = float(self.totalSamples)/self.rate # [sec]
        self.dataType = str(self.data.dtype)
        
    def _selectInput(self):
        '''GUI for the selection of an in-file. '''

        (inFile, inPath) = ui.getfile('*.wav;*.mp3', 'Select sound-input: ')
        if inFile == 0:
            print('No file selected')
            return 0
        else:
            fullInFile = os.path.join(inPath, inFile)
            print('Selection: ' + fullInFile)
            return fullInFile

def main():
    ''' Main function, to test the module '''
    import os
    import numpy as np
    import matplotlib.pyplot as plt
    
    ### Import a file, and play the sound
    #dataDir = r'C:\Users\p20529\Documents\Teaching\ETH\CSS\Exercises\Ex_Auditory\sounds\mp3'
    #inFile = 'tiger.mp3'
    
    #fullFile = os.path.join(dataDir, inFile)
    #mySound = Sound(fullFile)
    #mySound.play()
    
    ## Test with self-generated data
    #rate = 22050
    #dt = 1./rate
    #t = np.arange(0,0.5,dt)
    #freq = 880
    #x = np.sin(2*np.pi*freq*t)
    #sounddata = np.int16(x*2**13)
    
    #inSound = Sound(inData=sounddata, inRate=rate)
    #inSound.summary()
    #inSound.play()
    
    ## Test if type conversion works
    #inSound2 = Sound(inData=x, inRate=rate)
    #inSound2.play()
    
    # Test with GUI
    inSound = Sound()
    inSound.play()
    #inSound.writeWav()
    
if __name__ == '__main__':
    main()
    
