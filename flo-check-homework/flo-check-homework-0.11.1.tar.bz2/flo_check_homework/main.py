# -*- coding: utf-8 -*-

# main.py --- Main module of flo-check-homework
# Copyright (c) 2011, 2012, 2013, 2014  Florent Rougon
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 51 Franklin St, Fifth Floor,
# Boston, MA  02110-1301 USA.


import sys, os, locale, getopt, subprocess, logging, operator, random, time, \
    datetime, math, numbers, hashlib, errno, functools, pkgutil, posixpath
from PyQt4 import QtCore, QtGui
translate = QtCore.QCoreApplication.translate

import textwrap
tw = textwrap.TextWrapper(width=78, break_long_words=False,
                          break_on_hyphens=True)
from textwrap import dedent

import decimal
from decimal import Decimal
# In the state of super magic formulas at the time of this writing, a precision
# of 6 (3 for the integer part and 3 for the fractional part) should be enough
# to represent any correct answer. Thus, the precision of the default decimal
# context (28) should be largely enough, even if someone modifies the algorithm
# and forgets to check that the context precision is enough for the new
# computations.
decimalContext = decimal.Context(prec=28)
# InvalidOperation should already be enabled by default
# FloatOperation provides a safety net against possibly subtle bugs
for trapName in ("InvalidOperation", "FloatOperation"):
    decimalContext.traps[getattr(decimal, trapName)] = True
decimal.setcontext(decimalContext)

from . import fch_util, conjugations, image_widgets


progname = os.path.basename(sys.argv[0])
from . import __version__ as progversion

usage = """Usage: %(progname)s [OPTION ...] [--] PROGRAM [ARGUMENT ...]
Check specific skills before launching a program.

Options:
  -e, --allow-early-exit       allow immediate exit even if the score is not
                               satisfactory
  -i, --interactive            start the graphical user interface in all
                               cases, even when a super magic token is present
  -D, --quit-delay=DELAY       when option -e is not in effect and the score
                               is lower than the success threshold, the first
                               attempt to quit starts a timer for DELAY
                               seconds (the special value "random", which is
                               the default, selects a random delay). Actually
                               exiting the program (without killing it) is
                               only possible when the timer expires.
  -p, --pretty-name            name of PROGRAM in pretty form for use in
                               the interface
  -t, --test-mode              enable debugging facilities
  -v, --verbose                be verbose about what the program is doing
      --help                   display this message and exit
      --version                output version information and exit""" \
  % { "progname": progname }

params = {}
app = None
cleanup_handlers_for_program_exit = []

# Define which reward image can be obtained from which (normalized) score. The
# first entry, starting from the end, for which 'score >= threshold', is
# selected and defines the (possibly empty) set of images that can be given
# for this score.
#
# Don't try to generate the image lists with glob.glob() at runtime, as the
# whole package could be stored as a single compressed file (moreover,
# pkgutil.get_data() expects '/' separators).
#
# import glob, pprint
# def list_files(d):
#     pprint.pprint([ f for f in glob.glob(d) if not f.endswith(".svg") ])
#
reward_images = [
    (float("-inf"), ['images/rewards/10-abysmal/NCI_steamed_shrimp.jpg',
                     'images/rewards/10-abysmal/Nordseegarnelen.jpg',
                     'images/rewards/10-abysmal/Heterocarpus_ensifer.jpg']),
    (0.2, ['images/rewards/20-not_good_enough/Paul01.jpg',
           'images/rewards/20-not_good_enough/cat-by-artbejo-174857.png',
           'images/rewards/20-not_good_enough/Cara_perro.png',
           'images/rewards/20-not_good_enough/Paul04.jpg',
           'images/rewards/20-not_good_enough/papapishu_Fighting_cat.png',
           'images/rewards/20-not_good_enough/Elvire_maybe_angry.jpg',
           'images/rewards/20-not_good_enough/Paul03.jpg',
           'images/rewards/20-not_good_enough/johnny_automatic_black_cat_1.png',
           'images/rewards/20-not_good_enough/Roger_dog.jpg',
           'images/rewards/20-not_good_enough/Elvire01.jpg',
           'images/rewards/20-not_good_enough/johnny_automatic_cat_reading.png',
           'images/rewards/20-not_good_enough/Paul02.jpg']),
    (0.9, ['images/rewards/30-happy/Caousette avec son rat en peluche.jpg',
           'images/rewards/30-happy/cat--6-by-inky2010.png',
           'images/rewards/30-happy/Caousette0004.jpg',
           'images/rewards/30-happy/cat-by-ruthirsty-174540.png',
           'images/rewards/30-happy/Caousette0010.jpg',
           'images/rewards/30-happy/Zita avec son rat en peluche.jpg']),
    (1.0, ['images/rewards/40-very_happy/Caousette0022.jpg',
           'images/rewards/40-very_happy/Gerald_G_Cartoon_Cat_Walking.png',
           'images/rewards/40-very_happy/Jean01.jpg']) ]

# The user is allowed to run the desired program if, and only if, the
# normalized score (i.e., between 0.0 and 1.0) is >= score_threshold.
# When altering this value, make sure it is consistent with reward_images!
score_threshold = reward_images[-2][0]


def setup_logging(level=logging.NOTSET, chLevel=None):
    global logger

    if chLevel is None:
        chLevel = level

    logger = logging.getLogger('flo_check_homework.main')
    logger.setLevel(level)
    # Create console handler and set its level
    ch = logging.StreamHandler() # Uses sys.stderr by default
    ch.setLevel(chLevel)  # NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
    # Logger name with :%(name)s... many other things available
    formatter = logging.Formatter("%(levelname)s %(message)s")
    # Add formatter to ch
    ch.setFormatter(formatter)
    # Add ch to logger
    logger.addHandler(ch)

setup_logging()
# Effective level for all child loggers with NOTSET level
logging.getLogger('flo_check_homework').setLevel(logging.INFO)


def register_cleanup_handler(func, args=(), kwargs=None):
    """Register a handler function to be run before program exit.

    The handler function will be called with ARGS (sequence) as positional
    arguments and KWARGS (mapping) as keywords arguments.

    All such handlers must return an integer, 0 meaning successful
    operation.

    """
    kwargs = kwargs or {}
    cleanup_handlers_for_program_exit.append((func, args, kwargs))


def loadResource(resource):
    return pkgutil.get_data(__package__, resource)

imgExtToQtFormat = {"png": "PNG",
                    "jpg": "JPEG",
                    "jpeg": "JPEG",
                    "gif": "GIF"}

def _QtImgFormat(path, format):
    """Return an image format name suitable for Qt functions."""
    if format:
        return format
    else:
        # pkgutil resource paths use '/' to separate components
        ext = posixpath.splitext(path)[1]
        return imgExtToQtFormat.get(ext.lower(), None)

def QPixmapFromResource(resource, format=None):
    format = _QtImgFormat(resource, format)
    p = QtGui.QPixmap()
    p.loadFromData(QtCore.QByteArray(loadResource(resource)), format)
    return p

def QImageFromResource(resource, format=None):
    format = _QtImgFormat(resource, format)
    return QtGui.QImage.fromData(
        QtCore.QByteArray(loadResource(resource)), format)


@QtCore.pyqtSlot(result=int)
def run_cleanup_handlers_for_program_exit():
    logger.debug("Running cleanup handlers...")
    retvals = []

    while len(cleanup_handlers_for_program_exit) > 0:
        handler, args, kwargs = cleanup_handlers_for_program_exit.pop()
        retvals.append(handler(*args, **kwargs))

    # Warning: bitwise OR!
    return functools.reduce(operator.or_, retvals, 0)


def getDecimalDigit(d, n):
    """Extract the nth digit of decimal d after the decimal point.

    This function is based on the decimal module to avoid problems
    such as:

    >>> 269.462 - 269
    0.4619999999999891
    >>> int(1000*(269.462 - 269))
    461

    """
    places = Decimal(10) ** -n
    td = d.quantize(places, rounding=decimal.ROUND_DOWN)
    return td.as_tuple().digits[-1]


