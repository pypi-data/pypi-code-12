

from gi.repository import Gst, GLib


class SimpleSoundPlayer:

    def __init__(self):
        self._pipeline = None
        return

    def play(self, filename=None, data=None):
        if self.is_playing():
            self.stop()

        if filename:

            pipeline = Gst.Pipeline()
            self._pipeline = pipeline

            self._pipeline.set_name("audio-player")
            source = Gst.ElementFactory.make("filesrc", "file-source")
            demuxer = Gst.ElementFactory.make("oggdemux", "ogg-demuxer")
            decoder = Gst.ElementFactory.make("vorbisdec", "vorbis-decoder")
            conv = Gst.ElementFactory.make("audioconvert", "converter")
            sink = Gst.ElementFactory.make("alsasink", "audio-output")

            source.set_property('location', filename)

            demuxer.connect('pad-added', self._on_pad_added, decoder)

            pipeline.add(source)
            pipeline.add(demuxer)
            pipeline.add(decoder)
            pipeline.add(conv)
            pipeline.add(sink)

            source.link(demuxer)
            decoder.link(conv)
            conv.link(sink)

            self._pipeline.set_state(Gst.State.PLAYING)

        elif data:
            pipeline = Gst.Pipeline()
            self._pipeline = pipeline

            self._pipeline.set_name("audio-player")
            source = Gst.ElementFactory.make("appsrc", "data-source")
            demuxer = Gst.ElementFactory.make("oggdemux", "ogg-demuxer")
            decoder = Gst.ElementFactory.make("vorbisdec", "vorbis-decoder")
            conv = Gst.ElementFactory.make("audioconvert", "converter")
            sink = Gst.ElementFactory.make("alsasink", "audio-output")

            source.set_property('location', filename)

            demuxer.connect('pad-added', self._on_pad_added, decoder)

            pipeline.add(source)
            pipeline.add(demuxer)
            pipeline.add(decoder)
            pipeline.add(conv)
            pipeline.add(sink)

            source.link(demuxer)
            decoder.link(conv)
            conv.link(sink)

            self._pipeline.set_state(Gst.State.PLAYING)

        else:
            raise Exception("filename or data must be supplied")

        return

    def stop(self):
        self._pipeline.set_state(Gst.State.NULL)
        return

    def is_playing(self):
        return (
            self._pipeline
            and
            self._pipeline.get_state(0)[1] == Gst.State.PLAYING
            )

    def _on_pad_added(self, element, pad, decoder):
        sinkpad = decoder.get_static_pad('sink')
        pad.link(sinkpad)
        return


class SimpleSoundFileIdentifier:

    def __init__(self):
        return

    def identify(self, filename):
        pipeline = Gst.Pipeline()
        self._pipeline = pipeline
        pipeline.set_name("audio-player")
        source = Gst.ElementFactory.make("filesrc", "file-source")
        demuxer = Gst.ElementFactory.make("oggdemux", "ogg-demuxer")
        decoder = Gst.ElementFactory.make("vorbisdec", "vorbis-decoder")
        conv = Gst.ElementFactory.make("audioconvert", "converter")
        sink = Gst.ElementFactory.make("alsasink", "audio-output")

        source.set_property(
            'location',
            filename
            )

        demuxer.connect('pad-added', self._on_pad_added, decoder)

        pipeline.add(source)
        pipeline.add(demuxer)
        pipeline.add(decoder)
        pipeline.add(conv)
        pipeline.add(sink)

        source.link(demuxer)
        decoder.link(conv)
        conv.link(sink)
        return


def play(filename):
    ret = SimpleSoundFilePlayer()
    ret.play(filename)
    return ret


def identify(filename):
    ret = SimpleSoundFileIdentifier()
    ret = ret.identify(filename)
    return ret
