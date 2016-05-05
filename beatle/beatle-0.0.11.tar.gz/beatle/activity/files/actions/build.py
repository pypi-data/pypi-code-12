# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

import os
import signal
import wx
import wxx
import threading
from ctx import localcontext as context


class build(object):
    """Handler of debug session"""

    def __init__(self, project):
        """Init"""
        super(build, self).__init__()
        self._process = None
        self.make(project)

    def activateUI(self):
        """Activate the panes"""
        context.frame.CleanOutputPane()
        self.activateOutputPane()

    def deactivateUI(self):
        """Deactivate the ui"""
        frame = context.frame
        frame.m_mgr.Update()

    def activateOutputPane(self):
        """Activate the output pane"""
        frame = context.frame
        if frame.m_aux_panes == frame.m_aux_output_pane:
            return True
        try:
            i = max(i for i in range(0, frame.m_aux_panes.GetPageCount())
            if frame.m_aux_panes.GetPage(i) == frame.m_aux_output_pane)
            frame.m_aux_panes.SetSelection(i)
            return True
        except:
            pass
        return False

    def receiver_proc(self):
        """funcion que realiza el trabajo en el thread"""
        handler = context.frame.GetEventHandler()
        handler.AddPendingEvent(wxx.LoggerEvent('build ...'))
        line = ''
        for line in iter(self._process.stdout.readline, ""):
            handler.AddPendingEvent(wxx.LoggerEvent(line.strip()))
            self._process.stdout.flush()
            wx.YieldIfNeeded()
        handler.AddPendingEvent(wxx.LoggerEvent('end'))
        self._process.stdout.close()
        self._process.wait()
        self._process = None

    def force_stop(self):
        """Brute stop"""
        self.done = True
        if self._process:
            os.killpg(os.getpgid(self._process.pid), signal.SIGTERM)

    def make(self, project):
        """Start a debug operation"""
        if self._process:
            return False  # is already running
        path = os.getcwd()
        os.chdir(project.dir)
        server_command = 'make all'
        import subprocess
        try:
            self._process = subprocess.Popen(server_command,
                bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True,
                preexec_fn=os.setsid)
            threading.Thread(target=self.receiver_proc,).start()
        except:
            handler = context.frame.GetEventHandler()
            handler.AddPendingEvent(wxx.LoggerEvent('execution failed'))
            os.chdir(path)
            return False
        self.activateUI()
        wx.YieldIfNeeded()
        os.chdir(path)
        return True





