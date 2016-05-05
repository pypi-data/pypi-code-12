# coding=utf-8
'''
Created on 23.07.2014

@author: joerg


open points:
+ gamma by temperature
+ docu. Hints at toolcase.org
 - Fine control shift/ctrl-modifications for slider key shortcuts
 - direct access for profiles starting with a number 
+ upload to PyPl / github ??
'''
#pyrcc5 -o res.py res.qrc

import math, re

from PyQt5 import QtGui, QtCore, QtWidgets as Qw
from src.res import qInitResources

class gui(Qw.QMainWindow):
    '''
    classdocs
    '''

    all = '[all]'
    _off = [0.01,0.05,0.2]
    _fac = [1.025,1.1,1.25]
    
    ## Not used at the moment, since they are visible in the menus
    hlp = "Some keyboard short cuts:<br/>" \
    + "<b>ESC</b>: reset to values at program start<br/>" \
    + "<b>D B</b>: darker / brighter<br/>" \
    + "<b>N M</b>: less / more contrast<br/>" \
    + "<b>I O P J K L</b>: change the color channels individual<br/>" \
    + "<b>F5</b>: reread values from system (xrandr)<br/>" \
    + "<b>R</b>: reset to 100% and gamma 1 for all colors"

    def __init__(self, devices):
        """init user interface"""
        self.devices = devices
        
        ## Window itself
        Qw.QMainWindow.__init__(self)
        self.setMinimumHeight(400)
        self.setMinimumWidth(250*devices.count())
        self.setWindowTitle(self.devices._title)
        self.setWindowIcon(QtGui.QIcon(':/img/logo'))
        
        ## Content
        tmp = Qw.QWidget()
        lay = Qw.QVBoxLayout(tmp)
        lay.setSpacing(0)
        #Qt4 lay.setMargin(0)
        lay.addWidget(self.sc_widgets())
        self.devices.profile_save("[current]") ## current values at startup
        
        ## separator
        frm = Qw.QFrame()
        frm.setFrameShape(Qw.QFrame.HLine)
        lay.addWidget(frm)
        
        ## command bar at the bottom
        lay.addWidget(self.bar_widget())
        self.setCentralWidget(tmp)
        self.profiles.setCurrentIndex(self.profiles.findText("[current]"))        
        self.profiles.currentIndexChanged.connect(self.pload)
        
        ## add menus
        self.mnu()
        
        ## Timer for auto refresh
        ## disabled at start since it blocks the system/cursor .. for a short moment
        self.tim = QtCore.QTimer()
        self.tim.setSingleShot(False)
        self.tim.timeout.connect(self.refresh)

        

    def mnu(self):
        mb = self.menuBar()
        tmp = [('Exit',self.close,'Ctrl+W',':/img/exit',None)]
        self.mnu_build(mb,'&File', tmp)
        
        tmp = [('Brighter',lambda x:self.cmd_br(+self.off(),self.all),'B',':/img/br_increase',None),
               ('Darker',lambda x:self.cmd_br(-self.off(),self.all),'D',':/img/br_decrease',None),
               ('More contrast',lambda x:self.cmd_cnt(1*self.fac(),self.all),'M',':/img/cnt_increase',None),
               ('Less contrast',lambda x:self.cmd_cnt(1/self.fac(),self.all),'N',':/img/cnt_increase',None),
               (u'Red ↗',lambda x:self.cmd_col(1*self.fac(),self.all,0),'I',None,None),
               (u'Red ↘',lambda x:self.cmd_col(1/self.fac(),self.all,0),'J',None,None),
               (u'Green ↗',lambda x:self.cmd_col(1*self.fac(),self.all,1),'O',None,None),
               (u'Green ↘',lambda x:self.cmd_col(1/self.fac(),self.all,1),'K',None,None),
               (u'Blue ↗',lambda x:self.cmd_col(1*self.fac(),self.all,2),'P',None,None),
               (u'Blue ↘',lambda x:self.cmd_col(1/self.fac(),self.all,2),'L',None,None),
               (None,None,None,None,None),
               ('Reset to inital values',self.fullreset,'ESC',':/img/reset',"Reset to the values at program start"),
               ('Full reset (100% / 1)',lambda x: self.cmd_reset(self.all),'R',None,"Reset to 100% and Gamma 1"),
               ('Refresh',self.refresh,'F5',':/img/refresh',"Reread values from system"),
               ]
        mnu = self.mnu_build(mb, '&Channels', tmp)
        act = self.mnu_itm_build(mnu, 'Auto refresh', None, None, None,None)
        act.setCheckable(True)
        act.toggled.connect(self.timer_activate)
        

        tmp = [('About',self.about,'A',':/img/info',"Show a short help about keyboard shortcuts"),
               ]
        self.mnu_build(mb, '&Help', tmp)
        
        
    def mnu_build(self,menubar,lab,items):
        if isinstance(lab,Qw.QMenu):
            mnu = lab
        else:
            mnu = menubar.addMenu(lab)
        for lab,slt,key,img,tt in items: self.mnu_itm_build(mnu,lab,slt,key,img,tt)
        return mnu
        
    def mnu_itm_build(self,mnu,lab,slt,key,img,tt):
        if lab == None:
            return mnu.addSeparator()
        if img != None:
            act = mnu.addAction(QtGui.QIcon(img),lab)
            act.setIconVisibleInMenu(True)
        else:
            act = mnu.addAction(lab)

        if key != None: act.setShortcut(key)
        if tt:  act.setStatusTip(tt)
        if slt: act.triggered.connect(slt)

        return act
            
        




    def refresh(self):
        self.devices.read()
        for cd in self.devices: 
            lv = self.scs[cd.key].values
            cv = cd.values
            if abs(lv['brightness']-cv['brightness']) > 0.01: self.scs[cd.key].bright.set(cv['brightness'])
            for i in range(3):
                if  abs(lv['gamma'][i] - cv['gamma'][i]) > 0.03: self.scs[cd.key].gamma[i].set(cv['gamma'][i])


    def timer_activate(self,val):
        if val:
            self.tim.start(1000)
        else:
            self.tim.stop()

    def off(self):
        md = Qw.QApplication.keyboardModifiers()
        if md == QtCore.Qt.ShiftModifier: return self._off[0]
        if md == QtCore.Qt.ControlModifier: return self._off[2]
        return self._off[1]

    def fac(self):
        md = Qw.QApplication.keyboardModifiers()
        if md == QtCore.Qt.ShiftModifier: return self._fac[0]
        if md == QtCore.Qt.ControlModifier: return self._fac[2]
        return self._fac[1]


    def keyPressEvent(self,evnt):
        ## Hint: This code stays (even if it already is used in menu) for the Shift/Ctrl-Modifications
        if evnt.key() == QtCore.Qt.Key_B: self.cmd_br(+self.off(),self.all)
        elif evnt.key() == QtCore.Qt.Key_D: self.cmd_br(-self.off(),self.all)
        elif evnt.key() == QtCore.Qt.Key_U: self.cmd_br(+self.off(),self.all)
        elif evnt.key() == QtCore.Qt.Key_H: self.cmd_br(-self.off(),self.all)
        elif evnt.key() == QtCore.Qt.Key_M: self.cmd_cnt(1*self.fac(),self.all)
        elif evnt.key() == QtCore.Qt.Key_N: self.cmd_cnt(1/self.fac(),self.all)
        elif evnt.key() == QtCore.Qt.Key_P: self.cmd_col(1*self.fac(),self.all,2)
        elif evnt.key() == QtCore.Qt.Key_L: self.cmd_col(1/self.fac(),self.all,2)
        elif evnt.key() == QtCore.Qt.Key_O: self.cmd_col(1*self.fac(),self.all,1)
        elif evnt.key() == QtCore.Qt.Key_K: self.cmd_col(1/self.fac(),self.all,1)
        elif evnt.key() == QtCore.Qt.Key_I: self.cmd_col(1*self.fac(),self.all,0)
        elif evnt.key() == QtCore.Qt.Key_J: self.cmd_col(1/self.fac(),self.all,0)
        elif evnt.key() in range(48,58):
            self.pload_num(evnt.key()-48)
        else:
            #print 'key',evnt.key(), int(evnt.key())
            Qw.QMainWindow.keyPressEvent(self,evnt)
    
    def sc_widgets(self):
        """Init a widget for every screen"""
        self.scs = {}
        self.init_values = {}
        wid = Qw.QWidget()
        lay = Qw.QHBoxLayout(wid)

        for sc in self.devices:
            tmp = widget_sc(sc)
            tmp.bright.set(sc.brightness)
            for i in range(3): tmp.gamma[i].set(sc.gamma[i])
            tmp.sigChanged.connect(self.sc_changed)
            self.scs[sc.key] = tmp
            self.init_values[sc.key] = sc.values
            lay.addWidget(tmp)

        return wid
    
    
    
    def sc_changed(self,key,br,r,g,b):
        """ callback if a slider of the screens has changed -> commit to devices"""
        cs = self.devices[str(key)]
        cs.gamma = [r,g,b]
        cs.brightness = br
        cs.apply(True)
        
            

    def bar_widget(self):
        """A horizontal widget for the 'other' stuff at the bottom"""
        wid = Qw.QWidget()
        lay = Qw.QHBoxLayout(wid)
        lay.setSpacing(0)
        lay.setContentsMargins(0,0,0,0)

        ## Various thingsCommand         
        lay.addWidget(self.cmd_widget())
        lay.addStretch()
        lay.addWidget(self.profile_widget())
        lay.addStretch()
        lay.addWidget(self.remaining_widget())
        
        return wid

    
    
    def remaining_widget(self):
        """ a widget for remianing commands"""
        tmp = Qw.QWidget()
        lay = Qw.QGridLayout(tmp)
        lay.setSpacing(0)
        lay.addWidget(label(' ',None,12,True),0,0,1,2)
        lay.addWidget(button(QtGui.QIcon(':/img/refresh'), self.refresh,'Reread values from system'),1,0)
        lay.addWidget(button(QtGui.QIcon(':/img/reset'),self.fullreset,'Reset to the values before starting this application'),1,1)
        lay.addWidget(button(QtGui.QIcon(':/img/info'), self.about,'about'),2,0)
        lay.addWidget(button(QtGui.QIcon(':/img/exit'), lambda x: self.close(),'Exit Brightness'),2,1)
        return tmp

    
    def fullreset(self):
        """ resets all value to those at apllication start"""
        for k,sc in self.scs.items():
            sc.wait = True
            sc.bright.set(self.init_values[k]['brightness'])
            for i in range(3): sc.gamma[i].set(self.init_values[k]['gamma'][i])
            sc.wait = False
        
    
    def about(self):
        """ shows general 'about' infos """
        with self.devices as sd: 
            txt = u"{} - Version {} ({})<br/>" \
            + "<br/><b>{}</b><br/><br/>" \
            + "Copyright: <a href='mailto:{}?subject={}'>{}</a>; license: {}<br/>" \
            + "<b>Help</b> and more on <a href='{}'>{}</a><br/><br/>" \
            + "Currently used file for profiles: '<a href='file://{}'>{}</a>'"
            txt = txt.format(sd._name, sd._version,sd._date,
                             sd._descr,
                                                          sd._email,sd._title,sd._author,sd._license,
                             sd._url,re.sub('^.*//(.*?)/.*$','\\1',sd._url),
                             sd.file,sd.file)
            Qw.QMessageBox.about(self,sd._title,txt)
        
    
    ## Not used at the moment, since they are visible in the menus
    def help(self):
        """ shows a short help for the gui """
        Qw.QMessageBox.about(self,self.devices._title,self.hlp)


    
    def cmd_widget(self):
        """ a block of commands: brightness, contrast, reset"""
        wid = Qw.QWidget()
        lay = Qw.QGridLayout(wid)
        lay.setSpacing(0)

        lay.addWidget(label('Screen commands',None,12,True),0,0,1,5)
        lay.addWidget(Qw.QLabel('Apply to'),1,0,1,2)
        self.sc_sel = Qw.QComboBox()
        self.sc_sel.addItems(['[all]'] + [x.key for x in self.devices])
        
        lay.addWidget(self.sc_sel,1,2,1,3)
        lay.addWidget(button(QtGui.QIcon(':/img/reset'),lambda x:self.cmd_reset(self.sc_sel.currentText()),'reset to 100% & gamma 1'),2,4,1,1)
        lay.addWidget(button(QtGui.QIcon(':/img/br_decrease'), lambda x:self.cmd_br( -self.off(), self.sc_sel.currentText()),'darker'),2,0,1,1)
        lay.addWidget(button(QtGui.QIcon(':/img/br_increase'), lambda x:self.cmd_br( +self.off(), self.sc_sel.currentText()),'brighter'),2,1,1,1)
        lay.addWidget(button(QtGui.QIcon(':/img/cnt_decrease'),lambda x:self.cmd_cnt(1/self.fac(),self.sc_sel.currentText()),'lower contrast'),2,2,1,1)
        lay.addWidget(button(QtGui.QIcon(':/img/cnt_increase'),lambda x:self.cmd_cnt(1*self.fac(),self.sc_sel.currentText()),'higher contrast'),2,3,1,1)
        
        return wid


    
    def cmd_reset(self,dev):
        """ reset the selected screens to 100% & gamm 1"""
        for sc in self.scs.values():
            sc.wait = True
            sc.bright.set(1)
            for i in range(3): sc.gamma[i].set(1)
            sc.wait = False

    
    def cmd_br(self,delta,dev):
        """ changes the brightness of the selected screens by a given delta """
        for k,sc in self.scs.items():
            if k == dev or dev == '[all]': sc.bright.set(sc.bright.get()+delta)
    

    def cmd_col(self,fac,dev,col):
        """ changes the brightness of the selected screens by a given delta """
        for k,sc in self.scs.items():
            if k == dev or dev == '[all]':sc.gamma[col].set(sc.gamma[col].get()*fac)


    def cmd_cnt(self,fac,dev):
        """ changes the brightness of the selected screens by a given factor """
        for k,sc in self.scs.items():
            if k == dev or dev == '[all]':
                sc.wait = True
                for i in range(3): sc.gamma[i].set(sc.gamma[i].get()*fac)
                sc.wait = False

    
    
    def profile_widget(self):
        """ widget for profile operations"""
        ## basics
        wid = Qw.QWidget()
        lay = Qw.QGridLayout(wid)
        lay.setSpacing(0)
        
        ## title and selection box
        lay.addWidget(label('Profiles',"saved in '{}'".format(self.devices.file),12,True),0,0,1,4)
        self.profiles = Qw.QComboBox()
        self.plist() ## load them
        lay.addWidget(self.profiles,1,0,1,4)
        
        ## the commands itself
        for i,c in [('load',self.pload),('save',self.psave),('saveas',self.psaveas),('delete',self.pdelete)]:
            lay.addWidget(button(QtGui.QIcon(':/img/' + i),c,i))

        return wid
    
    def plist(self):
        """load saved profiles"""
        self.profiles.clear()
        for sc in sorted(self.devices.profile_list()): self.profiles.addItem(sc)
        
    
    def pload(self,a):
        """load the selected profile"""
        tmp = self.profiles.currentText()
        if tmp=="": return
        tmp = self.devices.profile_get(tmp)
        for k,sc in self.scs.items():
            if k not in tmp: continue
            cur = tmp[k]
            sc.bright.set(cur['brightness'])
            for i in range(3): sc.gamma[i].set(cur['gamma'][i])
            


    def pload_num(self,n):
        """ n is a number between 0 and 9. Will load the first profile with name starting with this number"""
        try:
            for x in self.devices.xml.findall("./profile"):
                if x.get('key')[0:2] == str(n) + ' ':
                    self.profiles.setCurrentIndex(self.profiles.findText(x.get('key')))
                    return
        except IOError: pass


    def psave(self,a):
        """save current settings at the current profile"""
        tmp = self.profiles.currentText()
        if tmp=="": return
        self.devices.profile_save(tmp)


    def psaveas(self,a):
        """ save current settings in a new profile"""
        txt, ok = Qw.QInputDialog.getText(self,"Profiles","Name for the new profile")
        if not ok or str(txt).strip() == '': return
        self.devices.profile_save(txt)
        self.plist()
        self.profiles.setCurrentIndex(self.profiles.findText(txt))
        

    def pdelete(self,a):
        """delete selected profile after confirmation"""
        tmp = self.profiles.currentText()
        if tmp=="": return
        QM = Qw.QMessageBox
        if QM(QM.Question, "Profiles","Delete profile '{}'".format(tmp),QM.Yes | QM.No).exec_() == QM.No: return
        self.devices.profile_delete(tmp)
        self.plist()
        



