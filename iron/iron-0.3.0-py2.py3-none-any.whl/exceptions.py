from click import style


class IronError(Exception):
    pass


class IronFileNotFound(IronError):
    pass


class IronTaskError(IronError):
    def __init__(self, message, task):
        self.message = message
        self.task = task

    def __str__(self):
        return style(self.message, fg='red') + ' occurred in ' + style(self.task.name, fg='blue')


class ExternalCommandError(IronTaskError):
    def __init__(self, message, task, cmd, cwd, details=None):
        super().__init__(message, task)
        self.cmd = cmd
        self.cwd = cwd
        self.details = details

    def __str__(self):
        return (style(self.message, fg='red') + ' (from task ' +
                style(self.task.name, fg='blue') + ')\n' +
                'cmd was: ' + style(' '.join(self.cmd), fg='blue') + '\n' +
                'cwd was: ' + style(str(self.cwd), fg='blue') +
                '\n\nDetails:\n' +
                self.details)
