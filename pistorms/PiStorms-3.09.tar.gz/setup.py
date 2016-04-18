#!/usr/bin/env python

from distutils.core import setup

setup(name='PiStorms',
    version='3.09',
    description='PiStorms libraries',
    author='mindsensors.com',
    author_email='contact@mindsensors.com',
    url='http://www.mindsensors.com',
    py_modules=['PiStorms', 'mindsensors', 'PiStormsCom', 'ps_messenger_check', 'scratch', 'rmap', 'rmapcfg'],
    data_files=[('mindsensors_images', ['btns_center.png', 'btns_left.png', 'btns_right.png', 'button.png', 'Exclamation-mark-icon.png', 'Pane1.png', 'dialogbg.png']),
    ('/etc/init.d', ['PiStormsDriver.sh', 'PiStormsBrowser.sh']),
    ('/home/pi/PiStorms/programs', ['00-About_Me.py', '00-Scratch_PiStorms.py', '00-RevertWiFiChanges.py', '00-TestInternetConn.py', '00-WiFi_Setup.py', '01-PopHeads.py', '01-TestKeyboard.py', '01-JesterControl.py', '02-SamTheEmotional.py', '01-CatchMike.py', '02-PyDog.py', '03-Swarm_Demo.py', '04-Motor-Degrees.py', '04-Motor-Demo.py', '04-Motor-Seconds.py', '04-Motor-ShowPos.py', '05-custom_i2c_test.py', '05-BatteryVolt.py', '06-SumoEyes.py', '06-touch_sensor.py', '04-GoButton.py', '04-HelloWorld.py', '09-Change_i2c_addr.py', '09-Explorer.py', '09-refresh.py', 'dog.jpg', 'dog.png', 'faceAwesome.png', 'faceClown.png', 'faceClown_eyeLeft.png', 'faceClown_eyeRight.png', 'faceClown_nose.png', 'faceHappy.png', 'faceScared2.png', 'Puppy_Dog_Barking.mp3', 'addresschange', 'smiley.png', 'black-square.png', 'lock.png', 'ulock.png', 'load.png', 'x_red.png', 'wifi_green.png', 'haarcascade_frontalface_default.xml']),
	('/home/pi/PiStorms/programs/tests', ['msg-to-screen.py', 'print-battery-voltage.py', 'psm-info.py', 'screen-test.py']),
	('/home/pi/Documents/Scratch Projects/PiStorms',['PiStorms-EV3AmbientLight.sb', 'PiStorms-EV3Color.sb', 'PiStorms-EV3Gyro.sb', 'PiStorms-EV3IRDistance.sb', 'PiStorms-EV3IRRemote.sb', 'PiStorms-EV3TouchSensor.sb', 'PiStorms-EV3Ultrasonic.sb', 'PiStorms-JoyStick.sb', 'PiStorms-MotorDemo.sb', 'PiStorms-NXTAmbientLight.sb', 'PiStorms-NXTColor.sb', 'PiStorms-NXTTouchSensor.sb', 'PiStorms-printing.sb', 'PiStorms-ReadEncoder.sb', 'PiStorms-RemoteRobot.sb', 'PiStorms-Sumoeyes.sb', 'PiStorms-Template.sb', 'PiStorms-TouchScreen.sb', 'PiStorms-TouchSensor.sb']),
    ('/usr/local/bin', ['pistorms-diag.sh', 'PiStormsBrowser.py', 'PiStormsDriver.py']),
	('/usr/share/raspberrypi-artwork', ['mindsensors-logo-BG.png', 'mindsensors-logo-Menu.png']),
    ('/home/pi/.config/autostart', ['tightvnc.desktop'])],
    install_requires=['mindsensors_i2c', 'mindsensorsUI', 'RPi.GPIO', 'imutils', 'wireless', 'wifi', 'cv2', 'swarmclient'],
    )