class HomeWorkCheckApp(QtGui.QApplication):
    def __init__(self, args):
        super().__init__(args)

        # Not sure this is really useful with PyQt; however, either this or the
        # corresponding settings in the .pro file (or both) is necessary for
        # the first run of pylupdate4 to deal with UTF-8 correctly.
        QtCore.QTextCodec.setCodecForCStrings(
            QtCore.QTextCodec.codecForName("UTF-8"))
        QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName("UTF-8"))

        self.setupTranslations()
        self.mainWindow = None           # To be created
        self.mainWindowInitialized = False
        self.aboutToQuit.connect(run_cleanup_handlers_for_program_exit)

        self.setOrganizationName("Florent Rougon")
        self.setOrganizationDomain("florent.rougon.free.fr")
        self.setApplicationName(progname)

        icon = QtGui.QIcon(QPixmapFromResource("images/logo/logo_64x64.png"))
        for size in ("32x32", "16x16", "14x14"):
            icon.addPixmap(QPixmapFromResource(
                    "images/logo/logo_{0}.png".format(size)))
        self.setWindowIcon(icon)

        self.validSuperMagicToken = False

    def endInit(self):
        """Initialization tasks that must be done once the lock file acquired"""
        # Must be done early in order to be safe with respect to other modules
        QtCore.QSettings.setDefaultFormat(QtCore.QSettings.IniFormat)
        # We need the QSettings to read the ProgramLauncher setting. To avoid a
        # QSettings.sync() before the final os.execvp() every time the program
        # is run with a valid super magic token, we'll restrict usage of the
        # QSettings to read-only in this class, or explicitely sync.
        self.qSettings = QtCore.QSettings()

        self.desiredProgramProcess = QtCore.QProcess(self)
        self.desiredProgramProcess.setProcessChannelMode(
            QtCore.QProcess.ForwardedChannels)
        self.desiredProgramProcess.started.connect(
            self.onDesiredProgramStarted)
        self.desiredProgramProcess.finished.connect(
            self.onDesiredProgramFinished)
        self.desiredProgramProcess.error.connect(
            self.onDesiredProgramError)

        # Optional launcher to start the desired program (read-only access,
        # cf. comment above)
        if self.qSettings.contains("ProgramLauncher"):
            self.launcher = self.qSettings.value("ProgramLauncher", type=str)
        else:
            self.launcher = ""

        if self.launcher:
            # This will be our direct child
            self.executedProgram = self.launcher
        else:
            # Can only be done after command line processing
            self.executedProgram = params["desired_program"][0]

        if not self.qSettings.contains("ForceInteractive"):
            self.qSettings.setValue("ForceInteractive", 0)
            self.qSettings.sync() # See above, when self.qSettings is assigned

        # Indicates if the desired (child) program is currently running
        self.childRunning = False

    def setupTranslations(self):
        # If the translators are garbage collected (or the data used to
        # initialize them), then translation doesn't work.
        self.qtTranslator = QtCore.QTranslator()
        # Load the translations built in Qt for the current locale. Among
        # others, this enables the translation of QtGui.QMessageBox.Yes/No
        # button texts.
        if self.qtTranslator.load(
            QtCore.QLocale().system(), "qt_", "",
            QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath)):
            self.installTranslator(self.qtTranslator)

        # Get a list of locale names (such as 'C', 'fr-FR' or 'en-US') for
        # translation purposes, in decreasing order of preference.
        locales = QtCore.QLocale().uiLanguages()
        # Prevent the translators from being garbage-collected (see above).
        self.l10n_data = []

        for loc in reversed(list(locales)):
            if loc == "C":
                continue
            langCode = loc.split('-')[0] # extract the language part

            try:
                # pkgutil resource paths use '/' to separate components
                data = pkgutil.get_data(
                    __package__, "translations/{lang}/{prog}.{lang}.qm".format(
                        lang=langCode, prog=progname))
            # Precisely, this is a FileNotFoundError, but this exception is not
            # available before Python 3.3.
            except os.error as e:
                continue

            translator = QtCore.QTranslator()
            # To make sure the garbage collector doesn't remove these too early
            self.l10n_data.append((translator, data))
            if translator.loadFromData(data):
                self.installTranslator(translator)

    def processCommandLine(self, arguments):
        global params

        version_blurb1 = translate("app", """Written by Florent Rougon.

Copyright (c) 2011-2014  Florent Rougon""")
        version_blurb2 = translate("app", """\
This is free software; see the source for copying conditions.  There is NO \
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.""")

        try:
            opts, args = getopt.getopt(arguments[1:], "eiD:p:tv",
                                       ["allow-early-exit",
                                        "interactive",
                                        "quit-delay=",
                                        "pretty-name",
                                        "test-mode",
                                        "verbose",
                                        "help",
                                        "version"])
        except getopt.GetoptError as message:
            sys.stderr.write(usage + "\n")
            return ("exit", 1)

        # Let's start with the options that don't require any non-option
        # argument to be present
        for option, value in opts:
            if option == "--help":
                print(usage)
                return ("exit", 0)
            elif option == "--version":
                print("{name} {version}\n{blurb1}\n{blurb2}".format(
                        name=progname, version=progversion,
                        blurb1=version_blurb1, blurb2=tw.fill(version_blurb2)))
                return ("exit", 0)

        # Now, require a correct invocation.
        if len(args) == 0:
            print(usage, file=sys.stderr)
            return ("exit", 1)

        params["desired_program"] = args

        # Get the home directory, if any, and store it in params (often useful).
        try:
            home_dir = os.environ["HOME"]
        except KeyError:
            home_dir = None
        params["home_dir"] = home_dir

        # Default values for options
        params["allow_early_exit"] = False
        params["interactive"] = False
        params["quit_delay"] = "random"
        params["desired_program_pretty_name"] = params["desired_program"][0]
        params["test_mode"] = False

        # General option processing
        for option, value in opts:
            if option in ("-e", "--allow-early-exit"):
                params["allow_early_exit"] = True
            elif option in ("-i", "--interactive"):
                params["interactive"] = True
            elif option in ("-D", "--quit-delay"):
                if value == "random":
                    continue

                try:
                    params["quit_delay"] = int(value)
                    if params["quit_delay"] < 0:
                        raise ValueError()
                except ValueError:
                    print("Invalid value for option -D (--quit-delay): '{0}'"
                          .format(value), file=sys.stderr)
                    return ("exit", 1)
            elif option in ("-p", "--pretty-name"):
                params["desired_program_pretty_name"] = value
            elif option in ("-t", "--test-mode"):
                params["test_mode"] = True
            elif option in ("-v", "--verbose"):
                # Effective level for all child loggers with NOTSET level
                logging.getLogger('flo_check_homework').setLevel(logging.DEBUG)
            else:
                # The options (such as --help) that cause immediate exit
                # were already checked, and caused the function to return.
                # Therefore, if we are here, it can't be due to any of these
                # options.
                assert False, \
                    "Unexpected option received from the getopt module: " \
                    "{!r}".format(option)

        if params["quit_delay"] == "random":
            params["quit_delay"] = 60*random.randint(5, 8)

        return ("continue", 0)

    # Because of all the things we do with QSettings (especially in
    # exercise_generator.py), it is not conceivable to run several instances of
    # this program simultaneously.
    #
    # This method used to be a standalone function defined at module scope, but
    # translations with app.tr() were not able to properly determine the
    # context at runtime, with the result that messages from this function were
    # left untranslated.

    @classmethod
    def getCacheDir(self, msgBoxIcon, informativeText=""):
        """Get the cache directory and create it if necessary."""
        cacheDir = str(QtGui.QDesktopServices.storageLocation(
                QtGui.QDesktopServices.CacheLocation))

        if not cacheDir:
            msgBox = QtGui.QMessageBox(msgBoxIcon, self.tr(progname),
                self.tr(
                "Unable to obtain a location of type <i>CacheLocation</i> "
                "with QtGui.QDesktopServices.storageLocation()."),
                QtGui.QMessageBox.Ok)
            if informativeText:
                msgBox.setInformativeText(informativeText)
            msgBox.setTextFormat(QtCore.Qt.RichText)
            msgBox.exec_()
            return (None, None)

        cacheDirDisplayName = str(QtGui.QDesktopServices.displayName(
                QtGui.QDesktopServices.CacheLocation))
        cacheDirDisplayName = cacheDirDisplayName or cacheDir

        if not os.path.isdir(cacheDir):
            os.makedirs(cacheDir)

        return (cacheDir, cacheDirDisplayName)

    def checkAlreadyRunningInstance(self):
        # Find a place to store the lock file in
        cacheDir, cacheDirDisplayName = self.getCacheDir(
            QtGui.QMessageBox.Critical)
        if not cacheDir:
            sys.exit("Unable to obtain a CacheLocation with "
             "QtGui.QDesktopServices.storageLocation(). Aborting.")

        lockFile = os.path.join(cacheDir, "{0}.pid".format(progname))
        lockFileDisplayName = os.path.join(cacheDirDisplayName,
                                           "{0}.pid".format(progname))
        otherProcessHasLock = True

        for i in range(20):     # For the case where self.validSuperMagicToken
            try:                # is True
                # See the notes in README.lockfile
                lockFileFD = os.open(lockFile, os.O_WRONLY | os.O_CREAT |
                                     os.O_EXCL, 0o666)
            except os.error as e:
                if e.errno != errno.EEXIST:
                    raise
                # When self.validSuperMagicToken is True, flo-check-homework is
                # normally non-interactive, therefore the lock is likely to be
                # released shortly and it is worth retrying after a short time.
                elif self.validSuperMagicToken:
                    time.sleep(0.2)
                    continue
            else:
                # Our process is now holding the lock.
                otherProcessHasLock = False
            break

        if otherProcessHasLock:
            time.sleep(1)
            # We know the PID has been fully written when we encounter
            # os.linesep.
            try:
                with open(lockFile, mode="r", encoding="utf-8",
                          newline=os.linesep) as f:
                    prevSize = 0
                    while True:
                        # We use stat(2) to determine when the file grows and
                        # sleep at regular intervals. This is not the most
                        # elegant algorithm ever written but is nevertheless
                        # reliable. inotify would be more elegant but is
                        # Linux-specific (so far).
                        size = os.stat(lockFile).st_size
                        if size != prevSize:
                            f.seek(0, os.SEEK_SET)
                            line = f.readline()

                            # os.linesep marks the end of the PID and guarantees
                            # we are not reading a half-written PID.
                            if line.endswith(os.linesep):
                                pid = int(line[:-len(os.linesep)])
                                break
                            else:
                                prevSize = size

                        time.sleep(0.1)
            except (os.error, IOError) as e:
                excMsg = e.strerror
                if hasattr(e, "filename") and e.filename is not None:
                    excMsg += ": " + e.filename

                msg = self.tr("""\
{excMsg}

Another instance of '{prog}' has acquired the lock file '{lock}', but it is \
impossible to read that file in order to determine the PID of the other \
instance (for the reason indicated above). This can happen for instance if \
the lock file was removed by the other instance between the moment \
we tried to create it and the moment we tried to read it.

Remedy: check that all instances of '{prog}' are closed and remove the lock \
file manually if it still exists.""").format(
                    excMsg=excMsg, prog=progname, lock=lockFileDisplayName)
                textFormat = QtCore.Qt.PlainText
            else:
                msg = self.tr("""<p>
It seems there is already a running instance of <i>{prog}</i> (PID {pid}). \
If this is not the case, please remove the lock file <tt>{lock}</tt>.
</p>

<p>
Because of the monitoring of asked questions (in order, for instance, \
not to ask the same question twice during a given session), it is not possible \
to run several instances of <i>{prog}</i> simultaneously under the same \
user account.</p>""").format(
                    prog=progname, pid=pid, lock=lockFileDisplayName)
                textFormat = QtCore.Qt.RichText

            msgBox = QtGui.QMessageBox(
                QtGui.QMessageBox.Critical, self.tr(progname),
                msg, QtGui.QMessageBox.Ok)
            msgBox.setTextFormat(textFormat)
            msgBox.exec_()
        else:
            # Write our PID to the lock file, followed by os.linesep
            with open(lockFileFD, mode="w", encoding="utf-8") as f:
                f.write("%d\n" % os.getpid())

        return (otherProcessHasLock, lockFile)

    # Same remark concerning the translation context as for
    # checkAlreadyRunningInstance().
    def checkConfigFileVersion(self):
        res = True
        settings = QtCore.QSettings()

        if settings.contains("SuiviExos/TablesMultDirectCalcs"):
            msgBox = QtGui.QMessageBox(
                QtGui.QMessageBox.Critical, self.tr(progname),
                self.tr("""\
The configuration file <i>{0}</i> was written in an old format. Please \
remove or rename this file before restarting <i>{1}</i>.""").format(
                    settings.fileName(), progname),
                QtGui.QMessageBox.Ok)
            msgBox.setTextFormat(QtCore.Qt.RichText)
            msgBox.exec_()
            res = False

        return res

    @QtCore.pyqtSlot()
    def launchDesiredProgram(self, simpleExec=False):
        if self.mainWindowInitialized:
            self.mainWindow.launchDesiredProgramAct.setEnabled(False)

        if self.launcher:
            args = params["desired_program"]
        else:
            # The first element is the desired program
            args = params["desired_program"][1:]

        # Start the desired program, directly or via self.launcher
        if simpleExec:
            try:
                os.execvp(self.executedProgram,
                          [self.executedProgram] + list(args))
            except (os.error, IOError) as e:
                excMsg = e.strerror
                if hasattr(e, "filename") and e.filename is not None:
                    excMsg += ": " + e.filename

                msg = self.tr("""\
The following error was encountered when trying to execute the desired \
program:

{excMsg}""").format(excMsg=excMsg)
                msgBox = QtGui.QMessageBox(
                    QtGui.QMessageBox.Critical, self.tr(progname),
                    msg, QtGui.QMessageBox.Ok)
                msgBox.setTextFormat(QtCore.Qt.PlainText)
                msgBox.exec_()
        else:
            self.childRunning = True
            self.desiredProgramProcess.start(self.executedProgram, args)

    @QtCore.pyqtSlot()
    def onDesiredProgramStarted(self):
        logger.debug("Program '%s' started." % self.executedProgram)

    @QtCore.pyqtSlot(int, 'QProcess::ExitStatus')
    def onDesiredProgramFinished(self, exitCode, exitStatus):
        if exitStatus == QtCore.QProcess.NormalExit:
            logger.debug("Program '%s' returned exit code %d.",
                         self.executedProgram, exitCode)
        else:
            assert exitStatus == QtCore.QProcess.CrashExit, exitStatus
            msgBox = QtGui.QMessageBox()
            msgBox.setText(self.tr(
                    "The program '{0}' terminated abnormally (maybe killed "
                    "by a signal)."
                    ).format(self.executedProgram))
            msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
            msgBox.setIcon(QtGui.QMessageBox.Warning)
            msgBox.exec_()

        self.childRunning = False
        if self.mainWindowInitialized:
            self.mainWindow.launchDesiredProgramAct.setEnabled(True)

    @QtCore.pyqtSlot('QProcess::ProcessError')
    def onDesiredProgramError(self, processError):
        msg = {
            QtCore.QProcess.FailedToStart:
                self.tr("The program '{0}' could not start; maybe the "
                        "executable cannot be found or you don't have "
                        "the required permissions."
                        ).format(self.executedProgram),
            QtCore.QProcess.UnknownError:
                self.tr("Unknown error while executing the program "
                        "'{0}' (thanks to Qt for the precise diagnosis)."
                        ).format(self.executedProgram) }

        if processError ==  QtCore.QProcess.Crashed:
            logger.info("Program %s crashed." % self.executedProgram)
        else:
            msgBox = QtGui.QMessageBox()
            msgBox.setText(msg[processError])
            msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
            msgBox.setIcon(QtGui.QMessageBox.Warning)
            msgBox.exec_()

        self.childRunning = False
        if self.mainWindowInitialized:
            self.mainWindow.launchDesiredProgramAct.setEnabled(True)

    def checkSuperMagicToken(self):
        cacheDir, cacheDirDisplayName = self.getCacheDir(
            QtGui.QMessageBox.Warning, informativeText=self.tr(
                "It is therefore impossible to find an eventual super magic "
                "token."))
        if not cacheDir:
            return False

        tokenFilePath = os.path.join(cacheDir, "super-magic-token")
        if not os.path.exists(tokenFilePath):
            return False

        with open(tokenFilePath, "r", encoding="utf-8") as tokenFile:
            contents = tokenFile.read()

        try:
            nIntervals, resolution, hashStr = contents.strip().split(' ')
            nIntervals = int(nIntervals)
            resolution = int(resolution)
        except ValueError as e:
            msgBox = QtGui.QMessageBox(
                QtGui.QMessageBox.Warning, self.tr(progname),
                self.tr("Invalid syntax for the super magic token file:"),
                QtGui.QMessageBox.Ok)
            msgBox.setInformativeText(str(e))
            msgBox.setTextFormat(QtCore.Qt.PlainText)
            msgBox.exec_()

        # Current date and time expressed in UTC
        now = datetime.datetime.now(datetime.timezone.utc)
        # Truncate the minutes part to the closest multiple of 'resolution'
        t = now.replace(minute=now.minute - (now.minute % resolution),
                        second=0, microsecond=0)

        for i in range(nIntervals):
            t += datetime.timedelta(minutes=resolution)
            tStr = t.strftime("%Y-%m-%d %H:%M:%S %z")
            tHash = hashlib.sha1(tStr.encode("ascii")).hexdigest()
            # logger.debug("Checking super magic token against %s...", tStr)

            if tHash == hashStr:
                # logger.debug("Super magic token matches that time.")
                self.validSuperMagicToken = True
                break

        if not self.validSuperMagicToken:
            # Expired token, remove it
            os.unlink(tokenFilePath)

        return self.validSuperMagicToken


