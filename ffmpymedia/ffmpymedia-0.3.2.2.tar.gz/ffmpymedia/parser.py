#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import re
import datetime
from ffmpymedia.defs import *

def decodedatetime(datestring):
    """
    Faz a decodificação das representações de datas da saída do ffmpeg para o objeto nativo datetime.
    """
    if re.match('[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}', datestring):
        return datetime.datetime.strptime(datestring, '%Y-%m-%d %H:%M:%S')
    elif re.match('(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) [0-9]{2} [0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}', datestring):
        return datetime.datetime.strptime(datestring, '%b %d %Y %H:%M:%S')
    else:
        raise ValueError('date string "{}" does not match any supported date format.'.format(datestring))


def timecode_to_seconds(timecode):
    return str((int(timecode[0:2])*3600)+(int(timecode[3:5])*60)+(int(timecode[6:8]))+(int(timecode[9:])/100))


def prepare_remaining(remaining, keys):
    for key in keys:
        remaining = remaining.replace('({})'.format(key), '')
    return remaining.strip('\n').rstrip()


def reset_class_counters():
    Input.reset_count()
    InputStreamLineParser.reset_count()
    Output.reset_count()


#############################
# Abstract Class Definition #
#############################
class Context:
    """
    Classe abstrata que define a assinatura do contexto.
    """
    def __init__(self, parse_string):
        if isinstance(parse_string, io.TextIOBase):
            self.parse_string = parse_string
        elif isinstance(parse_string, str):
            self.parse_string = io.StringIO(parse_string)
        else:
            raise ValueError('parse_string must be a str or a io.TextIOBase child, not {}'.format(type(parse_string)))

        self.result = {}
        self.subcontext = None
        self.current_line = None
        reset_class_counters()

    def next_line(self):
        raise NotImplementedError

    def process(self):
        raise NotImplementedError


class Parser:
    """
    Classe abstrata ancestral dos Parsers
    """

    def __init__(self, context):
        self.context = context
        self.root = None
        self.state = None

    def process(self):
        raise NotImplementedError


class State:
    """
    Classe abstrata que define a assinatura dos estados
    """
    def process(self, parser):
        raise NotImplementedError


class LineParser:
    """
    Classe abstrata que define a assinatura dos SubContextos
    """
    count = 0

    @classmethod
    def reset_count(cls):
        cls.count = 0

    def __init__(self):
        self.root = {}
        self.state = None
        self.remaining = None

    def process(self, parser):
        raise NotImplementedError


##############################
# Context Classes Definition #
##############################
class ProbeContext(Context):
    """
    Objeto de contexto utilizado para a análise de mídia através da interpretação da saída do ffprobe.
    Contém o resultado do processamento e armazena o estado da máquina.
    """
    def __init__(self, parse_string):
        super().__init__(parse_string)
        self.subcontext = Header(self)

    def next_line(self):
        self.current_line = self.parse_string.readline()
        return self.current_line

    def process(self):
        while self.next_line():
            self.subcontext.process()
        return self.result


#################################
# LineParser Classes Definition #
#################################
class InputDurationLineParser(LineParser):
    """
    Faz a interpretação da linha de duração dos Inputs.
    """
    def process(self, parser):
        if re.match('^    Stream ', parser.context.current_line):
            parser.state = InputStreamLineParser()
            parser.state.process(parser)
        elif re.match('^    Chapter ', parser.context.current_line):
            parser.state = InputChapterLineParser()
            parser.state.process(parser)
        else:
            self.state = InputDuration()
            self.remaining = parser.context.current_line
            while self.remaining:
                self.state.process(self)
            parser.root.update(self.root)


class InputStreamLineParser(LineParser):
    """
    Faz a interpretação da linha de descrição dos Fluxos.
    """
    format = None

    @classmethod
    def reset(cls):
        cls.format = None
        cls.reset_count()

    def process(self, parser):
        if re.match('^    Chapter ', parser.context.current_line):
            parser.state = InputChapterLineParser()
            parser.state.process(parser)
        elif re.match('^    Metadata:', parser.context.current_line):
            self.root['metadata'] = {}
            parser.state = StreamMetadata(self)
        elif re.match('^    Stream ', parser.context.current_line):
            self.root = {}
            self.root['disposition'] = {"default": 1 if '(default)' in parser.context.current_line else 0,
                                        "dub": 0,
                                        "original": 0,
                                        "comment": 0,
                                        "lyrics": 0,
                                        "karaoke": 0,
                                        "forced": 1 if '(forced)' in parser.context.current_line else 0,
                                        "hearing_impaired": 0,
                                        "visual_impaired": 0,
                                        "clean_effects": 0,
                                        "attached_pic": 0}

            self.state = StreamIndex()
            self.remaining = prepare_remaining(parser.context.current_line,
                                               self.root.get('disposition').keys())

            while self.remaining:
                self.state.process(self)
            if not parser.root.get('streams'):
                parser.root['streams'] = []
            parser.root['streams'].append(self.root)
            InputStreamLineParser.count += 1


