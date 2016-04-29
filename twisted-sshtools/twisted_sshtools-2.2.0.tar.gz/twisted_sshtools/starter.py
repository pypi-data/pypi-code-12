# Copyright (C) 2014 Stefan C. Mueller


"""
Starts processes on this or another machine.

The starter returns a `Process` with the following API:
    
.. py:class:: Process

    Objects representing processes have the following attributes and methods:

    .. py:method:: send_stdin(data)
   
        Sends data to the standard input of this process.
   
        :param str data: Data to send.
      
    .. py:method:: kill()
    
        Attempts to forcefully end the process if it hasn't ended already.
        In any case, it cleans up all resources locally bound to it.
        The deferred calls back once finished.
        
    .. py:attribute:: stdout
    
        :class:`~twisted_sshtools.deferutils.Event` fired when the process produced
        standard output data.
        
    .. py:attribute:: stderr
    
        :class:`~twisted_sshtools.deferutils.Event` fired when the process produced
        standard error data.
        
    .. py:attribute:: exited
    
        :class:`~twisted_sshtools.deferutils.Event` fired when the process has ended
          with a :class:`Failure` indiciating the reason, or `None` if
          the process has exited normally.
    
    .. py:attribute:: hostname
    
        IP or host name on which the process has been started.
    
"""

import os.path
import tempfile
import logging

from twisted.internet import defer, reactor, threads, error, protocol

from twisted_sshtools import ssh
from twistit import _events as deferutils

logger = logging.getLogger(__name__)

class Starter(object):
    
    def start(self, command, fileset={}):
        """
        Starts one or more processes, potentially on a remote machine.
        
        :param command: Command to execute. The first element has to be the absolute
            path to the executable, followed by zero or more arguments.
        :type command: list of strings
        
        :param dict fileset: Set of files to transfer to the machine on which the
            command is executed. The keys are paths relative to the current working
            directory of the executed command. The values are strings with the file
            content. Not all starters support file transfer.
            
        :returns: The started process.
        :rtype: deferred :class:`twisted_sshtools.process.Process`.
        """
        raise NotImplementedError("abstract")
        
        
class LocalStarter(Starter):
    """
    Creates a starter that starts processes on the local machine.
    """
    
    def __init__(self, tmp_dir=None):
        self.tmp_dir = tmp_dir

    def start(self, command, fileset={}):
        
        def transfer_files():
            # we use blocking IO to create the files. Twisted's `fdesc` is of no use since
            # `O_NONBLOCK` is ignored on regular files (it is for sockets, really).
            # So we do this in a thread instead.
            for filename, content in fileset.iteritems():
                path = os.path.join(tmp_dir, filename)
                with open(path, 'wb') as f:
                    f.write(content)
                    
                    
        def spawn_process(command, path=None):
            protocol = _LocalProcessProtocol()
            d = defer.maybeDeferred(reactor.spawnProcess, protocol, command[0], command, env=None, path=path)  # @UndefinedVariable
            def started(_):
                return protocol.process_d
            d.addCallback(started)
            return d

                    
        # select directory for fileset. Don't do this in
        # in __init__ as the starter might be sent to a different
        # machine.
        if self.tmp_dir:
            tmp_dir = self.tmp_dir
        else:
            tmp_dir = tempfile.gettempdir()
        
        if fileset:
            d = threads.deferToThread(transfer_files)
        else:
            d = defer.succeed(None)
        
            
        d.addCallback(lambda _:spawn_process(command, path=tmp_dir))
        return d
        
        
        
class _LocalProcess(object):
    def __init__(self, transport):
        self._transport = transport
        self.stdout = deferutils.Event()
        self.stderr = deferutils.Event()
        self.exited = deferutils.Event()
        self.hostname = "localhost"

    def send_stdin(self, data):
        self._transport.write(data)
        
    def kill(self):
        try:
            self._transport.signalProcess('KILL')
        except error.ProcessExitedAlready:
            return defer.succeed(None)
        d = self.exited.next_event()
        def onerror(reason):
            # It's hardly a surprise that the process exits with a 
            # non-zero exit code at this point.
            reason.trap(error.ProcessTerminated)
        d.addErrback(onerror)
        return d

class _LocalProcessProtocol(protocol.ProcessProtocol):
    def __init__(self):
        self.process = None
        self.process_d = defer.Deferred()
        
    def connectionMade(self):
        self.process = _LocalProcess(self.transport)
        self.process_d.callback(self.process)
        
    def errReceived(self, data):
        self.process.stderr.fire(data)
    
    def outReceived(self, data):
        self.process.stdout.fire(data)
        
    def processEnded(self, status):
        if status and status.check(error.ProcessDone):
            status = None
        self.process.exited.fire(status)
        
