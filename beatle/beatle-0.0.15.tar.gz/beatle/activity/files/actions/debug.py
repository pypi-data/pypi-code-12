# -*- coding: utf-8 -*-

import os
import os.path
import sys
import signal
import re
import wx
import wxx
import threading
from ctx import localcontext as context
from activity.files.ui import pane


class threadInfo(object):
    """small class for thread information"""

    def __init__(self, **kwargs):
        """init"""
        self._is_current = kwargs.get('current', False)
        self._class = kwargs.get('cls', 'unknown')
        self._name = kwargs.get('name', '<unnamed>')
        self._status = kwargs.get('status', 'unknown')
        self._id = kwargs['id']
        self._stack = []
        super(threadInfo, self).__init__()

    @property
    def stack(self):
        """return thread stack"""
        return self._stack

    def append_stack(self, call, file, line):
        """Añade una llamada a la pila"""
        self._stack.append((call, file, line))

    @property
    def is_current(self):
        """return info about if the thread is the current thread"""
        return self._is_current

    @property
    def classname(self):
        """return the class name"""
        return self._class

    @property
    def name(self):
        """return the name"""
        return self._name

    @property
    def status(self):
        """return the thread status"""
        return self._status

    @property
    def id(self):
        """return the thread identifier"""
        return self._id


