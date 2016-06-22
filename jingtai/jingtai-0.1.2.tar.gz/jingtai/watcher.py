from concurrent.futures import ThreadPoolExecutor

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .server import send


observer = None


def start_watcher(dir_list):
    global observer
    watcher = Watcher()
    observer = Observer()
    for dirname in dir_list:
        observer.schedule(watcher, dirname, recursive=True)
    observer.start()


class Watcher(FileSystemEventHandler):
    def dispatch(self, evt):
        if not evt.is_directory:
            print('%s: %s' % (evt.event_type, evt.src_path))
            send('reload')

    def stop(self):
        observer.join()