class InputField(QtGui.QLineEdit):
    """QLineEdit subclass for easy customization of the size hint.

    The size hint can be customized from the constructor, without any
    need for subclassing QLineEdit.

    """
    def __init__(self, parent=None, hSizeHint=None, vSizeHint=None,
                 hSizeHintFM=None, vSizeHintFM=None):
        """Constructor for InputField objects.

        The horizontal part of the size hint returned by sizeHint()
        is specified by hSizeHint, unless None; if None, the
        horizontal part of the size hint returned by the parent class
        is used.

        Ditto for the vertical part and vSizeHint parameter.

        hSizeHintFM (resp. vSizeHintFM) work similarly, but using
        units of fm.averageCharWidth() (resp. fm.lineSpacing()) where
        fm is the QFontMetrics object returned by self.fontMetrics()
        when sizeHint() is called.

        Of course, hSizeHint and hSizeHintFM are mutually exclusive,
        as well as vSizeHint and vSizeHintFM.

        """
        super().__init__(parent)

        assert (hSizeHint is None) or (hSizeHintFM is None), \
            "parameters hSizeHint and hSizeHintFM are mutually exclusive"

        assert (vSizeHint is None) or (vSizeHintFM is None), \
            "parameters vSizeHint and vSizeHintFM are mutually exclusive"

        self.hSizeHint = hSizeHint
        self.vSizeHint = vSizeHint
        self.hSizeHintFM = hSizeHintFM
        self.vSizeHintFM = vSizeHintFM

    def sizeHint(self):
        hint = super().sizeHint()

        if (self.hSizeHintFM is not None) or (self.vSizeHintFM is not None):
            fm = self.fontMetrics()

        if self.hSizeHint is not None:
            hint.setWidth(self.hSizeHint)
        if self.hSizeHintFM is not None:
            hint.setWidth(self.hSizeHintFM * fm.averageCharWidth())

        if self.vSizeHint is not None:
            hint.setHeight(self.vSizeHint)
        if self.vSizeHintFM is not None:
            hint.setHeight(self.vSizeHintFM * fm.lineSpacing())

        return hint


