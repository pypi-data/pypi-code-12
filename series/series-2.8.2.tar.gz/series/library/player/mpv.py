from mpv import MPV as Player, _mpv_terminate_destroy

from series.library.player.interface import PlayerInterface

class Callback:

    def __init__(self, func):
        self._func = func

    def call(self):
        self._func()


class MPV(PlayerInterface):

    def __init__(self, args):
        super().__init__(Player(**args))
        self._player.event_callbacks.append(Callback(self.event))

    def stop(self):
        _mpv_terminate_destroy(self._player.handle)
        self._player = None

    def pause(self):
        self._player.pause = not self._player.pause.val

    def osd(self, level):
        self._player.osd_level = level

    def osd_level(self):
        return self._player.osd_level

    def __getattr__(self, name):
        try:
            return super().__getattr__(name)
        except TypeError:
            pass

    def event(self):
        try:
            pass
        except Exception as e:
            self.log.error(e)

__all__ = ['MPV']
