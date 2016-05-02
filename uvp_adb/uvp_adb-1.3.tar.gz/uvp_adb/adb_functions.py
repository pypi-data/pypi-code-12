# ===========================================
# adb_functions.py
# version 1.0 
#
# Core Ubiquiti phone class which uses adb to
# connect to phone and perform different functions 
#
# Written by Sajjad Ziyaei amiri (04/12/2016)
# ===========================================

from log_functions import *
import platform

class uvp_phone(object):
    
    #Initialization of global varibles in class 
    def __init__(self):
        self.Phone_IP = "127.0.0.1"
        self.adb_path = "C:\\adb"        
        self.ADB_PORT = 5555    #ADB port number 

        if "Windows" in platform.system() :
            self.apk_path = "\\APKs\\"
        elif "Linux" in platform.system() :
            self.apk_path = "/APKs/"

    
    # To set IP for phone - This function will validate if ip is pingable before setting it 
    def set_Phone_IP(self,ip):
        self.Phone_IP = ip
        if self._ip_validation() == 0 :
            UVP_log ("Phone IP is ONLINE ! ")
        else :
            UVP_error ("IP is not valid, exiting ...")
            return 1 # Return Error => need to exit
    
    # To set ADB path - This function will validate path to see if adb.exe exists or not
    def set_adb_path(self,path):
        if self._adb_path_validation() == 0 :    
            self.adb_path = path
        else :
            UVP_error ("ADB Path incorrect, exiting ...")
            return 1 # Return Error => need to exit

    # To APKs path for updating phones 
    def set_apk_path(self,path):
        self.apk_path = path

    def get_Phone_IP(self):
        return self.Phone_IP
    
    def get_adb_path(self):
        return self.adb_path

    def get_apk_path(self):
        return self.apk_path

    # This function will run adb command
    # First it will go to adb path to make sure adb.exe is reachable
    #This function will return shell output of resulted command 
    def _adb_run_shell_command(self,command,shell_on=False):
        import subprocess
        if shell_on == False:
            command = command.split()
        p = subprocess.Popen(command , shell=shell_on, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = p.communicate()[0]
        p.wait()
        return output
        
    def check_adb_daemon(self):
        # ADB daemon should run under supervisorctl 
        shell_output = self._adb_run_shell_command("pgrep adb")
        if shell_output == "":
            UVP_error ("ADB daemon is not running...")
            UVP_Warning ("ADB daemon is not running...")
            UVP_log ("Trying to start ADB daemon...")
            shell_output = self._adb_run_shell_command("sudo adb start-server")
            if "daemon started successfully" in shell_output:
                UVP_log ("Daemon started successfully!")
            else :
                UVP_error ("Can't start ADB daemon on this server")
                return 1 

    def restart_adb_daemon(self):
        UVP_log ("Killing ADB daemon...")
        shell_output = self._adb_run_shell_command("adb kill-server")
        self.check_adb_daemon()
                
    def try_socket_first (self):
        UVP_log("Testing socket to connect to Phone (" + self.get_Phone_IP() + ")")
        if self._run_socket_test() == 0:
            UVP_log ("Connection to "+ self.get_Phone_IP() + " via port ("+str(self.ADB_PORT)+") is alive!")
        else :
            UVP_error ("Connection to phone "+self.get_Phone_IP() + " via port ("+str(self.ADB_PORT)+") is rejected. \nMake sure IP address is correct. Then check for developer options to be on. Then check network Jitter and firewall port block")
            return 1 # Return Error => need to exit 

        
    # This function will connect to phone with provided IP address
    # Before using this function , you might want to use set_Phone_IP() to set ip for phone
    # Be careful , this function first check port 5555 and if it is open it will try to connect by adb.exe
    # So if port 5555 is closed to blocked by firewall or network is too slow or with high jitter it will consider
    # port 555 is closed. Look for timeout option in _check_socket() function.
    def adb_connect(self):
        UVP_log("ADB trying to connect to Phone (" + self.get_Phone_IP() + ")")
        shell_output = self._adb_run_shell_command("adb connect "+ self.get_Phone_IP())
        import time
        time.sleep(1)
        if "unable to connect" in shell_output :
            UVP_error ("Can't connect to phone (" + self.get_Phone_IP() + ") ...")
            return 1 # Return Error => need to exit
            
          
    # It will diconnect adb.exe from the phone.
    def adb_disconnect(self):
        adb_path = self.get_adb_path()
        phone_ip = self.get_Phone_IP()
        shell_output = self._adb_run_shell_command("adb disconnect "+str(phone_ip))
        UVP_log("ADB is disconnecting ...")
    
    # Try to connect 3 times after find device disconnected
    def try_to_connect_if_offline (self):
        count = 0
        import time
        while count < 3 :
            out = self._adb_run_shell_command ("adb devices")
            for line in out.split('\n'):
                if self.get_Phone_IP() in line :
                    out = line
                    if "offline" in out :
                        count += 1
                        UVP_log("Retrying to connect to phone ... Try "+ str(count))
                        self.adb_disconnect()
                        self.adb_connect()
                        #shell_output = self._adb_run_shell_command("adb connect "+ self.get_Phone_IP())
                    elif "unknown" in out :
                        count += 1
                        UVP_log("Trying to connect to phone ... Try "+ str(count))
                        self.adb_disconnect()
                        self.adb_connect()
                        #shell_output = self._adb_run_shell_command("adb connect "+ self.get_Phone_IP())
                    elif "device" in out:
                        return 0
                    time.sleep(1)

        UVP_error ("Can't connect to phone with ip ("+self.get_Phone_IP()+") after 3 tries. It seems it is offline")
        self.adb_disconnect()
        return 1 # Return Error => need to exit

        
    # This function asks user to input IP addresss 
    def ask_for_ip (self):
        input_result = raw_input ("Please enter IP address for target phone - Enter for defualt (10.100.105.116) : ")
        if input_result == "":
            self.set_Phone_IP("10.100.105.116")
        else :
            self.set_Phone_IP(input_result)
    
    # This function asks user to input adb path 
    def ask_for_adb_path(self):
        input_result2 = raw_input ("Please enter adb address - Press enter for default (c:\\adb) : ")
        if input_result2 == "":
            self.set_adb_path("c:\\adb")
        else :
            import os.path
            if os.path.isfile (input_result2+"\\adb.exe") == True :
                self.set_adb_path(input_result2)
                UVP_log ("ADB Path is correct and accessable")
            else :
                UVP_error ("adb.exe file is not accessible or does not exist")
                self.adb_disconnect()

    # This function asks user to input APK path 
    def ask_for_input_APK_dir(self):
        import os.path
        currect_path = os.getcwd()
        input_result2 = raw_input ("Please enter APKs dir - Press enter for default (\\APKs\\) : ")
        print input_result2
        if input_result2 == "":
            self.set_apk_path("\\APKs\\")
        else :
            self.set_apk_path(input_result2)
                
    def _adb_path_validation(self):     
        if "Windows" in platform.system() :
            adb_path = self.get_adb_path()
            if adb_path == "":    
                return "c:\\adb"
            else :
                import os.path
                if os.path.isfile (adb_path+"\\adb.exe") == True :
                    UVP_log ("ADB Path is correct and accessable")
                    return 0
                else :
                    UVP_error ("adb.exe file is not accessible or does not exist")
                    return 1
        else :
            return 0

    def _ping_result(self):
        Phone_IP = self.get_Phone_IP()
          
        if "Windows" in str(platform.system()):
            return self._adb_run_shell_command('ping -n 1 -w 1000 ' + Phone_IP)
        if "Linux" in str(platform.system()):
            return self._adb_run_shell_command('ping -c 1 -w 1000 ' + Phone_IP)
    
    def _ip_validation (self):
        Phone_IP = self.get_Phone_IP()
        output = self._ping_result()
        if "destination host unreachable" in output.decode('utf-8').lower() :
            #UVP_error ("Phone IP is NOT accessible ! ")
            return 1
        elif "timed out" in output.decode('utf-8').lower():
            #UVP_error ("Phone IP is NOT accessible ! ")
            return 1
        elif "Please check the name and try again" in output.decode('utf-8') or "Bad option" in output.decode('utf-8') or "Invalid argument" in output.decode('utf-8'):
            #UVP_error ( "Please check phone IP address entered. -> ")
            return 1 
        else:
            #UVP_log ("Phone IP is ONLINE ! ")
            return 0
     
    def _block_app (self, pkg_name, pkg):
        adb_path = self.get_adb_path()
               
        UVP_log("Blocking " + pkg_name + " is in process")
        shell_output = self._adb_run_shell_command("adb -s "+ self.get_ip_and_port() + " shell pm block " + pkg)
        if shell_output[0] == "*" or shell_output[0:4] == "error":
            UVP_Warning ("Connection Error - Device disconnected")
            return 2
        result = shell_output.split(": ")
        if result[1] == "false\r\r\n":
            UVP_Warning ("Error Blocking " + pkg_name)
            return 1 
        return 0
    
    def _unblock_app (self, pkg_name, pkg):
        adb_path = self.get_adb_path()    
               
        UVP_log("Unblocking " + pkg_name + " is in process")
        shell_output = self._adb_run_shell_command("adb -s "+ self.get_ip_and_port() + " shell pm unblock " + pkg)
        if shell_output[0] == "*" or shell_output[0:4] == "error":
            UVP_Warning ("Connection Error - Device disconnected")
            return 2
        result = shell_output.split(": ")
        if result[1] == "true\r\r\n":
            UVP_Warning ("Error Unblocking " + pkg_name)
            return 1 
        return 0
    
    def block_unwanted_apps(self):
        resultsum = 0 
        resultsum += resultsum + self._block_app ("Sound Recorder","com.android.soundrecorder")
        resultsum += resultsum + self._block_app ("Gallery 3D","com.google.android.gallery3d")
        resultsum += resultsum + self._block_app ("Talk App","com.google.android.talk")
        resultsum += resultsum + self._block_app ("Download UI","com.android.providers.downloads.ui")
        resultsum += resultsum + self._block_app ("Keep App","com.google.android.keep")
        resultsum += resultsum + self._block_app ("Music","com.google.android.music")
        resultsum += resultsum + self._block_app ("Maps","com.google.android.apps.maps")
        resultsum += resultsum + self._block_app ("Magazines","com.google.android.apps.magazines")
        resultsum += resultsum + self._block_app ("Calendar","com.google.android.calendar")
        resultsum += resultsum + self._block_app ("Chrome Web Browser","com.android.chrome")
        resultsum += resultsum + self._block_app ("Books","com.google.android.apps.books")
        resultsum += resultsum + self._block_app ("Videos","com.google.android.videos")
        resultsum += resultsum + self._block_app ("TalkBack","com.google.android.marvin.talkback")
        resultsum += resultsum + self._block_app ("Widget","com.google.android.apps.genie.geniewidget")
        resultsum += resultsum + self._block_app ("GooglePlus","com.google.android.apps.plus")
        resultsum += resultsum + self._block_app ("googleGames","com.google.android.play.games")
        resultsum += resultsum + self._block_app ("GMail","com.google.android.gm")
        resultsum += resultsum + self._block_app ("Email","com.android.email")
        resultsum += resultsum + self._block_app ("Youtube","com.google.android.youtube")
        resultsum += resultsum + self._block_app ("Docs","com.google.android.apps.docs")
        resultsum += resultsum + self._block_app ("Google Contacts","com.google.android.syncadapters.contacts")
        resultsum += resultsum + self._block_app ("Filemanager","com.cyanogenmod.filemanager")
        resultsum += resultsum + self._block_app ("Google Login","com.google.android.gsf.login")
        resultsum += resultsum + self._block_app ("Google Play","com.android.vending")
        resultsum += resultsum + self._block_app ("Exchange","com.android.exchange")
        resultsum += resultsum + self._block_app ("Google Services","com.google.android.gms")
        resultsum += resultsum + self._block_app ("Google Voice Search","com.google.android.googlequicksearchbox")
        
        input_result = raw_input ("Do you want to block setting menu (yes/no) ?")
        if input_result == "yes":
            resultsum += resultsum + self._block_app ("Setting","com.android.settings")
        
        if resultsum == 0:
            UVP_log (" ===== Blocking Finished Successfully =====")
            return 0
        else:
            UVP_Warning (" Blocking Finished with Errors . One or more apps didn't blocked successfully. To make please sure check the phone. If warning is because of Google Services App . Make sure to login to Google Setting and disable all of options. Location and data sending should be desabled. These setting are configred in Startup configuration of device.Try to disable those options and try again.")
            return 1
    
    
    def unblock_apps(self):
        resultsum = 0 
        resultsum += resultsum + self._unblock_app ("Sound Recorder","com.android.soundrecorder")
        resultsum += resultsum + self._unblock_app ("Gallery 3D","com.google.android.gallery3d")
        resultsum += resultsum + self._unblock_app ("Talk App","com.google.android.talk")
        resultsum += resultsum + self._unblock_app ("Download UI","com.android.providers.downloads.ui")
        resultsum += resultsum + self._unblock_app ("Keep App","com.google.android.keep")
        resultsum += resultsum + self._unblock_app ("Music","com.google.android.music")
        resultsum += resultsum + self._unblock_app ("Maps","com.google.android.apps.maps")
        resultsum += resultsum + self._unblock_app ("Magazines","com.google.android.apps.magazines")
        resultsum += resultsum + self._unblock_app ("Calendar","com.google.android.calendar")
        resultsum += resultsum + self._unblock_app ("Chrome Web Browser","com.android.chrome")
        resultsum += resultsum + self._unblock_app ("Books","com.google.android.apps.books")
        resultsum += resultsum + self._unblock_app ("Videos","com.google.android.videos")
        resultsum += resultsum + self._unblock_app ("TalkBack","com.google.android.marvin.talkback")
        resultsum += resultsum + self._unblock_app ("Widget","com.google.android.apps.genie.geniewidget")
        resultsum += resultsum + self._unblock_app ("GooglePlus","com.google.android.apps.plus")
        resultsum += resultsum + self._unblock_app ("googleGames","com.google.android.play.games")
        resultsum += resultsum + self._unblock_app ("GMail","com.google.android.gm")
        resultsum += resultsum + self._unblock_app ("Email","com.android.email")
        resultsum += resultsum + self._unblock_app ("Youtube","com.google.android.youtube")
        resultsum += resultsum + self._unblock_app ("Docs","com.google.android.apps.docs")
        resultsum += resultsum + self._unblock_app ("Google Contacts","com.google.android.syncadapters.contacts")
        resultsum += resultsum + self._unblock_app ("Filemanager","com.cyanogenmod.filemanager")
        resultsum += resultsum + self._unblock_app ("Google Login","com.google.android.gsf.login")
        resultsum += resultsum + self._unblock_app ("Google Play","com.android.vending")
        resultsum += resultsum + self._unblock_app ("Google Quick Search Widget","com.google.android.googlequicksearchbox")
        resultsum += resultsum + self._unblock_app ("Exchange","com.android.exchange")
        resultsum += resultsum + self._unblock_app ("Google Services","com.google.android.gms")
        resultsum += resultsum + self._unblock_app ("Google Voice Search","com.google.android.googlequicksearchbox")
        resultsum += resultsum + self._unblock_app ("Setting","com.android.settings")
        
        if resultsum == 0:
            UVP_log (" ===== Unblocking Finished Successfully =====")
            return 0
        else:
            UVP_Warning (" Unblocking Finished with Errors")
            return 1
    
    # Check if adb.exe exists or not 
    def _validate_file_exist (self,filepath):
        import os.path
        if os.path.isfile (filepath) == True :
            return 0
            UVP_log (filepath + " path is correct and accessable")
        else :
            UVP_error (filepath + " is not accessible or does not exist")
            return 1 
            self.adb_disconnect()
    
    def _install_apk (self,filename):
        adb_path = self.get_adb_path()
        apk_dir = self.get_apk_path()
        UVP_log("Installing " + filename + " is in process ...")
        import os.path
        currect_path = os.getcwd()
        apk_path = currect_path + apk_dir + filename
        self._validate_file_exist (apk_path)
        
        shell_output = self._adb_run_shell_command("adb -s "+ self.get_ip_and_port() + " install -r " + apk_path)
        
        if "INSTALL_FAILED_VERSION_DOWNGRADE" in shell_output:
            UVP_Warning (filename + " installation failed because your current APK version is outdated.")
            UVP_Warning ("Please download lastest version from (http://dl.ubnt.com/unifi/static/uvp/"+filename+") and put in APKs folder.")
            UVP_Warning ("Also it might happen when your phone already is upgraded with Controller.")
            return 1 
        elif "Success" not in shell_output: 
            UVP_error (filename + " installation failed with unknown errors : (See Below)")
            print shell_output
            return 1
        else :
            UVP_log (filename + " has been installed successfully")
            return 0 
    
    def update_phone_with_apks(self):
        UVP_log("Updating process starting !")
        err= 0
        err += self._install_apk("SipService.apk")
        err += self._install_apk("UnifiPhone.apk")
        err += self._install_apk("Google_pdf_reader.apk")
        #err += self._install_apk("Latitude_UVP.apk")
        err += self._install_apk("MyIP.apk")
        if err == 0:
            UVP_log("Updating completed successfully !")
        else :
            UVP_Warning ("Updating finished with errors ...")

    
    def get_ip_and_port(self):
        string = self.get_Phone_IP() + ":" + str(self.ADB_PORT)
        return string
        
    def clear_history (self):
        PHONE_IP = self.get_Phone_IP()
        
        shell_output = self._adb_run_shell_command("adb -s "+ self.get_ip_and_port() + " shell pm clear com.android.providers.contacts")
        
        if "Success" not in shell_output:
            UVP_log ("Clearing call history of "+PHONE_IP+ " Failed!")
            return 1
        UVP_log ("Clearing call history of "+PHONE_IP+ " was successfull!")
    
    def bring_latitude_app (self):
        PHONE_IP = self.get_Phone_IP()
        adb_path = self.get_adb_path()        
        
        shell_output = self.adb_disconnect()
        shell_output = self.adb_connect()
        shell_output = self._adb_run_shell_command("adb -s "+ self.get_ip_and_port() + " shell am start -n com.percipia.latitude/.MainActivity")
        if "Error" in shell_output:
            UVP_log ("Bringing up Latitute app on "+PHONE_IP+ " failed!")
            shell_output = self.adb_disconnect()
            return 1 
        UVP_log ("Bringing up Latitute app on "+PHONE_IP+ " was successfull!")
        shell_output = self.adb_disconnect()
        return 0
    
        
    # Return maximum respond time from ping 
    def _phone_ping_respond_time (self):
        Phone_IP = self.get_Phone_IP()
        DEFAUT_TIMEOUT = 300
        output = self._ping_result()
        
         
        if "Windows" in platform.system() :
            if "Lost = 0 (0% loss)" in output and "TTL=" in output :
                    network_delay = int(output.split("Maximum = ")[1].split("ms")[0])
                    if network_delay < 10 :
                        return network_delay+10,1   #If network is too fast we use 10 milli-seconds 
                    return network_delay*1.15,1     #Add 15% to be sure of result 
            else :
                return DEFAUT_TIMEOUT,0    #this ip is not pinagble for has loss 
        elif "Linux" in platform.system():
            if "0% packet loss" in output and "ttl=" in output :
                    network_delay = int(float(output.split("rtt min/avg/max/mdev = ")[1].split(" ms")[0].split('/')[2]))
                    if network_delay < 10 :
                        return network_delay+10,1   #If network is too fast we use 10 milli-seconds 
                    return network_delay*1.15,1     #Add 15% to be sure of result 
            else :
                return DEFAUT_TIMEOUT,0    #this ip is not pinagble for has loss 
            
    # check port 5555 for connection with timeout 
    def _check_socket (self,TIMEOUT):
        ip = self.get_Phone_IP() 
        import socket;    
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        #Convert to seconds        
        sock.settimeout(TIMEOUT/1000.0)
        
        #Check the Socket for connection
        result = sock.connect_ex((ip,self.ADB_PORT))
        sock.close()       
       
        if result == 0:
            return 0     #alive !
        else:
            return 1     #can't connect
    
    # Increase timeout and check respond time and use it in check_socket() as timeout.
    def _run_socket_test (self) :
        TIMEOUT,intruption = self._phone_ping_respond_time()
        UVP_log ("Network timeout is set as : "+str(TIMEOUT*1.5)+" ms")
        result = self._check_socket (TIMEOUT*1.5)
        if result == 0:
            return 0     #successfull
        else:       
            return 1     #error

    def start_logcat(self):
        import subprocess
        logfile = open('phone.log', 'w')
        proc = subprocess.Popen(['adb', 'logcat'], stdout=logfile)
    
    
    def take_screenshot(self):
        # First make sure adb is connected 
        self._adb_run_shell_command ("adb -s "+ self.get_ip_and_port() + " shell screencap -p /sdcard/screen.png")
        self._adb_run_shell_command ("adb -s "+ self.get_ip_and_port() + " pull /sdcard/screen.png")
        self._adb_run_shell_command ("adb -s "+ self.get_ip_and_port() + " shell rm /sdcard/screen.png")
        if "Linux" in platform.system():
            import os 
            os.rename("screen.png", "/var/tmp/screen.png")
        
    def is_DND_on(self):
        # Before using this function make sure adb connected
        import png,os
        if "Linux" in platform.system():
            f = open('/var/tmp/screen.png', 'rb')
        elif "Windows" in platform.system():
            f = open('screen.png', 'rb')
        r=png.Reader(file=f)
        
        w, h, pixels, metadata = r.read()
        
        for pix in pixels:
            colour = [pix[0], pix[1], pix[2], pix[3]]
            break
        
        f.close()
        if "Linux" in platform.system():
            os.remove('/var/tmp/screen.png')
        elif "Windows" in platform.system():
            os.remove('screen.png')
        del r
        
        if colour == [255,0,0,255]:
            UVP_log ("For "+ self.get_Phone_IP()+"-> DND is on ")
            return True
        else :
            UVP_log ("For "+ self.get_Phone_IP()+"-> DND is off ")
            return False
    
    def get_phone_model(self):
        out =  self._adb_run_shell_command ("adb devices -l")
        phone_model = out.split('model:')[1].split(' ')[0]
        #print phone_model
        UVP_log ("Phone model for "+ self.get_Phone_IP()+" is "+phone_model)
        if phone_model == "UVP":
            return "UVP"
        elif phone_model == "UVP_Executive":
            return "UVP_Executive"
    
    def bring_uvp_main_screen (self):
        out = self._adb_run_shell_command ("adb -s "+ self.get_ip_and_port() + " shell am start com.ubnt.uvp/com.ubnt.unifi.phone.MainActivity")
        if "Warning" not in out:
        	import time 
        	time.sleep (10)
    
    def turn_off_dnd(self):
        self.take_screenshot()
        if self.is_DND_on() :
            self.bring_uvp_main_screen()
            phone_model = self.get_phone_model()
            if phone_model == "UVP_Executive":
                self._adb_run_shell_command ("adb -s "+ self.get_ip_and_port() + " shell input tap 1000 60")
                self._adb_run_shell_command ("adb -s "+ self.get_ip_and_port() + " shell input tap 915 173")
                UVP_log ("DND has been truned off on for " + phone_model + "("+ self.get_Phone_IP() +")")

            elif phone_model == "UVP":
                self._adb_run_shell_command ("adb -s "+ self.get_ip_and_port() + " shell input tap 600 100")
                # The second touch point for UVP model was very tricky to find
                self._adb_run_shell_command ("adb -s "+ self.get_ip_and_port() + " shell input tap 597 234")        
                # I dont have test phone now to test with buttons 
                #self._adb_run_shell_command ("adb -s "+ self.get_ip_and_port() + " shell input keyevent 66")
                #self._adb_run_shell_command ("adb -s "+ self.get_ip_and_port() + " shell input keyevent 20")
                #self._adb_run_shell_command ("adb -s "+ self.get_ip_and_port() + " shell input keyevent 66")
                UVP_log ("DND has been truned off on for " + phone_model + "("+ self.get_Phone_IP() +")")
            
    def get_mac_address(self):
        return self._adb_run_shell_command ("adb -s "+ self.get_ip_and_port() + " shell netcfg | grep eth0 | awk {'print $5'}",shell_on=True)

    def configure_controller(self):
        import time
        self.bring_uvp_main_screen()
        time.sleep(5)
        phone_model = self.get_phone_model()
        maj_uvp_version = self._get_uvp_version ().split('.')[0]
        
        # Clear UVP setting 
        self._adb_run_shell_command ("adb -s "+ self.get_ip_and_port() + " shell pm clear com.ubnt.uvp")
        # Open Setting 
        self._adb_run_shell_command ("adb -s "+ self.get_ip_and_port() + " shell am force-stop com.ubnt.uvp")
        time.sleep(1)
        self._adb_run_shell_command ("adb -s "+ self.get_ip_and_port() + " shell am start com.ubnt.uvp/com.ubnt.unifi.phone.SettingsActivity")
        time.sleep(1)
        
        if phone_model == "UVP_Executive":
            if maj_uvp_version == '4':
                # Select controller
                self._adb_run_shell_command ("adb -s "+ self.get_ip_and_port() + " shell input tap 143 205")
                time.sleep(1)
            elif maj_uvp_version == '5':
                # Select controller
                self._adb_run_shell_command ("adb -s "+ self.get_ip_and_port() + " shell input tap 111 254")
                time.sleep(1)
                
            # Select Controller URL 
            self._adb_run_shell_command ("adb -s "+ self.get_ip_and_port() + " shell input tap 141 248")
            time.sleep(1)
            # Select text 
            self._adb_run_shell_command ("adb -s "+ self.get_ip_and_port() + " shell input tap 297 139")
            time.sleep(1)
            # Input Text 
            self._adb_run_shell_command ("adb -s "+ self.get_ip_and_port() + " shell input text http://10.100.105.131:8080/inform")
            time.sleep(2)
            # Click Ok
            self._adb_run_shell_command ("adb -s "+ self.get_ip_and_port() + " shell input tap 655 207")
            time.sleep(1)
            # Back Button
            self._adb_run_shell_command ("adb -s "+ self.get_ip_and_port() + " shell input tap 382 572")
            time.sleep(1)
            self.bring_uvp_main_screen()

            #UVP_log ("DND has been truned off on for " + phone_model + "("+ self.get_Phone_IP() +")")
            pass
    
    def _get_uvp_version(self):
        ver = self._adb_run_shell_command ("adb -s "+ self.get_ip_and_port() + " shell dumpsys package com.ubnt.uvp | grep versionName",shell_on=True).split('=')[1]
        UVP_log("UVP software version is " + ver)
        return ver
        
    