class SSHStarter(Starter):
    """
    Creates a starter that starts processes on remote machines.
    """

    def __init__(self, hostname, username, password=None, private_key_files=[], private_keys=[], tmp_dir="/tmp"):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.private_keys = map(_read_file, private_key_files) + list(private_keys)
        self.tmp_dir = tmp_dir


    def start(self, command_args, fileset={}):

        basedir = self.tmp_dir
        
        command = " ".join(_bash_escaping(arg) for arg in command_args)
        if fileset:
            command = "cd {basedir} ; exec {command}".format(basedir=_bash_escaping(basedir),
                                                                             command=command)

        def on_connected(connection):
                       
            def transmit_file(sftp, path, content):
                abspath = basedir + "/" + path
                logger.debug("Transferring %s..." % abspath)
                d = sftp.write_file(abspath, content)
                d.addCallback(lambda _:sftp)
                return d
            
            def start_command(ignore):
                logger.debug("Executing command on %s: %s" % (self.hostname, command))
                return connection.execute(command)
            
            def command_started(proc):
                logger.debug("Command on %s is running" % self.hostname)
                return _SSHProcess(proc, connection, self.hostname)
                       
            def error_while_connection_open(failure):
                logger.debug("Closing connection to %s due to error." % self.hostname)
                d = connection.close()
                d.addBoth(lambda _:failure)
                return d
 
            if fileset:
                logger.debug("Opening SFTP session to %s" % self.hostname)
                d = connection.open_sftp()
                for path, content in fileset.iteritems():
                    d.addCallback(lambda sftp:transmit_file(sftp, path, content))
                d.addCallback(lambda sftp:sftp.close())
            else:
                d = defer.succeed(None)
            d.addCallback(start_command)
            d.addCallback(command_started)
            d.addErrback(error_while_connection_open)
            return d
            
        logger.debug("Opening SSH connection %s @ %s" % (self.username, self.hostname))
            
        d = ssh.connect(self.hostname, self.username, self.password, private_keys=self.private_keys)
        d.addCallback(on_connected)
        
        return d
        
class _SSHProcess(object):
    """
    Wrapper around `ssh._SSHProcess`. The process from the `ssh` module
    correctly assumes that other processes and file transfers might be
    running over the same underlying connection, thous does not close
    the connection on exit. This process does exactly that, assuming
    that the connection only exists for the purpose of this one process.
    We also support `kill` after a fashion: We close the connection,
    the actual process will receive SIGHUB, and we can free all local
    resources.
    """
    def __init__(self, sshprocess, sshconnection, hostname):
        self._sshprocess = sshprocess
        self._sshconnection = sshconnection
        self.hostname = hostname
        
        self.stdout = self._sshprocess.stdout
        self.stderr = self._sshprocess.stderr
        
        self.exited = deferutils.Event()
        self._sshprocess.exited.add_callback(self._on_exit)
        
    def kill(self):
        """
        Closes the SSH connection. The process will only receive SIGHUB,
        hopefully this is enough to make it exit.
        """
        logging.warn("Killing ssh process")
        self._sshconnection.close()
        d = self.exited.next_event()
        def onerror(reason):
            # It's hardly a surprise that the process exits with a 
            # non-zero exit code or a lost connection.
            reason.trap(error.ProcessTerminated, error.ConnectionLost)
        d.addErrback(onerror)
        return d
        
    def _on_exit(self, reason):
        d = self._sshconnection.close()
        def on_closed(_):
            self.exited.fire(reason)
        d.addCallback(on_closed)


def _bash_escaping(string):
    """
    Escapes and puts quotes around an arbitrary byte sequence so that the given
    string will be interpreted as a single string in a bash command line.
    
    Escaped strings can be concatenated (separted by spaces) to form
    a bash command. For example to execute an arbitrary python script one could
    execute the following bash command:
    
       "python -c %s" % bash_escaping(my_script)
       
    This will work even if `string` contains new-lines, quotes or other
    special characters.
    """

    def octal(ascii_code):
        """
        Returns the octal string of the given ascii code.
        Leading zeros are added to pad to three characters.
        """
        if ascii_code < 0 or ascii_code > 255:
            raise ValueError("Not an ASCII code")
        least_sig = ascii_code % 8
        mid_sig = (ascii_code >> 3) % 8
        most_sig = (ascii_code >> 6) % 8
        return "%s%s%s" % (most_sig, mid_sig, least_sig)

    from cStringIO import StringIO
    strfile = StringIO()
    strfile.write("$'")
    for char in string:
        if char >= 'a' and char <= 'z':
            strfile.write(char)
        elif char >= 'A' and char <= 'Z':
            strfile.write(char)
        elif char >= '0' and char <= '9':
            strfile.write(char)
        elif char == "." or char == " ":
            strfile.write(char)
        else:
            strfile.write('\\')
            strfile.write(octal(ord(char)))
    strfile.write("'")
    return strfile.getvalue()

def _read_file(path):
    with open(path) as f:
        return f.read()
    