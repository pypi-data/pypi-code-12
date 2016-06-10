#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import subprocess
import logging
from ffmpymedia.parser import ProbeContext
from ffmpymedia import ffprobe_path


class MediaProbe:
    """Wrapper class that provides access to  all probing funcionalities"""

    @staticmethod
    def _ffprobe_media_file(filename, path=ffprobe_path):
        """Helper method that calls ffprobe and returns it's output as a string

        Args:
            filename (str): The full path filename of the file to be probed
            path (str): The path to the ffprobe utility

        Returns:
            str: The output of the ffprobe command
        """
        if os.path.exists(filename) and not os.access(filename, os.R_OK):
            raise IOError('File {} not accessible.'.format(filename))
        logging.info('Iniciando probing do arquivo {}'.format(filename))
        comando = [path, filename]
        saida = subprocess.check_output(comando, stderr=subprocess.STDOUT).decode()

        return saida

    @staticmethod
    def _parse_ffprobe_output(ffprobe_output):
        """Helper method that parses the ffprobe output into a dict

        Args:
            ffprobe_output (str): The output from the ffprobe command call.

        Returns:
            dict: ffprobe params
        """
        ctx = ProbeContext(ffprobe_output)
        return ctx.process()

    @staticmethod
    def get_media_file_input_params(filename, path=ffprobe_path):
        """Returns the input media params

        Args:
            filename (str): The full path filename of the file to be probed
            path (str): The path to the ffprobe utility

        Returns:
            dict: The input media params

        """
        return MediaProbe.get_params_from_ffprobe(MediaProbe._ffprobe_media_file(filename, path))

    @staticmethod
    def get_params_from_ffprobe(ffprobe_output):
        """Processes ffprobe otput and returns only the first files parameters

        Args:
            ffprobe_output (str | TextIOBase): The output string from ffprobe or io.TextIOBase from a live ffmpeg process
        """
        resultado = MediaProbe._parse_ffprobe_output(ffprobe_output)
        return resultado.get('Input 0')
