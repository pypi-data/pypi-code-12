from .startstop import get_pid


def status(**args):
    pid = int(get_pid('DreamDaemon'))
    if pid:
        print('Сервер работает. PID: {0}'.format(pid))
    else:
        print('Сервер не работает')
