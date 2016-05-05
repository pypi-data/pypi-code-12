#!/usr/bin/python
# coding=utf-8
'''
Created on 22.07.2014

see bright.py for author/copyright and so on

Brightness/contrast/gamma controller for multiple screens
Based on the functionality of xrandr ( -> linux only)

This module primary handles the command line features of this application.
The work horses are the classes bright_devices and bright_device in bright.py
gui.py is the visible application based on Qt4.8 (started if no option was used or --gui is present too)
'''


import sys, math, os, argparse
if __name__ == '__main__': sys.path.insert(0,os.path.dirname(sys.path[0]))
from src.bright import bright_devices


def run():
    with bright_devices() as bd:
        bd.read()

        parser = argparse.ArgumentParser(prog= bd._name,
                                         epilog="Copyright {} - {} Version {}\n{}".format(bd._author,bd._date,bd._version,bd._url),
                                         description='Control brightness and gamma for all connected screens.')
        
        parser.add_argument('-b',metavar='NUM',type=float,help='set brightness (float between 0.0 - 1.999 or integer between 2 - 200)')
        parser.add_argument('-B',metavar='NUM',type=float,help='set brightness by increment. Hint: To small changes may not work')
        parser.add_argument('-c','--count', action='store_true', help='count the connected screens')
        parser.add_argument('-d',metavar='DISPLAY',help="Limit action to this screen. Use 'a' for all, 'p' for primary and 'np' for non-primary")
        parser.add_argument('-g',metavar='GAMMA',help="set gamma correction. Either one or three float values between 0 and 10 separated by ':'")
        parser.add_argument('-l', action='store_true',help="list screens, together with '-v' the current values are shown.")
        parser.add_argument('-p', action='store_true',help="show key of primary screen, use -v for more details")
        parser.add_argument('-r', action='store_true',help="reset (set brightness to 100%% and gamma to 1)")
        parser.add_argument('-t',metavar='TEMP',type=int,help="set gamma using a temperature in Kelvin")
        parser.add_argument('-u', action='store_true',help="undo last changes (saved in profile [last])")
        parser.add_argument('-D', action='store_true',help="set the brightness to 0 or to the last value if it is already 0")
        parser.add_argument('-v', action='store_true',help="verbose output including the 'xrandr command' which was used to set the new values")
        parser.add_argument('--gui', action='store_true',help="show user interface after processing the other options (default if no option is present)")
        parser.add_argument('--version', action='store_true',help="show current version")
        parser.add_argument('--hard', action='store_true',help="Apply changes using xrandr even nothing has changed")
        parser.add_argument('--virtual', action='store_true',help="do not apply changes but show potential results")
        parser.add_argument('--file',metavar='FILE',help='file used for saving profiles and other settings (default: ~/.extBrightness.xml)')
        parser.add_argument('-P','--profile-load',metavar='NAME',help="load profile")
        parser.add_argument('--profile-save',metavar='NAME',help="save current values as profile. If option --gui is used too, the final values of it will be saved!")
        parser.add_argument('--profile-delete',metavar='NAME',help="delete profile")
        parser.add_argument('--profile-show',metavar='NAME',help="show profile")
        parser.add_argument('--profile-list', action='store_true',help="list all profiles. Use '-v' too for displaying the saved values.")
        
        
                 
        ## ------------------------------------------------------
        ## preparation
        ## ------------------------------------------------------

        args = parser.parse_args()

        ## special combinations
        uargs = [k for k,v in vars(args).items() if v not in (False,None,[])]
        if uargs==[]: ## no arguments at all -> show gui
            args.gui = True
        elif uargs==['d']: ## only restriction to some devices -> show values
            args.l = True
            args.v = True

        
        ## st some instance variables at bd
        try:
            bd.file = args.file
        except PermissionError:
            print("No read access to " + bd._file)
        bd.verbose = args.v
        
        bd.virtual = args.virtual
        if args.virtual:
            args.hard = True
            bd.verbose = True
        
        
        
        ## ------------------------------------------------------
        ## options which ignore others
        ## ------------------------------------------------------
        
        ## count devices
        if args.count == True:
            if bd.verbose:
                print('#Screens: {}'.format(bd.count()))
            else:
                print(bd.count())
            parser.exit()  
        
        
        ## show primary device
        if args.p:
            for cbd in bd: 
                if cbd.primary: print(cbd if args.v else cbd.key)
            parser.exit()
            
            
        ## show version of this tool
        if args.version:
            print(bd.version)
            parser.exit()        




        ## ------------------------------------------------------
        ## Profile options (except save)
        ## ------------------------------------------------------

        ## show a saved profiles
        if args.profile_show != None:
            try: 
                bd.profile_show(args.profile_show)
            except KeyError: 
                parser.exit("Unknown profile: " + args.profile_show)
            except PermissionError:
                parser.exit("profile file {} unknown or protected".format(bd._file))
            parser.exit()
        
        
        ## list all saved profiles
        if args.profile_list:
            try:
                for cbd in bd.profile_list(): print(cbd)
            except PermissionError:
                parser.exit("profile file {} unknown or protected".format(bd._file))

            parser.exit()


        ## load profile
        if args.profile_load != None:
            try: 
                bd.profile_load(args.profile_load)
                bd.changed = False
            except KeyError: 
                parser.exit("Unknown profile: " + args.profile_load)
            except PermissionError:
                parser.exit("profile file {} unknown or protected".format(bd._file))

        
        ## delete profile
        if args.profile_delete != None:
            try:
                bd.profile_delete(args.profile_delete)
            except KeyError:
                print("Warning: profile {} not found. Deletion not possible.".format(args.profile_delete))  
            except PermissionError:
                parser.exit("profile file {} unknown or protected".format(bd._file))


        
        
        
        
            
        ## ------------------------------------------------------    
        ## which devices should be affected
        ## ------------------------------------------------------
        if args.d in ('*','all','a',None):
            devs = bd.devices
        elif args.d == 'p':
            devs = [cd for cd in bd.devices if cd.primary]
        elif args.d in ('n','none'): # implemented if this tool is used from somewhere else and should do nothing!
            devs = []
        elif args.d == 'np':
            devs = [cd for cd in bd.devices if not cd.primary]       
        else:
            try: devs = [bd[args.d]]
            except KeyError: parser.exit("Unknown device: " + args.d)
        if len(devs)==0: 
            parser.exit("No devices selected/found")
        



        ## ------------------------------------------------------
        ## calculate changes
        ## ------------------------------------------------------
        
        ## list devices
        if args.l:
            for cbd in devs: print(cbd if args.v else cbd.key)
            
            
            
        ## reset
        if args.r:
            bd.changed = False
            for cd in devs: cd.reset()


        ## undo
        if args.u:
            bd.changed = False
            try: 
                bd.profile_load('[last]')
            except KeyError: 
                parser.exit("Unknown profile: [last]")
            except PermissionError:
                parser.exit("profile file {} unknown or protected".format(bd._file))


        ## set absolute brightness
        if args.b != None:
            bd.changed = False
            try:
                if args.b > 2: args.b /= 100
                for cd in devs: cd.brightness = args.b
            except ValueError:
                parser.exit("Invalid brightness value {}".format(args.b))
            
        
        ## set incremental brightness
        if args.B != None:
            bd.changed = False
            try:
                if abs(args.B) > 2: args.B /= 100
                for cd in devs: cd.brightness += args.B
            except ValueError:
                parser.exit("invalid value for brightness: {}".format(args.B))
                   
                   
        ## set gamma
        if args.g != None:
            bd.changed = False       
            try:
                for cd in devs: cd.gamma = [float(x) for x in args.g.split(':')]
            except ValueError:
                parser.exit("invalid value for gamma: {}".format(args.g))
                    
                    
        ## set some screen to dark or back
        if args.D:
            bd.changed = False
            try:
                last = dict([(k,v.get('brightness',1)) for k,v in bd.profile_get('[last]').items()])
            except KeyError:
                last = dict([(d.key,1.0) for d in devs])
            for d in devs:
                d.brightness = 0.0 if d.brightness != 0 else last[d.key]
                
                
        ## set gamma by temperature
        if args.t != None:
            bd.changed = False
            try:
                temp = math.log10(int(args.t))
                if temp < 3: temp = 3
                if temp > 4.5: temp = 4.5
                if temp > 3.78:
                    temp = [1-(temp-3.78)*1.42,1-(temp-3.78)*0.74,1]
                else:
                    temp = [1,1+(temp-3.78)*.85,1+(temp-3.78)*1.68]
                for cd in devs: cd.gamma = temp
            except ValueError: parser.exit("invalid value for temperature: {}".format(args.t))
            
                    
        ## show changes in virtual mode
        if args.virtual:
            for cd in devs: print(cd)
                        
                        
                        
                        

        ## ------------------------------------------------------
        ## apply changes and save last state if necessary
        ## ------------------------------------------------------
        for cd in devs: cd.apply(args.hard)
        if bd.changed: bd.profile_save_last()





        ## ------------------------------------------------------
        ## Post processes
        ## ------------------------------------------------------
        
        ## show gui
        if args.gui:
            import src.gui
            from PyQt5 import QtWidgets
            app = QtWidgets.QApplication(sys.argv)
            src.gui.gui(bd).show()
            app.exec_()
            bd.read() 
    
        ## save profile
        if args.profile_save != None:      
            bd.profile_save(args.profile_save)
                
                
    
    
    
    
    
if __name__ == "__main__":
    run()

