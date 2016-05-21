class ProgressCallback(object):
    def __init__(self, progress, maxval=None):
        self.progress = progress
        self.maxval = maxval
        self.minval = 0
        if self.maxval:
            self.progress.maxval = self.maxval
    def __call__(self, done, total=None):
        if total and not self.maxval:
            self.progress.maxval = total
        self.progress.update(done + self.minval)

class BaseProgressbar(object):
    def __init__(self, supress=False, maxval=None):
        self.supress = supress
        self.maxval = maxval
        self.minval = 0
        self.progress = None
    def __enter__(self):
        if not self.supress:
            try:
                self.progress = self.setup_progressbar()
                self.progress.start()
                return ProgressCallback(self.progress, self.maxval)
            except ImportError:
                self.supress = True
                import warnings
                warnings.warn("progressbar not found. Please pip install progressbar")
        if self.supress:
            def cb(*args, **kwargs): # pylint: disable=unused-argument
                pass
            return cb

    def __exit__(self, type, value, traceback): # FIXME pylint: disable=redefined-builtin
        if self.progress and hasattr(self.progress, 'finish'):
            self.progress.finish()

    def setup_progressbar(self):
        from progressbar import ProgressBar, Bar, Percentage
        return ProgressBar(widgets=[Bar(), ' ', Percentage()])

class FileTransferProgressbar(BaseProgressbar):
    def setup_progressbar(self):
        from progressbar import ProgressBar, FileTransferSpeed, Bar, Percentage, ETA
        return ProgressBar(widgets=[FileTransferSpeed(), ' <<<', Bar(), '>>> ', Percentage(), ' ', ETA()])
