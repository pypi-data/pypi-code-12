import subprocess, re, os, datetime, time, hashlib
import xml.etree.ElementTree as ET

class bright_devices(object):
    
    _name    = "extBrightness"
    _version = "1.0.4"
    _syntax  = "1.0"
    _date    = "2016-05-05"
    _author  = u"Jörg Mäder"
    _license = "GPLv3"
    _title   = "Extended Brightness and Gamma Controller"
    _descr   = "Brightness, contrast and Gamma controller for multiple screens on linux/X11 systems"
    _email   = "joerg@toolcase.org"
    _url     = "http://www.toolcase.org/app/linux/extBrightness"
    _uid     = "tc_linux_extBrightness"
    _id      = "extBrightness"
    
    showxrandr = False ## true for printing all xrandr commands
    
    def __init__(self):
        self.devices = [] # all active screens
        self.verbose = False # controls the amount of output

        ## saved profiles (xml structure, file and hash to prevent useless savings)
        self.xml = None 
        self._file = None
        self._hash = None
        self.changed = None

        
    def __enter__(self):
        return self
    
    def __exit__(self ,typ, value, traceback):
        ## save profiles if they have changed (if gui is used, this is always the case because of auto-profile [current])
        if self.xml == None: return
        if hashlib.md5(ET.tostring(self.xml.getroot())).digest() == self._hash:
            if self.verbose and self.changed==False: print("No changes to save")
            return
        try:
            root = self.xml.getroot()
            for x in ['_title','_syntax','_author','_url','_descr']: root.set(x[1:],getattr(self,x))
            root.set('timestamp',datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
            self.xml.write(self._file,"UTF-8")
            if self.verbose: print("Saved changes to profile file '{}'".format(self.file))
        except IOError as err:
            print("Not able to save current profiles: " + str(err))

           
    @property
    def version(self): return self._version


    @property
    def file(self): return self._file
    
    @file.setter
    def file(self,val):
        if val == None: val = os.path.join('~','.{}.xml'.format(self._id))
        val = os.path.expanduser(val)
        self._file = val
        
        if os.path.isfile(val):# and False:
            self.xml = ET.ElementTree(self._id,val)
            self._hash = hashlib.md5(ET.tostring(self.xml.getroot())).digest()
        else:
            self.xml = ET.ElementTree(ET.Element(self._id))
        
        

        


    def __getitem__(self,key):
        """
        get one of the devices by key
        allowed are numerical keys (including negative values) and strings
        """
        n = self.count()
        if type(key) == int:
            if key < 0: key = key+n
            if key >= n or key < 0: raise IndexError
            return self.devices[key]
        elif type(key) == str:
            for cd in self.devices:
                if cd.key == key: return cd
            raise KeyError    
        else:
            raise TypeError

    
    
    def exists(self,key):
        """
        returns True or False depending if a device with the given name (string) exists
        """
        for cd in self.devices:
            if cd.key == key: return True
        return False
        
    
    
    def count(self):
        """
        retuns the numer of recogniced devices
        """
        return len(self.devices)


    
    def read(self):
        """
        reads the connected devices by analycing the output of `xrandr -q --verbose`
        """
        cd = None
        self.devices = []
        cur = subprocess.check_output('xrandr -q --verbose',shell=True).decode("utf-8")
        
        for cline in cur.split('\n'):
            if ' connected ' in cline:
                p = cline.split(' connected ') 
                cd = bright_device(p[0],p[1],self)
                self.devices.append(cd)
            elif 'Gamma:' in cline and cd!= None:
                cd.gamma_load(cline)
            elif 'Brightness:' in cline and cd!= None:
                cd.brightness_load(cline)
            else:
                pass
               

    
    
    def gamma_get(self):
        """ returns a dict with all gamma values"""
        return dict([(x.key,x.gamma) for x in self.devices])

    def gamma_set(self,value,key=None):
        """ set the gamma values to all screens (key=None) or a single one (name given in key)""" 
        for cd in self.devices:
            if key == None or key == cd.key: cd.gamma = value
            
            
    def brightness_get(self):
        """ returns a dict with all brightness values"""
        return dict([(x.key,x.brightness) for x in self.devices])

    def brightness_set(self,value,key=None):
        """ set the brightness values to all screens (key=None) or a single one (name given in key)""" 
        for cd in self.devices:
            if key == None or key == cd.key: cd.brightness = value


    ## profile methods ===================================================================================================================
            
    def _profile_find(self,key,make=False):
        """ internal function to find (an create if make = True and not found) profiles in the xml structer"""
        key = str(key).strip()
        try:
            tmp = self.xml.findall("./profile[@key='{}']".format(key))
            if len(tmp) == 1: return tmp[0]
            if len(tmp) == 0 and make: return ET.SubElement(self.xml.getroot(),'profile',{'key':key})
            raise KeyError(key)
        except AttributeError: raise PermissionError(self._file)



    def profile_list(self):
        try:
            if self.verbose:
                res = []
                for cp in self.xml.findall('./profile'):
                    tmp = ['{}: {:0.0f}%, G: {}'.format(cs.get('key'),float(cs.get('brightness'))*100,cs.get('gamma')) for cs in cp.findall('screen')]
                    res.append('{}: {}'.format(cp.get('key'),' | '.join(tmp)))
            else:
                res = [cp.get('key') for cp in self.xml.findall('./profile')]
            return res
        except AttributeError: raise PermissionError(self._file)
            
                    
    def profile_save(self,key):
        """ saves the given values to a (new) profile"""
        tmp = self._profile_find(key,True)
        for cd in self.devices:
            ## remove only screens which are currently connected 
            for x in tmp.findall("screen[@key='{}']".format(cd.key)): tmp.remove(x)
            val = {'key': cd.key,
                   'brightness': str(cd.brightness),
                   'gamma': ' '.join([str(x) for x in cd.gamma])
                   }
            ET.SubElement(tmp,'screen',val)
        tmp.set('timestamp',datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
        
        
    def profile_save_last(self):
        """ saves the given values to profile [last] profile"""
        tmp = self._profile_find('[last]',True)
        for cd in self.devices:
            ## remove only screens which are currently connected 
            for x in tmp.findall("screen[@key='{}']".format(cd.key)): tmp.remove(x)
            val = {'key': cd.key,
                   'brightness': str(cd._org_brightness),
                   'gamma': ' '.join([str(x) for x in cd._org_gamma])
                   }
            ET.SubElement(tmp,'screen',val)
        tmp.set('timestamp',datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
        
        
    def profile_show(self,key):
        """ show values of the asked profile """
        print("Profile: {}".format(key))
        for sc in self._profile_find(key).findall('screen'):
            try:
                cd = self[sc.get('key')]
                print("  Screen: {}".format(cd.key))
                print("    Brightness: {:0.2f}".format(float(sc.get('brightness'))))
                x = [float(x) for x in sc.get('gamma').split(' ')]
                print("    Gamma: {:0.2f}:{:0.2f}:{:0.2f}".format(x[0],x[1],x[2]))
            except: pass
        
                
                
    def profile_delete(self,key):
        """ removes the given profile """
        try: self.xml.getroot().remove(self._profile_find(key))
        except AttributeError: raise PermissionError(self._file)


    def profile_load(self,key):
        """ load and apply the asked profile """
        for sc in self._profile_find(key).findall('screen'):
            try:
                cd = self[sc.get('key')]
                cd.brightness = float(sc.get('brightness'))
                cd.gamma = [float(x) for x in sc.get('gamma').split(' ')]
            except: pass

                       
    def profile_get(self,key):
        """
        returns a dict (one entry per screen) for the asked profile.
        Every screens entry is a dict again with entries for brightness and gamma
        """
        res = {}
        for sc in self._profile_find(key).findall('screen'):
            try:
                res[sc.get('key')] = {'brightness': float(sc.get('brightness')),
                                      'gamma': [float(x) for x in sc.get('gamma').split(' ')]}
            except: pass
        return res
          
        
        


class bright_device(object):
    
    def __init__(self,key,values,container):
        self.key = key
        self.container = container
        
        ## set default values
        self._size = [None,None]
        self._pixels = [None,None]
        self._brightness = 1
        self._gamma = [1,1,1]
        self._primary = False
        ## original values to check if something has changed
        self._org_gamma = self._gamma
        self._org_brightness = self._brightness
        
        
        ## get pixel size
        tmp = re.search('.*?(\d+)x(\d+)[ +].*',values)
        if tmp != None: self._pixels = [int(x) for x in tmp.expand('\\1 \\2').split(' ')]
        ## get physical size
        tmp = re.search('.*?(\d+)mm x (\d+)mm.*',values)
        if tmp != None: self._size = [int(x) for x in tmp.expand('\\1 \\2').split(' ')]
        ## is it the primary screen
        self._primary = re.search('^(.*[^\w])?primary[^\w].*',values) != None

    
    ## ===========================================================================================================
    ## Properties ================================================================================================
    ## ===========================================================================================================
        
    @property
    def values(self):
        """ returns a dict with all values """
        return {'key': self.key, 'gamma':self._gamma, 'brightness': self._brightness}

    @property
    def gamma(self): return self._gamma
    
    @gamma.setter
    def gamma(self,value):
        try:
            if type(value) == float or type(value) == int:
                value = [value]
            if len(value) < 3: value = (value * 3)[0:3]
            for i in range(0,3):
                if value[i] <=0 or value[i] > 10: raise ValueError
            self._gamma = value[0:3]
        except:
            raise ValueError
        
    
    def gamma_load(self,value):
        """ in opposite to 'gamma = ', this will define the (new) original values"""
        tmp = re.search('.*?(\d+\.\d+):(\d+\.\d+):(\d+\.\d+).*',value)
        if tmp != None: 
            self._gamma = [float(x) for x in tmp.expand('\\1 \\2 \\3').split(' ')]
            self._org_gamma = self._gamma

        
    @property
    def brightness(self): return self._brightness
    
    @brightness.setter
    def brightness(self,value):
        if type(value) != float: raise ValueError
        if value < 0 or value > 2: raise ValueError
        self._brightness = value
            
    
    def brightness_load(self,value):
        """ in opposite to 'brightness = ', this will define the (new) original values"""
        tmp = re.search('.*?(\d+\.\d+).*',value)
        if tmp != None: 
            self._brightness = float(tmp.expand('\\1'))
            self._org_brightness = self._brightness 
    
    
    @property
    def pixels(self): return self._pixels
    
    @property
    def size(self): return self._size
    
    @property 
    def primary(self): return self._primary

    
    def reset(self):
        self._gamma = [1,1,1]
        self._brightness = 1.0            


    def apply(self,hard=False):
        """ applies the values using xrandr. if no vlaues have changed and hard is False, nothing will be done """
        if not hard and self._org_brightness == self._brightness and self._org_gamma == self._gamma: return False
        cmd = 'xrandr --output {} --brightness {:0.2f} --gamma {:0.2f}:{:0.2f}:{:0.2f}'
        cmd = cmd.format(self.key,self._brightness,1/self._gamma[0],1/self._gamma[1],1/self._gamma[2]) # I really don't known why 1/gamma is necessary
        if self.container.verbose or self.container.showxrandr: print("Executed command: '{}'".format(cmd))
        if not self.container.virtual: subprocess.check_output(cmd.split(' '))
        self.container.changed = True
        return True


        
    def __str__(self):
        txt = '{}x{} px'.format(self._pixels[0],self._pixels[1])
        if self._size[0] != None: txt = '{}; {}x{} mm'.format(txt,self._size[0],self._size[1])
        if self._brightness != None: txt = '{}; Bright: {:0.0f}%'.format(txt,self._brightness*100)
        if self._gamma[0] != None: txt = '{}; Gamma: {:0.2f}:{:0.2f}:{:0.2f}'.format(txt,self.gamma[0],self.gamma[1],self.gamma[2])
        if self.primary: txt += '; primary'
        return '{} [{}]'.format(self.key,txt)