# QtSvg has a number of issues that have been unresolved for a long time,
# among which ignoring of aspect ratio and bad rendering of some files.
# Therefore, we use QPixmap with PNG format for now.
# class AssessmentWidget(QtSvg.QSvgWidget):
#     def __init__(self, file_=None, parent=None):
#         if file_ is None:
#             super().__init__(parent=parent)
#         else:
#             super().__init__(file_, parent=parent)

#     def sizeHint(self):
#         return QtCore.QSize(40, 40)


class MultipleInputQuestionLine(QtCore.QObject):
    # Arguments: line index in its subQuestionnaire, correct (boolean)
    validated = QtCore.pyqtSignal(int, bool)

    def __init__(self, lineIndex, question, IFparams, parent=None):
        super().__init__(parent)

        self.lineIndex = lineIndex # starts from 0
        self.isValidated = False   # avoid name conflict with the signal
        self.question = question

        self.questionLabels = []
        formatInfo = self.question.format_question()
        assert len(formatInfo) == 1 + len(IFparams)

        for info in formatInfo:
            if info is None:
                label = None
            else:
                label = QtGui.QLabel(info["text"])
                label.setTextFormat(QtCore.Qt.PlainText)

                if "help" in info:
                    label.setToolTip(info["help"])

                self.questionLabels.append(label)

        self.inputFields = []
        for i, params in enumerate(IFparams):
            self.inputFields.append(InputField(**params))

            if i >= 1:
                self.inputFields[i-1].returnPressed.connect(
                    self.inputFields[i].setFocus)

        self.inputFields[-1].returnPressed.connect(self.validate)

        self.assessmentWidget = QtGui.QLabel()
        self.useImagesForAssessment = True

        if self.useImagesForAssessment:
            self.pixmapCorrect = QPixmapFromResource("images/happy_cat.png")
            self.pixmapIncorrect = QPixmapFromResource(
                "images/angry_dog_bobi_architetto_francesc_01.png")
            # max(width1, width2) × max(height1, height2)
            size = self.pixmapCorrect.size().expandedTo(
                self.pixmapIncorrect.size())
            # 10 + 10 pixels for left and right margins
            size.setWidth(size.width() + 20)
            self.assessmentWidget.setMinimumSize(size)
            self.assessmentWidget.setAlignment(QtCore.Qt.AlignCenter)
        else:
            # Set a minimum width in order to avoid seeing the label grow
            # when actual text is written to it.
            w = self.assessmentWidget.fontMetrics().width(self.tr(" Ouch! "))
            self.assessmentWidget.setMinimumWidth(w)

        self.validateButton = QtGui.QPushButton(self.tr("Submit"))
        self.validateButton.clicked.connect(self.validate)

    @QtCore.pyqtSlot()
    def validate(self):
        if self.isValidated:
            return

        for widget in self.inputFields:
            widget.setEnabled(False)
        self.validateButton.setEnabled(False)
        correct = self.question.check([ w.text() for w in self.inputFields ])

        if self.useImagesForAssessment:
            self.assessmentWidget.setPixmap(
                self.pixmapCorrect if correct else self.pixmapIncorrect)
            # self.assessmentWidget.load(
            #     u":/images/happy_cat.svg" if correct else
            #     u":/images/angry_dog.svg")
        else:
            self.assessmentWidget.setText(
                self.tr("OK") if correct else self.tr("Ouch!"))

        assert len(self.inputFields) == len(self.question.result_as_strings)

        if not correct:
            for i, result in enumerate(self.question.result_as_strings):
                if self.question.is_correct_result(
                    self.inputFields[i].text(), field=i):
                    continue

                ans = self.inputFields[i].text().strip()
                if not ans:
                    ans = self.tr("<nothing>")
                correction = self.tr("{0} (not {1})").format(result, ans)

                self.inputFields[i].setText(correction)
                palette = self.inputFields[i].palette()
                palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text,
                                 QtGui.QColor(255, 0, 0))
                # palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Base,
                #                  QtGui.QColor(50, 50, 50))
                self.inputFields[i].setPalette(palette)

        self.isValidated = True
        self.validated.emit(self.lineIndex, correct)

    def addToLayout(self, layout):
        # We want to add the line at the bottom of the grid layout
        row = layout.rowCount()
        col = 0

        for i, label in enumerate(self.questionLabels):
            if label is not None:
                layout.addWidget(label, row, col)
                col += 1

            if i < len(self.inputFields):
                layout.addWidget(self.inputFields[i], row, col)
                col += 1

        layout.addWidget(self.assessmentWidget, row, col)
        layout.addWidget(self.validateButton, row, col+1)

    def setFocus(self):
        self.inputFields[0].setFocus()


class SubQuestionnaire(QtCore.QObject):
    # SubQuestionnaire index, new score
    score_updated = QtCore.pyqtSignal(int, int)
    # Signal emitted when all lines  of the SubQuestionnaire have been
    # validated. Argument: SubQuestionnaire index
    all_validated = QtCore.pyqtSignal(int)
    # Signal emitted when When the focus should be transferred to the "next"
    # widget. Argument: SubQuestionnaire index
    focus_next = QtCore.pyqtSignal(int)

    def __init__(self, lineFactory, IFparams, questionGenerator,
                 instruction=None, maxNbQuestions=10,
                 blendIntoPrev=False, parent=None, index=0):
        """Initialize a SubQuestionnaire object.

        questionGenerator must be a "Question generator", as defined
        in exercise_generator.py.

        """
        super().__init__(parent)

        self.lineFactory = lineFactory
        self.IFparams = IFparams
        self.index = index
        self.questionGenerator = questionGenerator
        self.maxNbQuestions = maxNbQuestions
        self.instruction = instruction or None
        self.blendIntoPrev = blendIntoPrev
        self.initializeLines()
        self.score = 0
        self.maxScore = sum([ line.question.score for line in self.lines ])
        self.allValidated = False     # avoid name conflict with the signal
        # obsolete --- One might also use a QSignalMapper
        # self.validateButton_group = QtGui.QButtonGroup(self, exclusive=False)
        # self.validateButton_group.buttonClicked[int].connect(
        #     self.validate_line)
                # validateButton_group.setId(validateButton, i)

    def initializeLines(self):
        self.lines = []
        i = 0

        for question in self.questionGenerator:
            line = self.lineFactory(i, question, self.IFparams)
            line.validated.connect(self.onLineValidated)
            self.lines.append(line)

            i += 1
            if i == self.maxNbQuestions:
                break

    def addToLayout(self, outerLayout):
        if self.instruction is not None:
            instructionLabel = QtGui.QLabel(self.instruction,
                                             wordWrap=True)
            instructionLabel.setTextFormat(QtCore.Qt.RichText)
            outerLayout.addWidget(instructionLabel)

            outerLayout.addSpacing(10)

        self.gridLayout = QtGui.QGridLayout()
        outerLayout.addLayout(self.gridLayout)

        for line in self.lines:
            line.addToLayout(self.gridLayout)

    def addLinesToGridLayout(self, layout):
        """Add lines to an already existing QGridLayout.

        This is useful if one or more subQuestionnaires must be presented
        as a continuation of a previous subQuestionnaire. In particular,
        no vertical space is inserted between the subQuestionnaires and
        then alignment of columns is preserved.

        Users of this class are supposed to call this method instead of
        addToLayout for subQuestionnaires that have the 'blendIntoPrev'
        attribute set to True.

        """
        for line in self.lines:
            line.addToLayout(layout)

    def findNextUnvalidatedLine(self, lineIndex):
        """Find the first unvalidated line after LINEINDEX.

        Return None if there is no such line.

        """
        i = lineIndex + 1

        while i < len(self.lines) and self.lines[i].isValidated:
            i += 1

        return (i if i < len(self.lines) else None)

    @QtCore.pyqtSlot(int, bool)
    def onLineValidated(self, lineIndex, correct):
        """Function run after a line has been validated.

        LINEINDEX starts from 0.
        CORRECT is a boolean indicating whether the answer is correct.

        """
        if correct:
            self.score += self.lines[lineIndex].question.score
            self.score_updated.emit(self.index, self.score)

        for line in self.lines:
            if not line.isValidated:
                break
        else:
            self.allValidated = True
            self.all_validated.emit(self.index)

        i = self.findNextUnvalidatedLine(lineIndex)

        if i is None:
            self.focus_next.emit(self.index)
        else:
            self.lines[i].setFocus()

    def setFocus(self):
        self.lines[0].setFocus()

    def validateAll(self):
        if self.allValidated:
            return

        for i, line in enumerate(self.lines):
            line.validate()

        self.allValidated = True


