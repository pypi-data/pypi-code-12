
import subprocess
import logging


def edit_file(filename, editor='emacs'):
    return edit_file_direct(filename, editor=editor)


def edit_file_direct(filename, editor='emacs'):
    p = None
    try:
        p = subprocess.Popen([editor, filename])
    except:
        logging.exception("error starting editor")
    else:
        try:
            p.wait()
        except:
            logging.exception("error waiting for editor")
        finally:
            if p.returncode is None:
                p.terminate()

        logging.info("editor exited")

    del(p)

    return