class InputChapterLineParser(LineParser):
    """
    Faz a interpretação da linha de descrição dos Fluxos.
    """
    def process(self, parser):
        if re.match('^    Stream ', parser.context.current_line):
            parser.state = InputStreamLineParser()
            parser.state.process(parser)
        elif re.match('^    Metadata:', parser.context.current_line):
            self.root['metadata'] = {}
            parser.state = ChapterMetadata(self)
        elif re.match('^    Chapter ', parser.context.current_line):
            # Should be default.
            self.root = {}
            self.state = ChapterIndex()
            self.remaining = parser.context.current_line.strip('\n')
            while self.remaining:
                self.state.process(self)
            if not parser.root.get('chapters'):
                parser.root['chapters'] = []
            parser.root['chapters'].append(self.root)
            InputChapterLineParser.count += 1

#############################
# Parser Classes Definition #
#############################
class Header(Parser):
    """
    Parser para o bloco de cabeçalho do ffprobe.
    """

    def __init__(self, context):
        super().__init__(context)
        self.root = context.result['header'] = {}

        self.state = Version()

    def process(self):
        self.state.process(self)


class Input(Parser):
    """
    Parser para o bloco de arquivo de entrada do ffprobe/ffmpeg.
    """
    count = 0

    @classmethod
    def reset_count(cls):
        cls.count = 0

    def __init__(self, context):
        super().__init__(context)
        self.root = context.result['Input {}'.format(Input.count)] = {}
        Input.count += 1

        self.state = PreInputMessages()

    def process(self):
        self.state.process(self)


class CodecMessages(Parser):

    def __init__(self, context):
        super().__init__(context)
        self.root = {}

        self.state = CodecLine()

    def process(self):
        self.state.process(self)


class Output(Parser):
    """
    Parser para o bloco de arquivo de entrada do ffprobe/ffmpeg.
    """
    count = 0

    @classmethod
    def reset_count(cls):
        cls.count = 0

    def __init__(self, context):
        super().__init__(context)
        self.root = context.result['Input {}'.format(Input.count)] = {}
        Input.count += 1

        self.state = InputLine()

    def process(self):
        self.state.process(self)


########################
# Parser State Classes #
########################

# Estados do Parser Header
class Version(State):
    """
    Utilitário e versão
    """
    def process(self, parser):
        values = re.match('(ffmpeg|ffprobe) version (.*) Copyright.*\n', parser.context.current_line)
        parser.root.update(dict(zip(['util', 'version'], values.groups())))
        parser.state = Build()


class Build(State):
    """
    Data e compilador usado na compilação do FFMPEG.
    """
    def process(self, parser):
        if re.match('^  built on (.*) with (.*)', parser.context.current_line):
            values = re.match('^  built on (.*) with (.*)', parser.context.current_line)
            parser.root.update(dict(zip(['build_date'], [decodedatetime(values.groups()[0])])))
        elif re.match('^  built with (\S*?) (\S*?)', parser.context.current_line):
            values = re.match('^  built with (\S*?) (\S*?)', parser.context.current_line)
            parser.root.update(dict(zip(['compiler', 'compiler_version'],
                                        [values.groups()[0],
                                         values.groups()[1]])))
        parser.state = Configuration()


class Configuration(State):
    """
    Lerá a linha de configuração.
    """
    def process(self, parser):
        parser.state = LibVersions()


class LibVersions(State):
    """
    Estados que buscam as versões das bibliotecas.
    """
    def process(self, parser):
        if re.match('^  (\S*)\s*(\S*)\s*(\S*) /', parser.context.current_line):
            values = re.match('^  (\S*)\s*(\S*)\s*(\S*) /', parser.context.current_line)
            parser.root.update(dict(zip([values.groups()[0]], [values.groups()[1]+values.groups()[2]])))
        else:
            parser.context.subcontext = Input(parser.context)
            parser.context.subcontext.process()