class FloScrollArea(QtGui.QScrollArea):
    """Subclass of QtGui.QScrollArea with slightly modified sizeHint() method.

    The implementation of sizeHint() mimics that of Qt 4.6.3 with the
    following differences:

      1) The vertical/horizontal scroll bar width/height is added to
         the size hint width/height when the corresponding scroll bar policy
         is one of ScrollBarAlwaysOn, ScrollBarAsNeeded. In contrast, the
         original implementation only does this in the ScrollBarAlwaysOn case.

         This avoids having a useless horizontal scroll bar when the widget
         would only need a vertical scroll bar (and vice versa), as described
         on <https://bugreports.qt.nokia.com//browse/QTBUG-10265>.

      2) The upper bound for the returned QSize is increased from its default
         of (36 * h, 24 * h) in the hope of avoiding the use of scroll bars
         for not-too-small sizes. However, this can be rendered ineffective by
         enclosing widgets having their own upper bounds for the size hint...

    """
    def __init__(self, parent=None):
        super().__init__(parent)

    def sizeHint(self):
        f = 2*self.frameWidth()
        sz = QtCore.QSize(f, f)
        h = self.fontMetrics().height()
        widget = self.widget()

        if widget is not None:
            widgetSize = widget.size()
            if (not widgetSize.isValid()) and self.widgetResizable():
                widgetSize = widget.sizeHint()

            sz += widgetSize
        else:
            sz += QtCore.QSize(12 * h, 8 * h)

        if self.verticalScrollBarPolicy() in (QtCore.Qt.ScrollBarAlwaysOn,
                                              QtCore.Qt.ScrollBarAsNeeded):
            sz.setWidth(sz.width()
                        + self.verticalScrollBar().sizeHint().width())

        if self.horizontalScrollBarPolicy() in (QtCore.Qt.ScrollBarAlwaysOn,
                                                QtCore.Qt.ScrollBarAsNeeded):
            sz.setHeight(sz.height()
                         + self.horizontalScrollBar().sizeHint().height())

        return sz.boundedTo(QtCore.QSize(50 * h, 40 * h))


def _scoreTextConv(x, precision=1):
    assert isinstance(x, numbers.Real), x

    if isinstance(x, numbers.Integral):
        return locale.format("%d", x)
    elif x == math.floor(x):
        return locale.format("%d", int(x))
    else:
        return locale.format("%.*f", (precision, x))

def scoreText(prefix, score, maxScore):
    return translate("app", "{0}{1}/{2}").format(
        prefix, _scoreTextConv(score), _scoreTextConv(maxScore))


class Questionnaire(QtGui.QWidget):
    # Questionnaire index, new score
    score_updated = QtCore.pyqtSignal(int, int)
    # Signal emitted when all subQuestionnaires of the Questionnaire have been
    # validated. Argument: Questionnaire index
    all_validated = QtCore.pyqtSignal(int)

    def __init__(self, label, subQuestionnaires, parent=None, icon=None,
                 index=0):
        super().__init__(parent)

        self.label = str(label)
        self.icon = icon or QtGui.QIcon()
        self.index = index
        self.subQuestionnaires = []
        self.score = 0
        self.maxScore = 0
        self.scorePrefix = self.tr("Score: ")
        self.allValidated = False     # avoid name conflict with the signal

        # QWidget containing the "concatenation" of all subQuestionnaires of
        # self. It will be placed in a QScrollArea, itself in a bigger QWidget
        # (self) containing the validate button and score for the whole
        # questionnaire.
        self.bareQuest = QtGui.QWidget()
        self.bareQuestLayout = QtGui.QVBoxLayout()

        for i, sub in enumerate(subQuestionnaires):
            self.subQuestionnaires.append(sub)
            sub.index = i       # We rely on this!
            sub.setParent(self.bareQuest)
            self.maxScore += sub.maxScore

            if i != 0 and not sub.blendIntoPrev:
                self.bareQuestLayout.addSpacing(10)

            if sub.blendIntoPrev:
                assert i != 0, "blendIntoPrev cannot be set to True for the " \
                    "first subQuestionnaire of a Questionnaire"
                # This subQuestionnaire will add its lines to the last
                # subQuestionnaire that doesn't have blendIntoPrev set to
                # True. This has the benefit to preserve column alignment.
                sub.gridLayout = subQuestionnaires[i-1].gridLayout
                sub.addLinesToGridLayout(sub.gridLayout)
            else:
                sub.addToLayout(self.bareQuestLayout)

            sub.focus_next.connect(self.subQuestRequestFocusNext)
            sub.score_updated.connect(self.updateScore)
            sub.all_validated.connect(self.onSubValidated)

        self.bareQuest.setLayout(self.bareQuestLayout)
        self.scrollArea = FloScrollArea()
        # self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidget(self.bareQuest)

        self.layout = QtGui.QVBoxLayout(self)
        self.layout.addWidget(self.scrollArea)
        self.layout.addSpacing(10)

        bottomLayout = QtGui.QHBoxLayout()

        self.validateButton = QtGui.QPushButton(self.tr("&Submit all"))
        self.validateButton.clicked.connect(self.validateAll)
        bottomLayout.addWidget(self.validateButton)

        bottomLayout.addStretch(1)

        self.scoreWidget = QtGui.QLabel()
        self.updateScoreWidget()
        bottomLayout.addWidget(self.scoreWidget)

        self.layout.addLayout(bottomLayout)

        # hLine = QtGui.QFrame()
        # hLine.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Plain)
        # self.layout.addWidget(hLine)

        # sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
        #                                QtGui.QSizePolicy.Expanding,
        #                                QtGui.QSizePolicy.Frame)
        # self.setSizePolicy(sizePolicy)
        # self.updateGeometry()

    # def sizeHint(self):
    #     return QtCore.QSize(350, 200)

    # def minimumSizeHint(self):
    #     return QtCore.QSize(250, 150)

    def updateScoreWidget(self):
        self.scoreWidget.setText(scoreText(self.scorePrefix, self.score,
                                           self.maxScore))

    @QtCore.pyqtSlot(int)
    def subQuestRequestFocusNext(self, subQuestIndex):
        if subQuestIndex + 1 < len(self.subQuestionnaires):
            self.subQuestionnaires[subQuestIndex + 1].setFocus()
        else:
            self.validateButton.setFocus()

    @QtCore.pyqtSlot(int)
    def onSubValidated(self, subQuestIndex):
        for sub in self.subQuestionnaires:
            if not sub.allValidated:
                break
        else:
            self.validateButton.setEnabled(False)
            self.allValidated = True
            self.all_validated.emit(self.index)

    @QtCore.pyqtSlot()
    def updateScore(self):
        self.score = sum([sub.score for sub in self.subQuestionnaires])
        self.updateScoreWidget()
        self.score_updated.emit(self.index, self.score)

    @QtCore.pyqtSlot()
    def validateAll(self):
        self.validateButton.setEnabled(False)

        if self.allValidated:
            return

        for sub in self.subQuestionnaires:
            # This will automatically set self.allValidated to True once the
            # last subQuestionnaire is validated.
            sub.validateAll()


