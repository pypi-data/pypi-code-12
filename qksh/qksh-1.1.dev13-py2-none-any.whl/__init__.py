# TODO: implement qkshell, autocompletion, CLI command to get command output.
# CMD2 package. maybe we can create the shell on ipython
import sys
import os


def _create_log_folder():
    try:
        if os.path.exists('/var/log/qksh/'):
            if os.stat('/var/log/qksh/').st_mode & 0777 == 0777:
                pass
            else:
                os.chmod('/var/log/qksh', 0777)
        else:
            os.mkdir('/var/log/qksh')
            os.chmod('/var/log/qksh', 0777)
    except Exception as e:
        print e
        sys.exit(1)

    open('/var/log/qksh/qksh.log', 'a').close()
    os.chmod('/var/log/qksh/qksh.log', 0777)

_create_log_folder()