# Estados do Parser Input
class PreInputMessages(State):
    """
    Processa mensagens gerais prévias ao primeiro Input
    """
    def process(self, parser):
        if re.match('^Input', parser.context.current_line):
            parser.state = InputLine()
            parser.state.process(parser)


class InputLine(State):
    """
    Tipo e nome do arquivo.
    """
    def process(self, parser):
        values = re.match('Input #\d*,\s(.*),\sfrom\s\'(.*)\':', parser.context.current_line)
        parser.root.update({'format_name': values.groups()[0],
                            'format_long_name': get_format_long_name(values.groups()[0]),
                            'filename': values.groups()[1]})

        #Resets input parametares and defines input format
        InputStreamLineParser.reset()
        InputStreamLineParser.format = values.groups()[0]

        parser.state = InputMetadata()


class InputMetadata(State):
    """
    Metadados do bloco de entrada.
    """
    def __init__(self):
        self.root = {}

    def process(self, parser):
        if re.match('^  Duration:', parser.context.current_line):
            parser.state = InputDurationLineParser()
            parser.state.process(parser)
        elif re.match('^  Metadata:', parser.context.current_line):
            self.root = parser.root['tags'] = {}
        else:
            values = re.match('^    (\S*)\s*: (.*?)\s*$', parser.context.current_line).groups()
            self.root.update({values[0]: values[1]})


class InputDuration(State):
    """
    Recupera a duração do container, convertidas para segundos.
    """
    def process(self, parser):
        if re.match('^  Duration: N/A', parser.remaining):
            values = re.match('^  Duration: (N/A)', parser.remaining)
            parser.root.update({'duration': 0})
        elif re.match('^  Duration: [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{2}', parser.remaining):
            values = re.match('^  Duration: ([0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{2})', parser.remaining)
            parser.root.update({'duration': timecode_to_seconds(values.groups()[0])})
        parser.remaining = parser.remaining[values.end():]
        if re.match(', start', parser.remaining):
            parser.state = InputStartTime()
        elif re.match(', bitrate: (\d*) kb/s', parser.remaining) or re.match(', bitrate: (\S*)', parser.remaining):
            parser.state = InputBitrate()


class InputStartTime(State):
    """
    Busca o tempo de início do container
    """
    def process(self, parser):
        values = re.match(', start: (\d*\.\d*)', parser.remaining)
        parser.root.update({'start_time': values.groups()[0]})
        parser.remaining = parser.remaining[values.end():]
        parser.state = InputBitrate()


class InputBitrate(State):
    """
    Busca o bitrate do container
    """
    def process(self, parser):
        if re.match(', bitrate: (\d*) kb/s', parser.remaining):
            values = re.match(', bitrate: (\d*) kb/s', parser.remaining)
            parser.root.update({'bit_rate': str(int(values.groups()[0])*1000)})
        elif re.match(', bitrate: (\S*)', parser.remaining):
            parser.root.update({'bit_rate': 0})
        parser.remaining = ''


class ChapterIndex(State):
    """
    Índice do capitulo.
    """
    def process(self, parser):
        values = re.match('^    Chapter #\d:(\d)', parser.remaining)
        parser.root.update({'id': values.groups()[0],
                            'time_base': '1/1000000000'})
        parser.remaining = parser.remaining[values.end():]
        parser.state = ChapterStart()


class ChapterStart(State):
    """
    Inicio do Capitulo.
    """
    def process(self, parser):
        values = re.match(': start (\d*.\d*),', parser.remaining)
        parser.root.update({'start': int(float(values.groups()[0])),
                            'start_time': values.groups()[0]})
        parser.remaining = parser.remaining[values.end():]
        parser.state = ChapterEnd()


class ChapterEnd(State):
    """
    Inicio do Capitulo.
    """
    def process(self, parser):
        values = re.match(' end (\d*.\d*)', parser.remaining)
        parser.root.update({'end': int(float(values.groups()[0])),
                            'end_time': values.groups()[0]})
        parser.remaining = parser.remaining[values.end():]