class debugPythonSession(object):
    """Handler of debug session"""

    def __init__(self, script=None):
        """Init"""
        self.ansi_escape = re.compile(r'\x1b[^m]*m')
        self.bin_obj = re.compile(r'<(?P<decl>.*?)>(?!\')')
        self.find_unquoted = [
            re.compile(r'\'copyright\': .*?\.\,', re.DOTALL),
            re.compile(r'\'credits\': .*?\.\,', re.DOTALL),
            re.compile(r'\'license\': .*?\,', re.DOTALL),
            re.compile(r'\'help\': .*?\.\,', re.DOTALL),
            re.compile(r'\'exit\': .*?\,', re.DOTALL),
            re.compile(r'\'quit\': .*?\,', re.DOTALL)
            ]        # hooks
        self.find_break = re.compile(
            r'(?P<bpnum>[0-9]+)\s+breakpoint\s+\w+\s+\w+\s+at\s+(?P<file>.+):(?P<line>[0-9]+)')
        self._set_file_line = lambda x, y: None
        # retained info
        self.info = {}
        self._process = None
        self._receiver = None
        self._message = []
        self._stepping = False
        self._threads = {}
        self._locals = {}
        self._breakpoints = {}
        self._buffer = ''  # buffer para stack
        self._bufferL = ''  # buffer para info de lineas
        self._bufferT = ''  # buffer para info de threads/locales
        self._bufferB = ''  # buffer para info de breakpoints
        self._sema = threading.Semaphore(0)
        super(debugPythonSession, self).__init__()
        if script:
            self.debugScript(script)

    @property
    def threads(self):
        """return the thread dictionary"""
        return self._threads

    @property
    def locals(self):
        """return the locals list"""
        return self._locals

    @property
    def breakpoints(self):
        """return the dict of breakpoints"""
        return self._breakpoints

    def activateUI(self):
        """Activate the panes"""
        context.frame.CleanOutputPane()
        self.addStackPane()
        self.addDebugCommandPane()
        self.activateOutputPane()
        self.activateWatchBook()

    def deactivateUI(self):
        """Deactivate the ui"""
        frame = context.frame
        self.removeStackPane()
        self.removeDebugCommandPane()
        frame.m_mgr.DetachPane(self.m_debugInfo)
        self.m_debugInfo.Destroy()
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

    def removeStackPane(self):
        """Remove the stack pane"""
        frame = context.frame
        auxbook = frame.m_aux_panes
        for i in range(0, auxbook.GetPageCount()):
            if auxbook.GetPage(i) == self.m_stack:
                auxbook.DeletePage(i)
                return

    def removeDebugCommandPane(self):
        """Remove the debug command pane"""
        frame = context.frame
        auxbook = frame.m_aux_panes
        for i in range(0, auxbook.GetPageCount()):
            if auxbook.GetPage(i) == self.m_command:
                auxbook.DeletePage(i)
                return

    def addStackPane(self):
        """Add stackframe pane"""
        frame = context.frame
        self.m_stack = pane.StackFrame(frame.m_aux_panes, self)
        frame.m_aux_panes.AddPage(self.m_stack, u"stack frame", False)

    def addDebugCommandPane(self):
        """Add debug command pane"""
        frame = context.frame
        self.m_command = pane.DebugCommand(frame.m_aux_panes, self)
        frame.m_aux_panes.AddPage(self.m_command, u"debug command", False)

    def activateWatchBook(self):
        """Activate the watch panel"""
        frame = context.frame
        self.m_debugInfo = wx.aui.AuiNotebook(frame, wx.ID_ANY, wx.DefaultPosition,
            wx.Size(200, -1), wx.aui.AUI_NB_DEFAULT_STYLE)
        frame.m_mgr.AddPane(self.m_debugInfo, wx.aui.AuiPaneInfo().Right().PinButton(True).
            Dock().Resizable().FloatingSize(wx.Size(120, -1)).DockFixed(False).Row(1).Layer(4))
        # add panes:
        # threads and stack
        self.m_threads = pane.Threads(self.m_debugInfo, self)
        self.m_locals = pane.Locals(self.m_debugInfo, self)
        self.m_expressions = pane.Expressions(self.m_debugInfo, self)
        self.m_breakpoints = pane.Breakpoints(self.m_debugInfo, self)
        self.m_debugInfo.AddPage(self.m_threads, 'Threads', True, wx.NOT_FOUND)
        self.m_debugInfo.AddPage(self.m_locals, 'Locals', False, wx.NOT_FOUND)
        self.m_debugInfo.AddPage(self.m_expressions, 'Expressions', False, wx.NOT_FOUND)
        self.m_debugInfo.AddPage(self.m_breakpoints, 'Breakpoints', False, wx.NOT_FOUND)
        frame.m_mgr.Update()

    def UpdateThreadsUI(self):
        """Update the visual info"""
        self.m_threads.UpdateData()

    def UpdateDebugCommandUI(self, response):
        """Update debug command pane"""
        self.m_command.UpdateData(response)

    def UpdateLocalsUI(self):
        """Update the visual info"""
        self.m_locals.UpdateData()

    def UpdateBreakpointsUI(self):
        """Update the visual info"""
        self.m_breakpoints.UpdateData()

    def CaptureLocalsInfo(self, text):
        """capture lines of text"""
        self._buffer += str(text)

    def ProcessLocalsInfo(self):
        """Process the full thread info and dispatch"""
        text = self._buffer
        if not text:
            return
        self._buffer = ''
        cleaner = lambda x: '\'<{}>\''.format(re.sub(r'\'', '', x.group('decl')))
        text = self.bin_obj.sub(cleaner, text)
        for k in self.find_unquoted:
            text = k.sub('', text)
        #print '-----'
        #print text
        try:
            self._locals = eval(text)
        except:
            self._locals = {'note': 'failed translating locals'}

    def CaptureLineInfo(self, text):
        """obtiene info de las lineas"""
        self._bufferL += text

    def CaptureBreakInfo(self, text):
        """obtiene info de los breakpoints"""
        self._bufferB += text

    def ProcessBreakInfo(self):
        """procesa la informacion de los brekpoints"""
        text = self._bufferB
        if not text:
            return
        self._bufferB = ''
        lines = text.splitlines()
        self._breakpoints = {}
        for line in lines:
            z = self.find_break.match(line)
            if z:
                self._breakpoints[z.group('bpnum')] = (z.group('file'), z.group('line'))

    def CaptureThreadInfo(self, text):
        """capture linest of text"""
        self._bufferT += str(text)

    def ProcessLineInfo(self):
        """Process the line info"""
        text = self._bufferL
        if not text:
            return
        self._bufferL = ''
        text = ''.join(text.splitlines())
        handler = context.frame.GetEventHandler()
        #print 'processing line text {}'.format(text)
        z = re.search(r'Line (?P<lineno>[0-9]*) of \"(?P<file>.*)\"', text)
        if z:
            self._line = l = int(z.group('lineno'))
            self._file = f = z.group('file')
            # post a message
            handler.AddPendingEvent(wxx.DebuggerEvent(wxx.FILE_LINE_INFO, (f, l)))

    def ProcessThreadInfo(self):
        """Process the full thread info and dispatch"""
        text = self._bufferT
        if not text:
            return
        self._bufferT = ''
        handler = context.frame.GetEventHandler()
        lines = text.splitlines()[1:]  # discard separator
        thread_info_line = lines.pop(0)
        thread_info = re.search(r'(?P<ttype>..) <(?P<tclass>.+)\((?P<tname>\w+), (?P<tstatus>\w+) .*\)>: (?P<tid>[0-9]+)',
            thread_info_line)
        thread_current = False
        thread_class = '???'
        thread_name = '???'
        thread_status = '???'
        thread_id = '???'
        if thread_info:
            thread_current = (thread_info.group('ttype') == '=>')
            thread_class = thread_info.group('tclass')
            thread_name = thread_info.group('tname')
            thread_status = thread_info.group('tstatus')
            thread_id = thread_info.group('tid')
        else:
            thread_info = re.search(r'    thread id: (?P<tid>[0-9]+)', thread_info_line)
            if not thread_info:
                # post a info message
                msg = 'Thread info:{info}'.format(info=thread_info_line)
                handler.AddPendingEvent(wxx.DebuggerEvent(wxx.UNKNOWN_DEBUG_INFO, msg))
                #handler.AddPendingEvent(wxx.LoggerEvent(msg))
                return
        # The thread info is append to the internal list
        thread_id = thread_info.group('tid')
        thread = threadInfo(
            current=thread_current,
            cls=thread_class,
            name=thread_name,
            status=thread_status,
            id=thread_id)
        self._threads[thread_id] = thread
        # Now parse the stack frame
        header = True
        while len(lines):
            try:
                item = lines.pop(0).strip()
                if item[:8] == '<module>':
                    thread.append_stack(item, None, None)
                    continue
                _line = lines.pop(0).strip()
                # skip separator
                # dissmiss debugger lines
                if header:
                    if 'trepan.processor.command.info' in item:
                        continue
                    if 'trepan.processor.cmdproc' in item:
                        continue
                    if 'trepan.lib.core.DebuggerCore' in item:
                        continue
                    if item[:13] == '_tracer_func(':
                        continue
                header = False
                z = re.search(r"called from file '(?P<source>.+)' at line (?P<line>[0-9]+)", _line)
                if z:
                    s = '{f}:{l} in {c}'.format(
                        f=z.group('source'),
                        l=z.group('line'),
                        c=item)
                    thread.append_stack(s, z.group('source'), z.group('line'))
                else:
                    thread.append_stack(_line, None, None)
            except:
                break
        #print thread.stack

    def receiver_proc(self):
        """funcion que realiza el trabajo en el thread"""
        handler = context.frame.GetEventHandler()
        handler.AddPendingEvent(wxx.LoggerEvent('watching process ...'))
        line = ''
        for line in iter(self._process.stdout.readline, ""):
            handler.AddPendingEvent(wxx.LoggerEvent(line.strip()))
            self._process.stdout.flush()
            wx.YieldIfNeeded()
        handler.AddPendingEvent(wxx.LoggerEvent('closing ...'))
        # serious issue here: we cound'nt close the pipe!
        # closing that means closing the app stdout!
        #self._process.stdout.close()
        self._process.wait()
        self._process = None
        handler.AddPendingEvent(wxx.LoggerEvent('execution ended!'))
        handler.AddPendingEvent(wxx.DebuggerEvent(wxx.DEBUG_ENDED))

    def command_proc(self):
        """reads commands from the debugger"""
        from trepan.interfaces import comcodes as Mcomcodes
        from trepan.interfaces import client as Mclient
        connection_opts = {'open': True,
            'IO': 'TCP', 'HOST': '127.0.0.1', 'PORT': 8765}
        try:
            self.intf = Mclient.ClientInterface(connection_opts=connection_opts)
        except:
            attempts = 10
            while(attempts):
                try:
                    wx.Sleep(1)
                    self.intf = Mclient.ClientInterface(connection_opts=connection_opts)
                    break
                except:
                    attempts = attempts - 1
            if not attempts:
                frame = context.frame
                handler = frame.GetEventHandler()
                handler.AddPendingEvent(wxx.LoggerEvent('connection failed'))
                if self._process:
                    os.killpg(os.getpgid(self._process.pid), signal.SIGTERM)
                return

        self.done = False
        last_command = None
        handler = context.frame.GetEventHandler()
        with open(os.path.expanduser('~/.debug_log.log'), 'w') as dlog:
            dlog.write('starting session\n')
            while not self.done:
                try:
                    control, remote_msg = self.intf.read_remote()
                except:
                    # an exception has happen in the debugger
                    self.done = True
                    continue
                remote_msg = self.ansi_escape.sub('', remote_msg)  # remove ansi console color escape codes
                try:
                    if control == Mcomcodes.COMMAND:
                        cmd = 'COMMAND'
                    elif control == Mcomcodes.CONFIRM_FALSE:
                        cmd = 'CONFIRM_FALSE'
                    elif control == Mcomcodes.CONFIRM_REPLY:
                        cmd = 'CONFIRM_REPLY'
                    elif control == Mcomcodes.CONFIRM_TRUE:
                        cmd = 'CONFIRM_TRUE'
                    elif control == Mcomcodes.PRINT:
                        cmd = 'PRINT'
                    elif control == Mcomcodes.PROMPT:
                        cmd = 'PROMPT'
                    elif control == Mcomcodes.QUIT:
                        cmd = 'QUIT'
                    elif control == Mcomcodes.RESTART:
                        cmd = 'RESTART'
                    elif control == Mcomcodes.SYNC:
                        cmd = 'SYNC'
                    else:
                        cmd = 'UNKNOWN'
                    dlog.write('received remote msg: {d}[{m}] previous command: [{c}]\n'.format(
                        d=cmd, m=remote_msg, c=last_command or 'None'))
                except:
                    dlog.write('failed to write remote\n')
                # print 'c, r', control, remote_msg
                if control == Mcomcodes.PRINT:
                    if last_command:
                        if last_command[0] == '#':
                            handler.AddPendingEvent(wxx.DebuggerEvent(wxx.USER_COMMAND_RESPONSE, remote_msg))
                        elif last_command == 'info line':
                            dlog.write('capturing line\n')
                            self.CaptureLineInfo(remote_msg)
                        elif last_command == 'info threads verbose':
                            self.CaptureThreadInfo(remote_msg)
                        elif last_command == 'pp locals()':
                            self.CaptureLocalsInfo(remote_msg)
                        elif last_command == 'info break':
                            self.CaptureBreakInfo(remote_msg)
                        elif re.search(r'The program finished', remote_msg):
                            self.intf.write_remote(Mcomcodes.CONFIRM_REPLY, 'quit')
                    continue
                if control in [Mcomcodes.CONFIRM_TRUE, Mcomcodes.CONFIRM_FALSE]:
                    self.intf.write_remote(Mcomcodes.CONFIRM_REPLY, 'Y')
                    continue
                if control == Mcomcodes.PROMPT:
                    # here, we read the message
                    try:
                        if last_command == 'info line':
                            self.ProcessLineInfo()
                        elif last_command == 'info threads verbose':
                            self.ProcessThreadInfo()
                            handler.AddPendingEvent(wxx.DebuggerEvent(wxx.UPDATE_THREADS_INFO))
                        elif last_command == 'pp locals()':
                            self.ProcessLocalsInfo()
                            handler.AddPendingEvent(wxx.DebuggerEvent(wxx.UPDATE_LOCALS_INFO))
                        elif last_command == 'info break':
                            self.ProcessBreakInfo()
                            handler.AddPendingEvent(wxx.DebuggerEvent(wxx.UPDATE_BREAKPOINTS_INFO))
                    except:
                        pass
                    self._stepping = True
                    self._sema.acquire()
                    if not len(self._message):
                        continue
                    last_command = self._message[0]
                    del self._message[0]
                    self._stepping = False
                    # debug commands
                    #if last_command != 'info line':
                    #    handler.AddPendingEvent(wxx.LoggerEvent(last_command))
                    if last_command[0] == '#':
                        #this is an user command, using debug command pane
                        self.intf.write_remote(Mcomcodes.CONFIRM_REPLY, last_command[1:])
                    else:
                        self.intf.write_remote(Mcomcodes.CONFIRM_REPLY, last_command)
                    continue
                if control == Mcomcodes.QUIT:
                    self.done = True
                    continue
                if control == Mcomcodes.RESTART:
                    self.intf.inout.close()
                    wx.Sleep(1)
                    self.intf.inout.open()
                else:
                    print("!! Weird status code received '%s'" % control)
                    print(remote_msg,)
        self.intf.close()
        del self.intf

    def force_stop(self):
        """Brute stop"""
        self.done = True
        self._sema.release()
        if self._process:
            os.killpg(os.getpgid(self._process.pid), signal.SIGTERM)

    def send_command(self, msg):
        """Post a command for the debugger in the queue"""
        self._message.append(msg)
        self._sema.release()

    # el comando para el cliente es
    # python -m trepan.client --port=8765 {script}
    # ... esto es lo que hemos de hackear

    def debugScript(self, script):
        """Start a debug operation"""
        if self._process:
            return False  # is already debugging
        server_flags = [
            '--private', '--post-mortem', '--nx',
            '--port=8765', '--server']
        server_command = 'trepan2 {flags} {file}'.format(
            flags=' '.join(server_flags),
            file=script)
        import subprocess
        self.activateUI()
        try:
            self._process = subprocess.Popen(server_command,
                bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True,
                preexec_fn=os.setsid)
            threading.Thread(target=self.receiver_proc,).start()
            threading.Thread(target=self.command_proc,).start()
        except:
            self.deeactivateUI()
            handler = context.frame.GetEventHandler()
            handler.AddPendingEvent(wxx.LoggerEvent('execution failed'))
            return False
        return True





