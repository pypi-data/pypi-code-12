import sys
import time

from click import echo

from .commands import run_commands


_watch_rules = set()


def watch_forever(env, verbose):
    """
    Starts the watcher.  This is the meat driving the ``iron watch`` shell
    command.
    """
    try:
        from watchdog.events import FileDeletedEvent, PatternMatchingEventHandler
        from watchdog.observers import Observer
    except ImportError:
        echo('The watcher requires watchdog to be installed.')
        sys.exit(3)

    class CommandTrigger(PatternMatchingEventHandler):
        def __init__(self, patterns, cmdname, env, verbose):
            super().__init__(patterns=patterns, ignore_patterns=['.DS_Store'], ignore_directories=True)
            self.cmdname = cmdname
            self.env = env
            self.verbose = verbose

        def on_any_event(self, event):
            if isinstance(event, FileDeletedEvent):
                # HACK: My vim is a bit messed up and deletes a file before
                # writing it, meaning this will typically trigger 2 changes
                # for every save, and thus 2 rebuilds.  The proper way to
                # handle this is to batch the events for, say 0.1 seconds, and
                # only when nothing happens within this time window, execute
                # it.  I.e. always take a 0.1 delay, but avoid the double
                # trigger.
                echo('*Ignoring file deletion* {}'.format(event.src_path))
                return

            echo('>>> Running {}'.format(self.cmdname))
            run_commands([self.cmdname], self.env, self.verbose)

    observer = Observer(timeout=1.7)

    for name, paths, patterns in sorted(_watch_rules):
        handler = CommandTrigger(patterns, name, env, verbose)

        for path in paths:
            patstr = ', '.join(patterns) if patterns else 'any file'
            echo('Will trigger {} when {} changes in {}'.format(name, patstr, path))
            observer.schedule(handler, path, recursive=True)

    observer.start()
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print('Stopping file system watches...')
        observer.stop()
    observer.join()