class ChapterMetadata(State):
    """
    Metadados do capitulo
    """
    def __init__(self, sub_context):
        self.root = sub_context.root['metadata']

    def process(self, parser):
        if re.match('^    Chapter ', parser.context.current_line):
            # If Chapter line is detected
            parser.state = InputChapterLineParser()
            parser.state.process(parser)
        elif re.match('^    Stream ', parser.context.current_line):
            # If Stream line is detected
            parser.state = InputStreamLineParser()
            parser.state.process(parser)
        elif re.match('^Input', parser.context.current_line):
            # If Input line is detected
            parser.context.subcontext = Input(parser.context)
            parser.context.subcontext.process()
        elif re.match('^      \S*\s*: .*?\s*$', parser.context.current_line):  # Default
            values = re.match('^      (\S*)\s*: (.*?)\s*$', parser.context.current_line).groups()
            if values[0] == 'creation_time':
                self.root.update({values[0]: decodedatetime(values[1])})
            else:
                self.root.update({values[0]: values[1]})


#General Stream States
class StreamIndex(State):
    """
    Índice do fluxo.
    """
    def process(self, parser):
        values = re.match('^    Stream #\d:(\d)', parser.remaining)
        parser.root.update({'index': values.groups()[0]})
        parser.remaining = parser.remaining[values.end():]
        if parser.remaining.startswith('('):
            parser.state = StreamLanguage()
        else:
            parser.state = StreamType()


class StreamLanguage(State):
    """
    Linguagem do fluxo.
    """
    def process(self, parser):
        values = re.match('\((\S*)\)', parser.remaining)
        parser.root.update({'language': values.groups()[0]})
        parser.remaining = parser.remaining[values.end():]
        parser.state = StreamType()


class StreamType(State):
    """
    Tipo do fluxo.
    """
    def process(self, parser):
        values = re.match(':\s(\S*):\s', parser.remaining)
        parser.root.update({'type': values.groups()[0].lower()})
        parser.remaining = parser.remaining[values.end():]
        if values.groups()[0] == 'Video':
            if InputStreamLineParser.format in image_formats.keys():
                parser.state = StillImageStreamCodec()
            else:
                parser.state = VideoStreamCodec()
        elif values.groups()[0] == 'Audio':
            parser.state = AudioStreamCodec()
        elif values.groups()[0] == 'Data':
            parser.state = DataStreamCodec()
        elif values.groups()[0] == 'Subtitle':
            parser.state = SubtitleStreamCodec()
        elif values.groups()[0] == 'Attachment':
            parser.state = AttachmentStreamCodec()
        else:
            parser.remaining = ''


class StreamMetadata(State):
    """
    Metadados do fluxo.
    """
    def __init__(self, sub_context):
        self.root = sub_context.root['metadata']

    def process(self, parser):
        if re.match('^    Stream ', parser.context.current_line):
            # If stream line is detected
            parser.state = InputStreamLineParser()
            parser.state.process(parser)
        elif re.match('^    Chapter ', parser.context.current_line):
            # If Chapter line is detected
            parser.state = InputChapterLineParser()
            parser.state.process(parser)
        elif re.match('^Input', parser.context.current_line):
            # If Input line is detected
            parser.context.subcontext = Input(parser.context)
            parser.context.subcontext.process()
        elif re.match('^      \S*\s*: .*?\s*$', parser.context.current_line):
            # If metadata line is detected
            values = re.match('^      (\S*)\s*: (.*?)\s*$', parser.context.current_line).groups()
            if values[0] == 'creation_time':
                self.root.update({values[0]: decodedatetime(values[1])})
            else:
                self.root.update({values[0]: values[1]})


# Video Stream States
class VideoStreamCodec(State):
    """
    Codec do fluxo.
    """
    def process(self, parser):
        if re.match('\S*,\s', parser.remaining):
            # Codec without profile or tag
            values = re.match('(\S*),\s', parser.remaining)
        elif re.match('\S*\s', parser.remaining):
            # Codec with profile or tag
            values = re.match('(\S*)\s', parser.remaining)

        parser.root.update({'codec': values.groups()[0],
                            'codec_long_name': get_codec_long_name(values.groups()[0])})
        parser.remaining = parser.remaining[values.end():]

        if values.groups()[0] in image_codecs.keys():
            if re.match('\S*, ', parser.remaining):
                parser.state = StillImagePixelFormat()
        else:
            if re.match('\(\S*\s/\s\S*\),', parser.remaining):
                parser.state = VideoStreamCodecSpec() # When theres only the codec spec
            elif re.match('\(\S*\)\s\(\S*\s/\s\S*\),', parser.remaining) or re.match('\(.*?\),', parser.remaining):
                parser.state = VideoStreamCodecProfile() # When theres a profile and spec


