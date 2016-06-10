#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Media operations and data structures
"""

from ffmpymedia import __author__, __version__, __version_info__, __copyright__
from ffmpymedia import probe
import os
import logging


class MediaAnalyser:
    """
    Static Class that aggregates media comparison and validation
    """

    @staticmethod
    def compare_media_file_with_template(media_file, media_file_template):
        """Compares an input MEdiaFile parameters against a MediaFileTemplate parameters

        Args:
            media_file (MediaFile): MediaFile object to be compared
            media_file_template (MediaFileTempalte): MediaFileTemplate

        Returns:
            dict: a dict with only the keys that exist in media_file_template and not in media_file

        """
        descriptor = probe.MediaProbe.get_media_file_input_params(media_file)
        media_file = MediaFile(**descriptor)
        if isinstance(media_file_template, dict):
            media_file_template = MediaFileTemplate(**media_file_template)
        elif isinstance(media_file_template, MediaFileTemplate):
            pass
        else:
            raise ValueError('media_file_template must be a MediaFileTemplate instance or a dict')

        if media_file_template != media_file:
            return media_file_template.difference(media_file)

    @staticmethod
    def validate_with_template(media_file, media_file_template):
        logging.debug('MEDIAANALYSER - Validação com gabarito: {}, {}'.format(media_file, media_file_template))
        if isinstance(media_file_template, dict):
            media_file_template = MediaFileTemplate(**media_file_template)
        elif isinstance(media_file_template, MediaFileTemplate):
            pass
        else:
            raise ValueError('media_file_template must be a MediaFileTemplate instance or a dict')

        descriptor = probe.MediaProbe.get_media_file_input_params(media_file)
        media_file = MediaFile(**descriptor)
        return media_file_template == media_file

    @staticmethod
    def media_file_difference(filename1, filename2):
        return MediaFile.parse_file(filename1).difference(MediaFile.parse_file(filename2))


class _FFMPEGStream():
    """
    Abstract parent class for the Media Streams. Enforces allowed Media Stream types.
    """

    allowed_types = ['audio', 'video', 'image', 'subtitle', 'data', 'attachment']

    def __new__(cls, *args, **kwargs):
        try:
            stream_type = kwargs.get('type')
            if not stream_type: raise ValueError
            assert stream_type.lower() in MediaStream.allowed_types
            return super(_FFMPEGStream, cls).__new__(cls)
        except AssertionError as e:
            logging.error('Invalid media stream type: {}'.format(kwargs.get('type')))
        except ValueError as e:
            logging.error('Media stream type must be filled.')


    def __eq__(self, other):
        """
        Compares the layout of the MediaStreamTemplate with another MediaStreamTemplate or a MediaStream.
        Doesn't take stream metadata into account.

        Args:
            other (_FFMPEGStream): The other stream to calculate the difference

        Returns:
            bool: Returns false if any key in the other dict has a different value
        """
        for key in self.__dict__.keys():
            if key != 'metadata':
                if key in other.__dict__.keys():
                    if self.__dict__[key] != other.__dict__[key]:
                        return False
                else:
                    return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def difference(self, other, include_metadata=False):
        """
        Calculates the difference between this Stream and the other stream

        Args:
            other (_FFMPEGStream): The other stream to calculate the difference
            include_metadata (bool): Flag to include metadata in the comparison

        Returns:
            dict: A dict of tuples in the following format: {fieldname: (actual_value, expected_value)}
        """
        difference = {}
        for key in self.__dict__.keys():
            if key == 'metadata':
                if include_metadata:
                    if key in other.__dict__.keys():
                        for meta_key in self.__dict__.get('metadata').keys():
                            if meta_key in other.__dict__.get('metadata').keys():
                                if self.__dict__.get('metadata')[meta_key] != other.__dict__.get('metadata')[meta_key]:
                                    if difference.get('metadata') == None:
                                        difference['metadata'] = {}
                                    difference.get('metadata')[meta_key] = (other.__dict__.get('metadata')[meta_key],
                                                                            self.__dict__.get('metadata')[meta_key])
                            else:
                                difference.get('metadata')[meta_key] = (None, self.__dict__.get('metadata')[meta_key])
                    else:  # if metadata is only present in the template
                        if difference.get('metadata') == None:
                            difference['metadata'] = {}
                        difference['metadata'] = self.__dict__.get('metadata')
            elif key == 'disposition':
                if key in other.__dict__.keys():
                    for meta_key in self.__dict__.get('disposition').keys():
                        if meta_key in other.__dict__.get('disposition').keys():
                            if self.__dict__.get('disposition')[meta_key] != other.__dict__.get('disposition')[meta_key]:
                                if difference.get('disposition') == None:
                                    difference['disposition'] = {}
                                difference.get('disposition')[meta_key] = (other.__dict__.get('disposition')[meta_key],
                                                                           self.__dict__.get('disposition')[meta_key])
                        else:
                            difference.get('disposition')[meta_key] = (None, self.__dict__.get('disposition')[meta_key])
                else:  # if dispositions is only present in the template
                    difference['dispositions'] = self.__dict__.get('dispositions')
            else:
                if key in other.__dict__.keys():
                    if self.__dict__[key] != other.__dict__[key]:
                        difference[key] = (other.__dict__[key], self.__dict__[key])

        return difference


class MediaStream(_FFMPEGStream):
    """
    Representa um fluxo de mídia
    """

    def __init__(self, **kwargs):
        self.__dict__ = kwargs

    def __str__(self):
        result = self.__dict__.get('type') + ' Stream: {}'.format(', '.join(['{}: {}'.format(k, v) for k, v in sorted(self.__dict__.items())]))
        return result

    def __repr__(self):
        return 'MediaStream(**'+str(self.__dict__)+')'


#Classes representando os gabaritos dos fluxos de midia
class MediaStreamTemplate(_FFMPEGStream):
    """
    Representa o modelo de um fluxo de mídia
    """

    def __init__(self, **kwargs):
        self.__dict__ = kwargs

    def __str__(self):
        return '{} stream template: {}'.format(self.__dict__.get('type'),
                                               ', '.join(['{}: {}'.format(k, v) for k, v in sorted(self.__dict__.items())]))

    def __repr__(self):
        return 'MediaStreamTemplate(**'+str(self.__dict__)+')'


class _FFMPEGContainer:
    """
    Base para as abstrações representando arquivos de mídia
    """

    def __eq__(self, other):
        for key in self.__dict__.keys():
            if key != 'metadata':
                if key == 'streams':
                    for stream in self.streams:
                        if stream != other.streams[self.streams.index(stream)]:
                            return False
                elif self.__dict__[key] != other.__dict__[key]:
                    return False
        return True

    def difference(self, other, include_metadata=False):
        """
        Retorna as diferenças entre o template do fluxo e o fluxo. Cada campo é retornado com uma dupla
        {campo: (valor encontrado, valor esperado)}
        :param other: VideoStream
        :return: dict
        """
        difference = {}
        for key in self.__dict__.keys():
            if key != 'metadata':
                if key == 'streams':
                    for stream in self.streams:
                        if stream != other.streams[self.streams.index(stream)]:
                            if not difference.get('streams'):
                                difference['streams'] = []
                            difference['streams'].append(stream.difference(other.streams[self.streams.index(stream)]))
                elif key in other.__dict__.keys():
                    if self.__dict__[key] != other.__dict__[key]:
                        difference[key] = (other.__dict__[key], self.__dict__[key])
            elif include_metadata and key == 'metadata':
                if key in other.__dict__.keys():
                    for meta_key in self.__dict__.get('metadata').keys():
                        if meta_key in other.__dict__.get('metadata').keys():
                            if self.__dict__.get('metadata')[meta_key] != other.__dict__.get('metadata')[meta_key]:
                                if difference.get('metadata') == None:
                                    difference['metadata'] = {}
                                difference.get('metadata')[meta_key] = (other.__dict__.get('metadata')[meta_key],
                                                                        self.__dict__.get('metadata')[meta_key])
                        else:
                            difference.get('metadata')[meta_key] = (None, self.__dict__.get('metadata')[meta_key])
                else:  # if metadata is only present in the template
                    if difference.get('metadata') == None:
                        difference['metadata'] = {}
                    difference['metadata'] = self.__dict__.get('metadata')
        return difference


class MediaFile(_FFMPEGContainer):
    """Abstracts a Media File, made of various media streams"""

    def __new__(cls, *args, **kwargs):
        """Checks if the file exists and abort instance creation if not.

        Args:
            **dict: media file input params

        Returns:
            MediaFile: A representation of the media file
        """
        try:
            if len(kwargs) > 0:
                assert os.access(kwargs.get('filename'), os.R_OK)
            if len(kwargs) > 1:
                if not kwargs.get('duration') or not kwargs.get('start_time') or\
                        not kwargs.get('bit_rate') or not kwargs.get('format_name'):
                    raise AttributeError('MediaFile - ERRO - Lista de parâmetros incompleta')
            return super(MediaFile, cls).__new__(cls)
        except AssertionError as e:
            logging.error('Erro. Não foi possível acessar o arquivo {}.'.format(kwargs.get('filename')))
            return None
        except AttributeError as e:
            logging.error(e)
            return None

    @staticmethod
    def parse_file(file):
        return MediaFile(**probe.MediaProbe.get_media_file_input_params(file))

    def __init__(self, **kwargs):
        self.filename = kwargs.get('filename')
        if len(kwargs) == 1:  # Caso só haja o filename
            kwargs.update(probe.MediaProbe.get_media_file_input_params(self.filename))

        # Se houver os outros parâmetros
        self.duration = kwargs.get('duration')
        self.start_time = kwargs.get('start_time')
        self.bitrate = kwargs.get('bit_rate')
        self.metadata = kwargs.get('metadata')
        self.type = kwargs.get('format_name')

        self.streams = []
        for stream in kwargs.get('streams'):
            self.streams.append(MediaStream(**stream))

    def __str__(self):
        return 'Arquivo {}'.format(self.filename)

    def __repr__(self):
        output = {}
        output['filename'] = self.filename
        output['duration'] = self.duration
        output['start_time'] = self.start_time
        output['bit_rate'] = self.bitrate
        output['metadata'] = self.metadata
        output['streams'] = []
        for stream in self.streams:
            output['streams'].append(stream.__dict__)

        return str('MediaFile(**'+str(output)+')')

    def get_streams(self):
        """Returns all streams defined in the media file.

        Returns:
            list: [MediaStreams]
        """
        result = []
        for stream in self.streams:
            result.append(stream)
        return result

    def __get_streams_by_type(self, type):
        """Returns all streams of a supplied type defined in the media file.

            Args:
                type (str): 'video', 'image', 'audio', 'subtitle', 'data' or 'attachment'

            Returns:
                list: [MediaStreams]
            """
        result = []
        for stream in self.streams:
            if stream.type == type:
                result.append(stream)
        return result

    def get_video_streams(self):
        return self.__get_streams_by_type('video')

    def get_image_streams(self):
        return self.__get_streams_by_type('image')

    def get_audio_streams(self):
        return self.__get_streams_by_type('audio')

    def get_subtitle_streams(self):
        return self.__get_streams_by_type('subtitle')

    def get_data_streams(self):
        return self.__get_streams_by_type('data')

    def get_attachments(self):
        return self.__get_streams_by_type('attachment')


class MediaFileTemplate(_FFMPEGContainer):
    """Abstracts a MEdia File parameters.
    It is used for validation and for generating FFMPEG transcoding commands.
    """

    def __init__(self, **kwargs):
        self.type = kwargs.get('format_name') or kwargs.get('type')

        if kwargs.get('duration'):
            self.duration = kwargs.get('duration')
        if kwargs.get('start_time'):
            self.start_time = kwargs.get('start_time')
        if kwargs.get('bit_rate'):
            self.bitrate = kwargs.get('bit_rate')
        if kwargs.get('metadata'):
            self.metadata = kwargs.get('metadata')
        self.streams = []
        for stream in kwargs.get('streams'):
            self.streams.append(MediaStreamTemplate(**stream))

    def __str__(self):
        return '{} File Template: {}'.format(self.type, self.__dict__)

    def __repr__(self):
        return 'MediaFileTemplate(**'+str(self.__dict__)+')'