class MainWidget(QtGui.QTabWidget):
    # New score
    score_updated = QtCore.pyqtSignal(int)
    # Signal emitted when all Questionnaires have been validated.
    all_validated = QtCore.pyqtSignal()

    def __init__(self, questionnaires, parent=None):
        super().__init__(parent)

        self.questionnaires = []
        self.score = self.normalizedScore = 0
        self.maxScore = 0
        self.allValidated = False

        for i, quest in enumerate(questionnaires):
            self.questionnaires.append(quest)
            quest.index = i
            self.maxScore += quest.maxScore

            self.addTab(quest, quest.icon, quest.label)

            quest.score_updated.connect(self.updateScore)
            quest.all_validated.connect(self.onQuestValidated)

    @QtCore.pyqtSlot(int)
    def onQuestValidated(self, questIndex):
        for quest in self.questionnaires:
            if not quest.allValidated:
                break
        else:
            self.allValidated = True
            self.all_validated.emit()

    def validateAll(self):
        if self.allValidated:
            return

        for quest in self.questionnaires:
            # This will automatically set self.allValidated to True once the
            # last questionnaire is validated.
            quest.validateAll()

    @QtCore.pyqtSlot()
    def updateScore(self):
        self.score = sum([quest.score for quest in self.questionnaires])
        self.normalizedScore = self.score / self.maxScore

        self.score_updated.emit(self.score)

    def successfulWork(self):
        return (self.normalizedScore >= score_threshold)

    def setInitialFocus(self):
        try:
            self.questionnaires[0].subQuestionnaires[0].setFocus()
        except IndexError:
            pass


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super().__init__()

        self.allowedToQuit = params["allow_early_exit"] \
            or app.validSuperMagicToken
        self.quitTimer = QtCore.QTimer(self)
        self.quitTimer.setSingleShot(True)
        self.quitTimer.timeout.connect(self.quitTimerTimeout)

        self.magicFormulaAttempts = 0
        self.superMagicFormulaAttempts = 0

        self.mainWidget = MainWidget(self.prepareQuestionnaires())
        self.setCentralWidget(self.mainWidget)

        self.mainWidget.all_validated.connect(self.onAllValidated)
        self.mainWidget.score_updated.connect(self.onScoreUpdate)
        self.mainWidget.setInitialFocus()

        self.setWindowTitle(self.tr("Password check"))

        self.initSettings()
        register_cleanup_handler(self.writeSettings)

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()

        app.mainWindowInitialized = True

    def loadOrInitIntSetting(self, *args, **kwargs):
        return fch_util.loadOrInitIntSetting(self.qSettings, *args, **kwargs)

    def prepareQuestionnaires(self, nbEuclidianDivisions=1, nbDirectMultTables=8,
                              nbDirectAddTables=2, nbRandomAdditions=2,
                              nbBasicSubstractions=2, nbRandomSubstractions=2,
                              nbConjugations=1):
        # Objects used to remember the questions asked during a session, to
        # avoid asking the same question twice in the same session
        divisorsSeen = Seen()
        multSeen = Seen()
        addSeen = Seen()
        subSeen = Seen()
        conjSeen = Seen()

        calcSubQList = [ SubQuestionnaire(
                MultipleInputQuestionLine, ({"hSizeHintFM": 21},
                                            {"hSizeHintFM": 16}),
                EuclidianDivisionGenerator(register_cleanup_handler,
                                  seen=divisorsSeen),
                instruction=self.tr("<i>Division</i> password:"),
                maxNbQuestions=nbEuclidianDivisions),
                         SubQuestionnaire(
                MultipleInputQuestionLine, ({"hSizeHintFM": 20},),
                DirectMultTablesGenerator(register_cleanup_handler,
                                          seen=multSeen),
                instruction=self.tr("<i>Multiplication</i> password:"),
                maxNbQuestions=nbDirectMultTables),
                         SubQuestionnaire(
                MultipleInputQuestionLine, ({"hSizeHintFM": 20},),
                DirectAddTablesGenerator(register_cleanup_handler,
                                         seen=addSeen),
                instruction=self.tr("<i>Addition</i> password:"),
                maxNbQuestions=nbDirectAddTables),
                         SubQuestionnaire(
                MultipleInputQuestionLine, ({"hSizeHintFM": 20},),
                RandomAdditionGenerator(11, 100, seen=addSeen),
                maxNbQuestions=nbRandomAdditions, blendIntoPrev=True),
                         SubQuestionnaire(
                MultipleInputQuestionLine, ({"hSizeHintFM": 20},),
                BasicSubstractionGenerator(register_cleanup_handler,
                                           seen=subSeen),
                instruction=self.tr("<i>Substraction</i> password:"),
                maxNbQuestions=nbBasicSubstractions),
                         SubQuestionnaire(
                MultipleInputQuestionLine, ({"hSizeHintFM": 20},),
                RandomSubstractionGenerator(11, 100, seen=subSeen),
                maxNbQuestions=nbRandomSubstractions, blendIntoPrev=True) ]

        calcQuest = Questionnaire(self.tr("&Calculus"), calcSubQList,
                                  icon=QtGui.QIcon(
                QPixmapFromResource("images/cubic root.png")))

        conjSubQList = []
        # We set disable_needswork to True in order to workaround the strategy
        # where the user writes down the correction before restarting the
        # program.
        conjGenerator = VerbTenseComboGenerator(
            register_cleanup_handler, instruction_type="Qt rich text",
            disable_needswork=True, seen=conjSeen)

        for verb, tense, instruction in conjGenerator:
            conjSubQList.append(SubQuestionnaire(
                    MultipleInputQuestionLine, ({"hSizeHintFM": 45},),
                    ConjugationsGenerator(conjGenerator, verb, tense),
                    instruction=instruction))

            nbConjugations -= 1
            if nbConjugations == 0:
                break

        conjQuest = Questionnaire(self.tr("French C&onjugation"), conjSubQList,
                                  icon=QtGui.QIcon(
                QPixmapFromResource("images/pencil_benji_park_02.png")))

        return [ calcQuest, conjQuest ]

    def closeEvent(self, event):
        if self.allowedToQuit:
            if self.qSettings.value("AllowExitBeforeChild", type=int) == 1 \
                    or not app.childRunning:
                event.accept()
            else:
                msgBox = QtGui.QMessageBox()
                msgBox.setText(self.tr("Impossible to exit now."))
                msgBox.setInformativeText(self.tr(
                        "You are not allowed to quit this program before "
                        "{0} is terminated.").format(
                        params["desired_program_pretty_name"]))
                msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
                msgBox.setIcon(QtGui.QMessageBox.Information)
                msgBox.exec_()

                event.ignore()
        else:
            if not self.quitTimer.isActive():
                # QtCore.QTimer.start() wants the delay in milliseconds
                self.quitTimer.start(params["quit_delay"] * 1000)

            msgBox = QtGui.QMessageBox()
            msgBox.setText(self.tr("Impossible to exit now."))
            msgBox.setInformativeText(self.tr(
                    "I suggest you to examine the corrections before leaving."))
            msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
            # msgBox.setIcon(QtGui.QMessageBox.Information)
            msgBox.setIconPixmap(QPixmapFromResource(
                        "images/warning..._cedric_bosdon_.png"))
            msgBox.exec_()

            event.ignore()

    @QtCore.pyqtSlot()
    def quitTimerTimeout(self):
        self.allowedToQuit = True

    @QtCore.pyqtSlot()
    def about(self):
        aboutText = """\
{ident}\n\n{desc}\n\n{version_blurb1}\n{version_blurb2}""".format(
            ident=self.tr("{progname} {progversion}").format(
                                progname=progname, progversion=progversion),
            desc=self.tr(
        "Little program that allows one to check and consolidate "
        "one's skills..."),
            version_blurb1=version_blurb1, version_blurb2=version_blurb2)
        QtGui.QMessageBox.about(self, self.tr("About {0}").format(progname),
                                aboutText)

    def createActions(self):
        if params["test_mode"]:
            self.testAct = QtGui.QAction(
                QtGui.QIcon(QPixmapFromResource(
                        "images/nebu_work-margin80.png")),
                self.tr("&Test"), self)
            self.testAct.setShortcut(self.tr("Ctrl+T"))
            self.testAct.setStatusTip(self.tr("Test something"))
            self.testAct.triggered.connect(self.test)

        self.launchDesiredProgramAct = QtGui.QAction(
            QtGui.QIcon(QPixmapFromResource(
                    "images/trafficlight-margin20.png")),
            self.tr("&Launch {0}").format(params["desired_program_pretty_name"]),
            self)
        self.launchDesiredProgramAct.setShortcut(self.tr("Ctrl+L"))
        self.launchDesiredProgramAct.setStatusTip(
            self.tr("Launch the program {0}").format(
                params["desired_program_pretty_name"]))
        self.launchDesiredProgramAct.setEnabled(
            app.validSuperMagicToken and not app.childRunning)
        self.launchDesiredProgramAct.triggered.connect(
            app.launchDesiredProgram)

        self.magicFormulaAct = QtGui.QAction(
            QtGui.QIcon(QPixmapFromResource(
                    "images/magic-wand-by-jhnri4_58480760.png")),
            self.tr("&Magic word"), self)
        self.magicFormulaAct.setShortcut(self.tr("Ctrl+M"))
        self.magicFormulaAct.setStatusTip(
            self.tr("Cast a spell"))
        self.magicFormulaAct.triggered.connect(
            self.magicFormula)
        self.magicFormulaAct.setEnabled(not app.validSuperMagicToken)

        self.superMagicFormulaAct = QtGui.QAction(
            QtGui.QIcon(QPixmapFromResource(
                    "images/magic-wand-by-jhnri4+flo_58480760.png")),
            self.tr("&Super magic word"), self)
        self.superMagicFormulaAct.setShortcut(self.tr("Ctrl+S"))
        self.superMagicFormulaAct.setStatusTip(
            self.tr("Cast a super spell (with prolonged effects)"))
        self.superMagicFormulaAct.triggered.connect(
            self.superMagicFormula)
        self.superMagicFormulaAct.setEnabled(not app.validSuperMagicToken)

        self.removeSuperMagicTokenAct = QtGui.QAction(
            QtGui.QIcon(QPixmapFromResource(
                    "images/raemi_Cross_Out-margin160.png")),
            self.tr("&Remove the super magic token"), self)
        self.removeSuperMagicTokenAct.setStatusTip(
            self.tr("Renounce the advantages given by the super magic token"))
        self.removeSuperMagicTokenAct.triggered.connect(
            self.removeSuperMagicToken)
        self.removeSuperMagicTokenAct.setEnabled(app.validSuperMagicToken)

        self.exitAct = QtGui.QAction(
            app.style().standardIcon(QtGui.QStyle.SP_FileDialogEnd),
            self.tr("&Quit"), self)
        self.exitAct.setShortcut(self.tr("Ctrl+Q"))
        # We want this shortcut to work in all application windows.
        self.exitAct.setShortcutContext(QtCore.Qt.ApplicationShortcut)
        self.exitAct.setStatusTip(self.tr("Quit the application"))
        # self.exitAct.setEnabled(False)
        self.exitAct.triggered.connect(self.close)

        self.aboutAct = QtGui.QAction(self.tr(
                "About {0}").format(progname), self)
        self.aboutAct.setStatusTip(
            self.tr("Display information about the program"))
        self.aboutAct.triggered.connect(self.about)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu(self.tr("&File"))
        self.fileMenu.addAction(self.launchDesiredProgramAct)
        if params["test_mode"]:
            self.fileMenu.addAction(self.testAct)
        self.fileMenu.addSeparator();
        self.fileMenu.addAction(self.exitAct)

        self.magicMenu = self.menuBar().addMenu(self.tr("&Magic"))
        self.magicMenu.addAction(self.magicFormulaAct)
        self.magicMenu.addAction(self.superMagicFormulaAct)
        self.magicMenu.addAction(self.removeSuperMagicTokenAct)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu(self.tr("&Help"))
        self.helpMenu.addAction(self.aboutAct)

    def createToolBars(self):
        toolbars = []
        # Doesn't seem to work with Qt 4.8:
        #   self.setStyleSheet("QToolBar { icon-size: 80pt; }")
        self.fileToolBar = self.addToolBar(self.tr("File"))
        if params["test_mode"]:
            self.fileToolBar.addAction(self.testAct)
        self.fileToolBar.addAction(self.launchDesiredProgramAct)
        toolbars.append(self.fileToolBar)

        self.magicToolBar = self.addToolBar(self.tr("Magic"))
        self.magicToolBar.addAction(self.magicFormulaAct)
        self.magicToolBar.addAction(self.superMagicFormulaAct)
        self.magicToolBar.addAction(self.removeSuperMagicTokenAct)
        toolbars.append(self.magicToolBar)

        iconSize = self.qSettings.value("ToolbarIconSize", type=int)
        for tb in toolbars:
            tb.setIconSize(QtCore.QSize(iconSize, iconSize))

    def createStatusBar(self):
        self.statusBar().showMessage(self.tr("Ready"))

    def initSettings(self):
        # This is done earlier, at application startup, to ensure other
        # modules don't initialize the QSettings before the correct format has
        # been defined.
        # QtCore.QSettings.setDefaultFormat(QtCore.QSettings.IniFormat)
        self.qSettings = QtCore.QSettings()

        # This can be used independently of RememberGeometry to workaround
        # some window manager bugs.
        self.restoreGeometry = bool(
            self.loadOrInitIntSetting("RestoreGeometry", 1))

        if self.restoreGeometry:
            if self.qSettings.contains("Position"):
                pos = self.qSettings.value("Position", type='QPoint')
                self.move(pos)
            if self.qSettings.contains("Size"):
                size = self.qSettings.value("Size", type='QSize')
                self.resize(size)

        if not self.qSettings.contains("ProgramLauncher"):
            self.qSettings.setValue("ProgramLauncher", "")

        self.loadOrInitIntSetting("AllowExitBeforeChild", 1)
        self.loadOrInitIntSetting("ToolbarIconSize", 64)

    def writeSettings(self):
        self.rememberGeometry = bool(
            self.loadOrInitIntSetting("RememberGeometry", 1))

        if self.rememberGeometry:
            self.qSettings.setValue("Position", self.pos())
            self.qSettings.setValue("Size", self.size())

        return 0

    @QtCore.pyqtSlot()
    def onAllValidated(self):
        # Possibly display a reward or blame image
        for i in range(len(reward_images)):
            threshold, images = reward_images[-1-i]

            if self.mainWidget.normalizedScore >= threshold:
                break
        else:
            # If reward_images is properly defined with float("-inf") as the
            # lowest threshold, it should be impossible to get there.
            logger.warning("No image list defined in reward_images for "
                           "normalized score {0}. Is this variable properly "
                           "defined?".format(
                    self.mainWidget.normalizedScore))
            images = []

        if images:
            imageRes = random.choice(images)
            rewardWindow = image_widgets.ImageWindow(
                self, QImageFromResource(imageRes))
            rewardWindow.show()

        if self.mainWidget.successfulWork():
            # This enables the program launcher button, among others.
            self.grantSuperMagicToken(10, 15)
            # The exit action is always enabled but only prints an explanatory
            # message without quitting when self.allowedToQuit is False.
            # self.exitAct.setEnabled(True)
        elif not images:
            # Give an explanation if no image was displayed and the score
            # was too low to enable the program launcher button
            msgBox = QtGui.QMessageBox()
            msgBox.setText(self.tr("Wrong password."))
            msgBox.setInformativeText(self.tr(
                    "You must try again and improve your score in order to "
                    "be allowed to launch {0}!").format(
                    params["desired_program_pretty_name"]))
            msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
            # msgBox.setIcon(QtGui.QMessageBox.Information)
            msgBox.setIconPixmap(QPixmapFromResource(
                        "images/warning..._cedric_bosdon_.png"))
            msgBox.exec_()

    @QtCore.pyqtSlot()
    def onScoreUpdate(self):
        msg = scoreText(self.tr("Total score: "),
                        self.mainWidget.score, self.mainWidget.maxScore)
        self.statusBar().showMessage(msg)

        if self.mainWidget.successfulWork():
            self.allowedToQuit = True

    @QtCore.pyqtSlot()
    def test(self):
        logger.info("Running Test action...")
        # app.launchDesiredProgram()

        # imageRes = \
        #     'images/rewards/40-very_happy/Gerald_G_Cartoon_Cat_Walking.png'
        # rewardWindow = image_widgets.ImageWindow(
        #     self, QImageFromResource(imageRes))
        # rewardWindow.show()

        # for w in (rewardWindow, rewardWindow.layout(), rewardWindow.label):
        #     print w.sizeHint(),
        #     if hasattr(w, "sizePolicy"):
        #         print w.sizePolicy().horizontalPolicy(),
        #     print w.maximumSize()

    def grantSuperMagicToken(self, nIntervals, resolution):
        """Grant a super magic token.

        The validity duration d of the generated token will be such that:

          (nIntervals - 1) * resolution <= d <= nIntervals * resolution

        where resolution is expressed in minutes.

        """
        self.magicFormulaAct.setEnabled(False)
        self.superMagicFormulaAct.setEnabled(False)
        self.launchDesiredProgramAct.setEnabled(not app.childRunning)
        self.allowedToQuit = True

        # Find a place to store the token
        cacheDir, cacheDirDisplayName = app.getCacheDir(
            QtGui.QMessageBox.Warning, informativeText=self.tr(
                "It is therefore impossible to store the super magic token "
                "for future sessions."))
        if not cacheDir:
            res = False
        else:
            res = True
            # Current date and time expressed in UTC
            now = datetime.datetime.now(datetime.timezone.utc)
            # Truncate the minutes part to the closest multiple of 'resolution'
            base = now.replace(minute=now.minute - (now.minute % resolution),
                               second=0, microsecond=0)
            endDate = base + datetime.timedelta(minutes=nIntervals*resolution)
            endDateStr = endDate.strftime("%Y-%m-%d %H:%M:%S %z")

            with open(os.path.join(cacheDir, "super-magic-token"), "w",
                      encoding="utf-8") as tokenFile:
                # Make the token slightly opaque to prevent the most obvious
                # forgery
                tokenFile.write("{} {} {}\n".format(nIntervals, resolution,
                      hashlib.sha1(endDateStr.encode("ascii")).hexdigest()))

            app.validSuperMagicToken = True
            self.removeSuperMagicTokenAct.setEnabled(app.validSuperMagicToken)

            msg = self.tr(
                "You are now in possession of a super magic token that will "
                "be valid for about {avg} minutes (actually, between {min} "
                "and {max} minutes).").format(
                avg=round((nIntervals - 0.5) * resolution),
                min=(nIntervals - 1) * resolution,
                max=nIntervals * resolution)
            msgBox = QtGui.QMessageBox(
                QtGui.QMessageBox.Information, self.tr(progname),
                msg, QtGui.QMessageBox.Ok)
            msgBox.setTextFormat(QtCore.Qt.PlainText)
            msgBox.exec_()

        return res

    @QtCore.pyqtSlot()
    def removeSuperMagicToken(self):
        cacheDir, cacheDirDisplayName = app.getCacheDir(
            QtGui.QMessageBox.Warning, informativeText=self.tr(
                "It is therefore impossible to find or remove any super magic "
                "token."))
        if not cacheDir:
            return False

        tokenFilePath = os.path.join(cacheDir, "super-magic-token")
        if not os.path.exists(tokenFilePath):
            msg = self.tr("There is no super magic token to remove!")
            msgBox = QtGui.QMessageBox(
                QtGui.QMessageBox.Warning, self.tr(progname),
                msg, QtGui.QMessageBox.Ok)
            msgBox.setTextFormat(QtCore.Qt.PlainText)
            msgBox.exec_()

            self.magicFormulaAttempts = 0 # Start afresh
            self.magicFormulaAct.setEnabled(True)
            self.superMagicFormulaAttempts = 0 # Start afresh
            self.superMagicFormulaAct.setEnabled(True)
            app.validSuperMagicToken = False
            self.removeSuperMagicTokenAct.setEnabled(False)
            return False

        msg = self.tr("Are you sure you want to remove the super magic token?")
        msgBox = QtGui.QMessageBox(
            QtGui.QMessageBox.Warning, self.tr(progname),
            msg)
        removeButton = msgBox.addButton(self.tr("&Remove"),
                                        QtGui.QMessageBox.AcceptRole)
        cancelButton = msgBox.addButton(QtGui.QMessageBox.Cancel)
        msgBox.setDefaultButton(removeButton)
        msgBox.setEscapeButton(cancelButton)
        msgBox.setTextFormat(QtCore.Qt.PlainText)
        msgBox.exec_()
        clickedButton = msgBox.clickedButton()

        if clickedButton == cancelButton:
            return False
        assert clickedButton == removeButton, (clickedButton, removeButton)

        try:
            os.unlink(tokenFilePath)
        except (os.error, IOError) as e:
            excMsg = e.strerror
            if hasattr(e, "filename") and e.filename is not None:
                excMsg += ": " + e.filename

            msg = self.tr("""\
The following error was encountered when trying to remove the super magic \
token:

{excMsg}""").format(excMsg=excMsg)
            msgBox = QtGui.QMessageBox(
                QtGui.QMessageBox.Warning, self.tr(progname),
                msg, QtGui.QMessageBox.Ok)
            msgBox.setTextFormat(QtCore.Qt.PlainText)
            msgBox.exec_()
            return False

        self.magicFormulaAttempts = 0 # Start afresh
        self.magicFormulaAct.setEnabled(True)
        self.superMagicFormulaAttempts = 0 # Start afresh
        self.superMagicFormulaAct.setEnabled(True)
        self.launchDesiredProgramAct.setEnabled(False)
        self.allowedToQuit = False

        app.validSuperMagicToken = False
        self.removeSuperMagicTokenAct.setEnabled(False)

        return True

    def _GenericMagicFormula(self, formulaType, counterAttr, maxAttempts,
                            title, prompt, failedText, informativeFailedText):
        if getattr(self, counterAttr) >= maxAttempts:
            return ("too many attempts", None)

        R1 = random.randint(4, 99)
        R2 = random.randint(4, 99)

        text, ok = QtGui.QInputDialog.getText(
            self, title, prompt.format(R1, R2), QtGui.QLineEdit.Password)

        h = time.localtime().tm_hour

        if ok:
            # Increment the counter that keeps track of the number of attempts
            setattr(self, counterAttr,  getattr(self, counterAttr) + 1)

            try:
                i = int(text)
                cond = True
            except ValueError:
                if formulaType == "super":
                    try:
                        # This will avoid nasty surprises such as:
                        #   269.462 - 269              => 0.4619999999999891
                        #   int(1000*(269.462 - 269))  => 461
                        d = Decimal(text)
                    except decimal.InvalidOperation:
                        return ("failed", None)
                    else:
                        i = int(d)
                        d1, d3 = ( getDecimalDigit(d, n) for n in (1, 3) )
                        cond = d >= 0 and 10*d1 + d3 == 2*h
                else:
                    return ("failed", None)

            r1 = int(math.sqrt(R1))
            r2 = int(math.sqrt(R2))
            res = "passed" if (cond and i == 10*(h+r1) + r2) else "failed"

            return (res, text)
        else:
            return ("cancelled", None)

    def GenericMagicFormula(self, formulaType, counterAttr, maxAttempts,
                            title, prompt, failedText, informativeFailedText):
        outcome, data = self._GenericMagicFormula(
            formulaType, counterAttr, maxAttempts,
            title, prompt, failedText, informativeFailedText)

        if outcome == "too many attempts":
            msgBox = QtGui.QMessageBox()
            msgBox.setText(failedText)
            msgBox.setInformativeText(informativeFailedText)
            msgBox.setTextFormat(QtCore.Qt.PlainText)
            msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
            msgBox.setIcon(QtGui.QMessageBox.Information)
            msgBox.exec_()
        elif outcome == "failed":
            msg = self.tr("Sorry, but you don't appear to be a wizard.")
            msgBox = QtGui.QMessageBox(
                QtGui.QMessageBox.Information, self.tr(progname),
                msg, QtGui.QMessageBox.Ok)
            msgBox.setTextFormat(QtCore.Qt.PlainText)
            msgBox.exec_()
        else:
            assert outcome in ("passed", "cancelled"), outcome

        return (outcome, data)

    @QtCore.pyqtSlot()
    def magicFormula(self):
        maxAttempts = 3

        title = self.tr("Magic word")
        prompt = self.tr("I say {0} and {1}. Please enter the magic word.")
        failedText = self.tr("Too many failed attempts for the magic word.")
        informativeFailedText = self.tr(
            "After {0} failed attempts, the magic wand stops working.").format(
            maxAttempts)
        outcome, data = self.GenericMagicFormula(
            "standard", "magicFormulaAttempts", maxAttempts, title, prompt,
            failedText, informativeFailedText)

        if outcome == "passed":
            self.magicFormulaAct.setEnabled(False)
            self.launchDesiredProgramAct.setEnabled(not app.childRunning)
            self.allowedToQuit = True

    @QtCore.pyqtSlot()
    def superMagicFormula(self):
        maxAttempts = 2

        title = self.tr("Super magic word")
        prompt = self.tr(
            "I say {0} and {1}. Please enter the super magic word.")
        failedText = self.tr(
            "Too many failed attempts for the super magic word.")
        informativeFailedText = self.tr(
            "After {0} failed attempts at the super magic word, the "
            "wand stops working.").format(maxAttempts)
        outcome, text = self.GenericMagicFormula(
            "super", "superMagicFormulaAttempts", maxAttempts, title, prompt,
            failedText, informativeFailedText)

        if outcome != "passed":
            return

        # Resolution in minutes
        resolution = 15

        try:
            i = int(text)
        except ValueError:
            # Allow decimal values
            try:
                d = Decimal(text)
            except decimal.InvalidOperation:
                assert False, "{!r} should be a readable as a decimal " \
                    "according to earlier validation".format(text)
            hundredthsDigit = getDecimalDigit(d, 2)
            hours = 2*(10 - hundredthsDigit)
            # The validity duration d of the generated token will be such that:
            #
            #   (nIntervals - 1) * resolution <= d <= nIntervals * resolution
            nIntervals = round(60*hours / resolution)
        else:
            # Duration of the super magic token in case no decimal part was
            # entered
            nIntervals = 10     # 2.5*60/15 = 10

        tokenSuccessfullyWritten = self.grantSuperMagicToken(nIntervals,
                                                             resolution)