class widget_sc(Qw.QWidget):
    '''
    Widget for a single screen
    '''
    
    sigChanged = QtCore.pyqtSignal(str,float,float,float,float)
    
    def __init__(self,sc):
        ## Basics
        Qw.QWidget.__init__(self)
        self._wait = False
        self._changed = True
        self.key = sc.key
        self.lay = Qw.QGridLayout(self)
        self.lay.setSpacing(0)
        self.lay.setContentsMargins(0,0,0,0)
        self.lay.setAlignment(QtCore.Qt.AlignHCenter)

        ## Title
        tmp = label(sc.key,None,16,sc.primary,QtCore.Qt.AlignCenter)
        if sc.primary: tmp.setToolTip('Primary screen')
        
        self.lay.addWidget(tmp,0,0,1,4)
        
        ## slider for the brightness
        self.bright = percSlider(0,2,1,'Bright:Brightness in percent')
        self.bright.sigChanged.connect(lambda x: self.sigChanged_emit())
        self.lay.addWidget(self.bright,1,0,1,1)
        
        ## three sliders for the gamma colors
        self.gamma = []
        for i in range(0,3):
            tmp = logSlider(0.1,10,1,['red:part of the color/contrast','green:part of the color/contrast','blue:part of the color/contrast'][i])
            tmp.sigChanged.connect(lambda x: self.sigChanged_emit())
            self.lay.addWidget(tmp,1,1+i,1,1)
            self.gamma.append(tmp)
        
        
        
    @property
    def wait(self): return self._wait
    
    @wait.setter
    def wait(self,val):
        self._wait = val
        if not val: self.sigChanged_emit() ## to 're send' the missed things

    @property
    def values(self):
        """ returns a dict with all values """
        return {'key': self.key, 'gamma':[self.gamma[0].get(),self.gamma[1].get(),self.gamma[2].get()], 'brightness': self.bright.get()}

        
    def sigChanged_emit(self):
        """ emit the widget signal 'Changed' (if not wait is active)"""
        if self._wait: # used to allow multiple values with a single commit
            self._changed = True
        else:
            self.sigChanged.emit(self.key,self.bright.get(),self.gamma[0].get(),self.gamma[1].get(),self.gamma[2].get())
            self._changed = False
        