class VideoStreamCodecProfile(State):
    """
    Perfil do codec.
    """
    def process(self, parser):
        values = re.match('\((.*?)\),?\s', parser.remaining)
        parser.root.update({'profile': values.groups()[0]})
        parser.remaining = parser.remaining[values.end():]
        if re.match('\(\S*\s/\s\S*\),', parser.remaining):
            parser.state = VideoStreamCodecSpec()
        else:
            parser.state = VideoStreamPixelFormat()


class VideoStreamCodecSpec(State):
    """
    Etiquetas do codec.
    """
    def process(self, parser):
        values = re.match('\((\S*)\s/\s(\S*)\), ', parser.remaining)
        parser.root.update({'codec_tag_string': values.groups()[0],
                            'codec_tag': values.groups()[1]})
        parser.remaining = parser.remaining[values.end():]
        parser.state = VideoStreamPixelFormat()


class VideoStreamPixelFormat(State):
    """
    Tipo de amostragem, intervalo de cor e espaço de cor.
    """
    def process(self, parser):
        if re.match('(\S*?)\(\S*?,\s\S*\),', parser.remaining):
            values = re.match('(\S*?)\(', parser.remaining)
            parser.state = VideoStreamColorSpec()
        elif re.match('\S*,\s', parser.remaining):
            values = re.match('(\S*),\s.', parser.remaining)
            parser.state = VideoStreamResolution()
        parser.root.update({'pixel_format': values.groups()[0]})
        parser.remaining = parser.remaining[values.end()-1:]


class VideoStreamColorSpec(State):
    """
    Intervalo e espaço de cor.
    """
    def process(self, parser):
        values = re.match('\((\S*?),\s(\S*)\), ', parser.remaining)
        parser.root.update({'color_range': values.groups()[0],
                            'color_space': values.groups()[1]})
        parser.remaining = parser.remaining[values.end():]
        parser.state = VideoStreamResolution()


class VideoStreamResolution(State):
    """
    Largura, altura, e razões de aspecto.
    """
    def process(self, parser):
        values = re.match('(\d*)x(\d*),?\s\[?SAR\s(\d*:\d*)\sDAR\s(\d*:\d*)\]?, ', parser.remaining)
        parser.root.update({'width': values.groups()[0],
                            'height': values.groups()[1],
                            'sample_aspect_ratio': values.groups()[2],
                            'display_aspect_ratio': values.groups()[3]})
        parser.remaining = parser.remaining[values.end():]
        if re.match('(\d*.?\d*) fps, (\d*.?\d*) tbr, (\S*?) tbn, (\S*?) tbc', parser.remaining):
            parser.state = VideoStreamTimeBase()
        else:
            parser.state = VideoStreamBitrate()


class VideoStreamTimeBase(State):
    """
    fps, tbr, tbn, tbc.
    """
    def process(self, parser):
        values = re.match('(\d*.\d*) fps, (\d*.\d*) tbr, (\S*?) tbn, (\S*?) tbc', parser.remaining)
        parser.root.update({'reported_frame_rate': values.groups()[0],
                            'average_frame_rate': values.groups()[1],
                            'container_time_base': values.groups()[2],
                            'codec_time_base': values.groups()[3]})
        parser.remaining = parser.remaining[values.end():]


class VideoStreamBitrate(State):
    """
    Bitrate.
    """
    def process(self, parser):
        if re.match('max\. \d* kb/s', parser.remaining):
            values = re.match('max\. (\d*) kb/s', parser.remaining)
            parser.root.update({'max_bit_rate': values.groups()[0]})
        else:
            values = re.match('(\d*) kb/s', parser.remaining)
            parser.root.update({'bitrate': values.groups()[0]})
        parser.remaining = parser.remaining[values.end():]
        if parser.remaining.startswith(', '):
            parser.remaining = parser.remaining[2:]
        parser.state = VideoStreamTimeBase()


