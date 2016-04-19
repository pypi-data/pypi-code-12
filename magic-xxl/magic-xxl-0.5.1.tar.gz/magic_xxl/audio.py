"""
Audio

Requires
- SOX
- WAV2PNG
- WAV2JSON
- BPM-TOOLS

"""
from __future__ import division
import os
import subprocess
from tempfile import mkstemp
import requests
from mutagen.mp3 import MP3


def hex_color_to_rgba(value):
    """
    Convert HEX color to RGBA color - rrggbbaa (8chars)
    :param value:
    :return:
    """
    value = value.lower().lstrip('#')
    if len(value) == 8:
        return value
    if len(value) == 3:
        value = ''.join([v*2 for v in list(value)])
    return value + "ff"

def get_file_name(filename):
    """
    Return the filename without the path
    """
    return os.path.basename(filename)

def get_file_extension(filename):
    """
    Return a file extension, without the dot
    """
    return os.path.splitext(filename)[1][1:].lower()

def run(cmd):
    ps = subprocess.Popen(cmd,
                     shell=True,
                     stdout=subprocess.PIPE,
                     stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    return output


def get_from_url(url, dest=None):
    """
    Download from url
    :param url:
    :param dest:
    :return:
    """
    if not dest:
        _, dest = mkstemp()
        ext = url.split("?")[0] if "?" in url else url
        dest = "%s.%s" % (dest, get_file_extension(ext))
        os.close(_)

    with open(dest, 'wb') as handle:
        response = requests.get(url, stream=True)
        if not response.ok:
            raise ValueError("Unable to download file '%s'" % url)
        for block in response.iter_content(1024):
            handle.write(block)
    return dest

def is_valid(src):
    return True

def gen_waveform(src,
                 dest,
                 fgcolor="2e4562ff",
                 bgcolor="00000000",
                 channels="left right",
                 width=960,
                 height=100):
    """
    Generate the PNG and JSON waveform of an audio file

    :param src: the source file. ie: MP3
    :param dest: Destination where to place the file. ie: /my-path/xyz124/waveform
        it will return: /my-path/xyz124/waveform.json, /my-path/xyz124/waveform.png
    :param fgcolor: foreground color of the png. format: rrggbbaa hexadecimal
    :param bgcolor: background color of the png.  format: rrggbbaa hexadecimal
    :param channels: string of channels, default="left right"
    :param width: width of png
    :param height: height png
    :return: return a tuple (png_file, json_file) path
    """

    if not is_valid(src):
        raise ValueError("Invalid file format")

    bgcolor = hex_color_to_rgba(bgcolor or "00000000")
    fgcolor = hex_color_to_rgba(fgcolor or "2e4562ff")

    json_file = "%s.json" % dest
    png_file = "%s.png" % dest
    _, tmp_wav = mkstemp()
    os.close(_)


    sox_cmd = "sox {src} -c 2 -t wav {tmp_wav}"\
        .format(src=src, tmp_wav=tmp_wav)
    wav2json = "wav2json {tmp_wav} --channels {channels} -n -o {json_file}"\
        .format(tmp_wav=tmp_wav, json_file=json_file, channels=channels)
    wav2png = "wav2png {tmp_wav} " \
              "--foreground-color={fgcolor} --background-color={bgcolor} " \
              "--width {width} --height {height} " \
              "-o {png_file} "\
        .format(fgcolor=fgcolor,
                bgcolor=bgcolor,
                tmp_wav=tmp_wav,
                png_file=png_file,
                width=width,
                height=height)
    del_wav = "rm {tmp_wav}".format(tmp_wav=tmp_wav)

    cmd = sox_cmd + ";" + wav2png + ";" + wav2json + ";" + del_wav
    run(cmd)

    if not os.path.isfile(png_file) or not os.path.isfile(json_file):
        for f in [png_file, json_file]:
            if os.path.isfile(f):
                os.remove(f)
        raise IOError("Failed to save png or json file: %s - %s" % (png_file, json_file))

    return png_file, json_file

def get_bpm(src):
    cmd = "sox -G {src} -t raw -r 44100 -e float -c 1 - | bpm".format(src=src)
    r = run(cmd)
    r = r.replace("\n", "")
    return float(r)

def get_info(src):
    """
    Get the MP3 file info
    :param src:
    :return:
    """
    audio = MP3(src)
    info = audio.info
    bpm = get_bpm(src)
    return {
        "duration": round(info.length, 2),
        "channels": info.channels,
        "bitrate": info.bitrate // 1000,
        "bpm": int(round(bpm)),
        "filesize": round(os.path.getsize(src) / (1024**2), 2)
    }

def trim(src, dest):
    pass

def joint_stereo(src, dest):
    pass

def fadein(src, dest):
    pass

def fadeout(src, dest):
    pass