# Early program initialization
random.seed()
locale.setlocale(locale.LC_ALL, '')

# Create the QApplication instance and initialize modules
app = HomeWorkCheckApp(sys.argv)

# Note: this requires a working translation system.
action, retcode = app.processCommandLine( tuple(map(str, app.arguments())) )
if action == "exit":
    sys.exit(retcode)

# Working l10n requires the QApplication instance well initialized to have the
# QTranslator objects set up and installed in the application.
from .exercise_generator import Seen, EuclidianDivisionGenerator, \
    DirectMultTablesGenerator, \
    DirectAddTablesGenerator, RandomAdditionGenerator, \
    BasicSubstractionGenerator, RandomSubstractionGenerator, \
    VerbTenseComboGenerator, ConjugationsGenerator

# Must be done before app.checkAlreadyRunningInstance(), because when there is
# a super magic token, the lock file is likely to be released shortly after its
# creation, and we need a specific algorithm to allow almost simultaneous
# executions of the desired program(s) in these conditions.
app.checkSuperMagicToken()

# Use a lock file to determine if another instance is already running
locked, lockFile = app.checkAlreadyRunningInstance()
if locked:
    sys.exit(1)

# If we are here, it means we have just created the lock file containing
# our PID, and we are responsible for removing it.
try:
    app.endInit()               # Things that need the lock file control
    if not app.checkConfigFileVersion():
        sys.exit(1)

    interactive = params["interactive"] \
        or app.qSettings.value("ForceInteractive", type=int) == 1 \
        or not app.validSuperMagicToken

    if interactive:
        app.mainWindow = MainWindow()
        app.mainWindow.show()
        retcode = app.exec_()
finally:
    os.unlink(lockFile)

if app.validSuperMagicToken and not interactive:
    # The following call does an execvp(2) or similar, therefore it is
    # necessary to flush all buffers associated to modified files beforehand.
    # Since the QSettings should have been used only for reads in this code
    # path, there is no need to call its sync() method, which would probably
    # cause significant work to the hard drive.
    app.launchDesiredProgram(simpleExec=True)
    # Getting here means that the execvp(2) call failed.
    retcode = 127

sys.exit(retcode)