# Image Stream States
class StillImageStreamCodec(State):
    """
    Codec do fluxo.
    """
    def process(self, parser):
        # Codec without profile or tag
        values = re.match('(\S*),\s', parser.remaining)
        parser.root.update({'codec': values.groups()[0],
                            'codec_long_name': get_codec_long_name(values.groups()[0])})
        parser.remaining = parser.remaining[values.end():]
        parser.state = StillImagePixelFormat()

class StillImageStreamCodecSpec(State):
    """
    """
    def process(self, parser):
        pass


class StillImagePixelFormat(State):
    """
    """
    def process(self, parser):
        if re.match('\S*?\(', parser.remaining):
            values = re.match('(\S*?)\(', parser.remaining)
        elif re.match('\S*, ', parser.remaining):
            values = re.match('(\S*), .', parser.remaining)
        parser.root.update({'pixel_format': values.groups()[0]})
        parser.remaining = parser.remaining[values.end()-1:]
        if re.match('\(\S*?,\s\S*\), ', parser.remaining):
            parser.state = StillImageColorSpec()
        else:
            parser.state = StillImageResolution()


class StillImageColorSpec(State):
    """
    """
    def process(self, parser):
        values = re.match('\((\S*?),\s(\S*)\), ', parser.remaining)
        parser.root.update({'color_range': values.groups()[0],
                            'color_space': values.groups()[1]})
        parser.remaining = parser.remaining[values.end():]
        parser.state = StillImageResolution()


class StillImageResolution(State):
    def process(self, parser):
        if re.match('\d*x\d*,?\s\[?SAR\s\d*:\d*\sDAR\s\d*:\d*\]?, ', parser.remaining):
            values = re.match('(\d*)x(\d*),?\s\[?SAR\s(\d*:\d*)\sDAR\s(\d*:\d*)\]?, ', parser.remaining)
            parser.root.update({'width': values.groups()[0],
                                'height': values.groups()[1],
                                'sample_aspect_ratio': values.groups()[2],
                                'display_aspect_ratio': values.groups()[3]})
        elif re.match('\d*x\d*, ', parser.remaining):
            values = re.match('(\d*)x(\d*), ', parser.remaining)
            parser.root.update({'width': values.groups()[0],
                                'height': values.groups()[1]})
        parser.remaining = parser.remaining[values.end():]
        parser.state = StillImageStreamTimeBase()


class StillImageStreamTimeBase(State):
    """
    tbr, tbn, tbc.
    """
    def process(self, parser):
        values = re.match('(\d*.?\d*) tbr, (\S*?) tbn, (\S*?) tbc', parser.remaining)
        parser.root.update({'average_frame_rate': values.groups()[0],
                            'container_time_base': values.groups()[1],
                            'codec_time_base': values.groups()[2]})
        parser.remaining = parser.remaining[values.end():]


# Audio Stream States
class AudioStreamCodec(State):
    """
    Codec do fluxo.
    """
    def process(self, parser):
        if re.match('\S*,\s', parser.remaining):
            values = re.match('(\S*),\s', parser.remaining)
        elif re.match('\S*\s', parser.remaining):
            values = re.match('(\S*)\s', parser.remaining)
        parser.root.update({'codec': values.groups()[0],
                            'codec_long_name': get_codec_long_name(values.groups()[0])})
        parser.remaining = parser.remaining[values.end():]
        if re.match('\(\S*\)\s\(\S*\s/\s\S*\),', parser.remaining) or re.match('\(\S*\),', parser.remaining):
            parser.state = AudioStreamCodecProfile() # When theres a profile and spec
        elif re.match('\(\S*\s/\s\S*\),', parser.remaining):
            parser.state = AudioStreamCodecSpec() # When theres only the codec spec
        elif re.match('\d*\sHz,', parser.remaining):
            parser.state = AudioStreamSamplingRate() # When theres the Sampling Rate


class AudioStreamCodecProfile(State):
    """
    Perfil do codec.
    """
    def process(self, parser):
        values = re.match('\((\S*?)\),?\s', parser.remaining)
        parser.root.update({'profile': values.groups()[0]})
        parser.remaining = parser.remaining[values.end():]
        if re.match('\(\S*\s/\s\S*\),', parser.remaining):
            parser.state = AudioStreamCodecSpec()
        else:
            parser.state = AudioStreamSamplingRate()


