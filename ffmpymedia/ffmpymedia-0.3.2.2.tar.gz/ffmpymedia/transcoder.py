class _DataPad:

    data_types = ['video', 'audio', 'subtitles', 'data']

    def __init__(self):
        self.__data_type = None
        self.media_stream = None

    @property
    def data_type(self):
        return self.__data_type

    @data_type.setter
    def data_type(self, dt):
        if dt in _DataPad.data_types:
            self.__data_type = dt
        else:
            raise ValueError('Data type {} isn\'t allowed'.format(dt))


class VideoDataPad(_DataPad):

    def __init__(self):
        super().__init__()
        self.data_type = 'video'


class AudioDataPad(_DataPad):

    def __init__(self):
        super().__init__()
        self.data_type = 'audio'


class SubtitleDataPad(_DataPad):

    def __init__(self):
        super().__init__()
        self.data_type = 'subtitle'


class ArbitraryDataPad(_DataPad):

    def __init__(self):
        super().__init__()
        self.data_type = 'data'


class _InputNode:

    def __init__(self, media_file=None, template=None):
        pass