class button(Qw.QPushButton):
    
    def __init__(self,text,callback,tooltip=None):
        if type(text) == QtGui.QIcon:
            Qw.QPushButton.__init__(self)
            self.setIcon(text)
            #self.setIconSize(QtCore.QSize(16,16))
        else:
            Qw.QPushButton.__init__(self,text)
        if tooltip != None: self.setToolTip(tooltip)
        self.clicked.connect(callback)
                
 
        

class label(Qw.QLabel):
    
    def __init__(self,text,tooltip=None,size=None,bold=None,align=QtCore.Qt.AlignLeft):
        Qw.QLabel.__init__(self,text)
        self.setAlignment(align)
        if tooltip != None: self.setToolTip(tooltip)
        fnt = QtGui.QFont()
        if size != None: fnt.setPointSize(size)
        if bold != None: fnt.setBold(bold)
        self.setFont(fnt)
        


        
class slider(Qw.QWidget):
    """ A slider derivate """
    
    sigChanged = QtCore.pyqtSignal(float)
    
    def __init__(self,vmin,vmax,vstart, lab):
        self.vstart = vstart

        ## Basic layout
        Qw.QWidget.__init__(self)
        lay = Qw.QVBoxLayout(self)
        lay.setSpacing(0)
        lay.setContentsMargins(0,0,0,0)
        self.setMinimumWidth(50)
        
        ## Title
        lab = lab.split(':')
        tmp = label(lab[0],None,12,True)
        lay.addWidget(tmp,0,QtCore.Qt.AlignHCenter)
        if len(lab)>1: tmp.setToolTip(lab[1])
        
        ## the slider as main object
        self.sld = Qw.QSlider(QtCore.Qt.Vertical)
        self.sld.setMinimumHeight(100)
        lay.addWidget(self.sld,0,QtCore.Qt.AlignHCenter)

        ## label to show current value
        self.lab = Qw.QLabel('?')
        self.lab.setToolTip("Doubleclick to reset\nRightclick to edit")
        self.lab.mouseDoubleClickEvent = lambda x: self.sld.setValue(self.u2s(vstart))
        self.lab.mouseReleaseEvent = self.uinput
        lay.addWidget(self.lab,0,QtCore.Qt.AlignHCenter)

        ## finishing
        self.sld.setMinimum(self.u2s(vmin))
        self.sld.setMaximum(self.u2s(vmax))
        self.sld.valueChanged.connect(self.vchanged)

        if self.u2s(vstart) == self.sld.value():
            self.vchanged(self.u2s(vstart))
        else:
            self.sld.setValue(self.u2s(vstart))

    def u2s(self,v): return v # slider to user scale
    def s2u(self,v): return v # user to slider scale

    def get(self): return self.s2u(self.sld.value())            
    def set(self,val): self.sld.setValue(self.u2s(val))


    def lab_set(self,uval): self.lab.setText(self.frmt.format(uval))
    
    def vchanged(self,val):
        """ update label and emit the widget-event Changed"""
        v = self.s2u(val)
        self.lab_set(v)
        self.sigChanged.emit(v)
        
        
        
        
class percSlider(slider):
    """ derivate for percent values"""
    scale = 100.0
    frmt = '{:0.0f}%'

    def u2s(self,v): return v*self.scale
    def s2u(self,v): return v/self.scale
    
    def lab_set(self,uval):
        self.lab.setText(self.frmt.format(uval*100))

    def uinput(self,evnt):
        if evnt.button() != QtCore.Qt.RightButton: return
        v,o = Qw.QInputDialog.getInteger(self, "new value", "new value", self.sld.value(), self.sld.minimum(), self.sld.maximum())
        if o: self.sld.setValue(v)


           
class logSlider(slider):
    """ derivate for log-scale"""
    scale = 100.0
    frmt = '{:0.2f}'
    def u2s(self,v): return math.log10(v)*self.scale
    def s2u(self,v): return math.pow(10,v/self.scale)

    def uinput(self,evnt):
        if evnt.button() != QtCore.Qt.RightButton: return
        v,o = Qw.QInputDialog.getDouble(self, "new value", "new value", self.s2u(self.sld.value()), self.s2u(self.sld.minimum()), self.s2u(self.sld.maximum()),1)
        if o: self.sld.setValue(self.u2s(v))

    