class AudioStreamCodecSpec(State):
    """
    Etiquetas do codec.
    """
    def process(self, parser):
        values = re.match('\((\S*)\s/\s(\S*)\), ', parser.remaining)
        parser.root.update({'codec_tag_string': values.groups()[0],
                            'codec_tag': values.groups()[1]})
        parser.remaining = parser.remaining[values.end():]
        parser.state = AudioStreamSamplingRate()


class AudioStreamSamplingRate(State):
    """
    Taxa de amostragem do audio
    """
    def process(self, parser):
        values = re.match('(\S*) Hz, ', parser.remaining)
        parser.root.update({'sample_rate': values.groups()[0]})
        parser.remaining = parser.remaining[values.end():]
        parser.state = AudioStreamLayout()


class AudioStreamLayout(State):
    """
    Taxa de amostragem do audio
    """
    def process(self, parser):
        values = re.match('(.*?), ', parser.remaining)
        parser.root.update({'channel_layout': values.groups()[0]})
        if values.groups()[0] == 'stereo':
            parser.root.update({'channels': 2})
        elif '5.1' in values.groups()[0]:
            parser.root.update({'channels': 6})
        parser.remaining = parser.remaining[values.end():]
        parser.state = AudioStreamSampleFormat()


class AudioStreamSampleFormat(State):
    """
    Taxa de amostragem do audio
    """
    def process(self, parser):
        if re.match('\S*\s\(\d*\s\S*\)', parser.remaining):
            values = re.match('(\S*)\s\((\d*)\s\S*\)', parser.remaining)
            parser.root.update({'sample_fmt': values.groups()[0],
                                'bits_per_raw_sample': values.groups()[1]})
        elif re.match('\S*,?\s?', parser.remaining):
            values = re.match('(\S*),?\s?', parser.remaining)
            parser.root.update({'sample_fmt': values.groups()[0]})
        parser.remaining = parser.remaining[values.end():]
        parser.state = AudioStreamBitrate()


class AudioStreamBitrate(State):
    """
    Bitrate.
    """
    def process(self, parser):
        values = re.match('(\d*) kb/s', parser.remaining)
        parser.root.update({'bitrate': str(int(values.groups()[0])*1000)})
        parser.remaining = parser.remaining[values.end():]


# Data Stream States
class DataStreamCodec(State):
    """
    Codec do fluxo.
    """
    def process(self, parser):
        if re.match('\S*,\s', parser.remaining):
            values = re.match('(\S*),\s', parser.remaining)
        elif re.match('\S*\s', parser.remaining):
            values = re.match('(\S*)\s', parser.remaining)
        parser.root.update({'codec': values.groups()[0]})
        parser.remaining = parser.remaining[values.end():]
        parser.state = DataStreamCodecSpec()


class DataStreamCodecSpec(State):
    """
    Etiquetas do codec.
    """
    def process(self, parser):
        values = re.match('\((\S*)\s/\s(\S*?)\)', parser.remaining)
        parser.root.update({'codec_tag_string': values.groups()[0],
                            'codec_tag': values.groups()[1]})
        parser.remaining = ""


class SubtitleStreamCodec(State):
    """
    Codec das legendas.
    """
    def process(self, parser):
        # Codec without profile or tag
        values = re.match('(\S*),?\s?', parser.remaining)
        parser.root.update({'codec': values.groups()[0],
                            'codec_long_name': get_codec_long_name(values.groups()[0])})
        parser.remaining = parser.remaining[values.end():]


class AttachmentStreamCodec(State):
    """
    Codec do Anexo.
    """
    def process(self, parser):
        # Codec without profile or tag
        values = re.match('(\S*),?\s?', parser.remaining)
        parser.root.update({'codec': values.groups()[0]})
        parser.remaining = parser.remaining[values.end():]


class PNGStreamTimeBase(State):
    """
    tbr, tbn, tbc.
    """
    def process(self, parser):
        values = re.match('(\d*.?\d*) tbr, (\d*.?\d*) tbn, (\d*.?\d*) tbc', parser.remaining)
        parser.root.update({'average_frame_rate': values.groups()[0],
                            'container_time_base': values.groups()[1],
                            'codec_time_base': values.groups()[2]})
        parser.remaining = parser.remaining[values.end():]
        if parser.remaining == '':
            parser.remaining = ''


class CodecLine(State):
    def process(self, parser):
        if re.match('^Output', parser.context.current_line):
            parser.context.subcontext = Output(parser.context)
            parser.context.subcontext.process()

