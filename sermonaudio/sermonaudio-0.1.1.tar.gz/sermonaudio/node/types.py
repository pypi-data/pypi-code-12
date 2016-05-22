"""Node API data structures"""
import datetime
import pytz


def isinstance_or_none(obj, type):
    return (obj is None) or isinstance(obj, type)


class Node(object):
    """The base node object, which encapsulates all node API responses"""
    def __init__(self, obj: dict):
        self.node_type = obj['nodeType']
        assert isinstance(self.node_type, str)

        self.node_display_name = obj['nodeDisplayName']
        assert isinstance(self.node_display_name, str)

        self.results = obj['results']
        assert isinstance(self.results, list)


class Source(object):
    """Broadcaster API data model"""
    def __init__(self, obj: dict):
        """Constructs a broadcaster from a dictionary returned from the SermonAudio API"""
        self.source_id = obj['sourceID']
        assert isinstance(self.source_id, str)

        self.display_name = obj['displayName']
        assert isinstance(self.display_name, str)

        self.location = obj['location']
        assert isinstance(self.location, str)

        self.latitude = obj['latitude']
        assert isinstance_or_none(self.latitude, float)

        self.longitude = obj['longitude']
        assert isinstance_or_none(self.longitude, float)

        self.image_url = obj['imageURL']
        assert isinstance(self.image_url, str)

        self.album_art_url_format = obj['albumArtURL']
        assert isinstance(self.album_art_url_format, str)

        self.minister = obj['minister']
        assert isinstance_or_none(self.minister, str)

        self.phone = obj['phone']
        assert isinstance_or_none(self.phone, str)

        self.home_page_url = obj['homePageURL']
        assert isinstance_or_none(self.home_page_url, str)

        self.bible_version = obj['bibleVersion']
        assert isinstance_or_none(self.bible_version, str)

        self.facebook_username = obj['facebookUsername']
        assert isinstance_or_none(self.facebook_username, str)

        self.twitter_username = obj['twitterUsername']
        assert isinstance_or_none(self.twitter_username, str)

        self.about_us = obj['aboutUs']
        assert isinstance_or_none(self.about_us, str)

        self.disabled = obj['disabled']
        assert isinstance(self.disabled, bool)

    def get_album_art_url(self, size: int):
        """Returns a URL for the square album art with a with and height equal to the provided size argument"""
        return self.album_art_url_format.replace('{size}', str(size))


class Speaker(object):
    """Speaker data model"""
    def __init__(self, obj: dict):
        self.display_name = obj['displayName']
        assert isinstance(self.display_name, str)

        self.bio = obj['bio']
        assert isinstance_or_none(self.bio, str)

        self.portrait_url = obj['portraitURL']
        assert isinstance(self.portrait_url, str)

        self.rounded_thumbnail_image_url = obj['roundedThumbnailImageURL']
        assert isinstance(self.rounded_thumbnail_image_url, str)

        self.album_art_url_format = obj['albumArtURL']
        assert isinstance(self.album_art_url_format, str)

    def get_album_art_url(self, size: int):
        """Returns a URL for the square album art with a with and height equal to the provided size argument"""
        return self.album_art_url_format.replace('{size}', str(size))


class Sermon(object):
    """Sermon data model"""
    def __init__(self, obj: dict):
        """Constructs a sermon from a dictionary returned from the SermonAudio API"""
        self.sermon_id = obj['sermonID']
        assert isinstance(self.sermon_id, str)

        self.source = Source(obj['source'])
        self.speaker = Speaker(obj['speaker'])

        self.full_title = obj['fullTitle']
        assert isinstance(self.full_title, str)

        self.display_title = obj['displayTitle']
        assert isinstance(self.display_title, str)

        self.subtitle = obj['subtitle']
        assert isinstance_or_none(self.subtitle, str)

        self.preach_date = datetime.datetime.strptime(obj['preachDate'], '%Y-%m-%d').date()
        assert isinstance(self.preach_date, datetime.date)

        self.language_code = obj['languageCode']
        assert isinstance(self.language_code, str)

        self.bible_text = obj['bibleText']
        assert isinstance_or_none(self.bible_text, str)

        self.more_info_text = obj['moreInfoText']
        assert isinstance_or_none(self.more_info_text, str)

        self.event_type = obj['eventType']
        assert isinstance(self.event_type, str)

        self.download_count = obj['downloadCount']
        assert isinstance(self.download_count, int)

        self.audio_bitrate = obj['audioBitrate']
        assert isinstance_or_none(self.audio_bitrate, int)

        self.video_bitrate = obj['videoBitrate']
        assert isinstance_or_none(self.video_bitrate, int)

        self.audio_file_url = obj['audioFileURL']
        assert isinstance_or_none(self.audio_file_url, str)

        self.audio_file_lo_url = obj['audioFileLOURL']
        assert isinstance_or_none(self.audio_file_lo_url, str)

        self.video_file_url = obj['videoFileURL']
        assert isinstance_or_none(self.video_file_url, str)

        self.video_file_lo_url = obj['videoFileLOURL']
        assert isinstance_or_none(self.video_file_lo_url, str)

        self.video_hls_url = obj['videoHLSURL']
        assert isinstance_or_none(self.video_hls_url, str)

        self.video_thumbnail_image_url = obj['videoThumbnailImageURL']
        assert isinstance_or_none(self.video_thumbnail_image_url, str)

        self.text_file_url = obj['textFileURL']
        assert isinstance_or_none(self.text_file_url, str)

    def __str__(self):
        return '{0:s} - {1:s}'.format(self.speaker.display_name, self.display_title)


class HLSStreamInfo(object):
    """An HLS video stream info object"""

    def __init__(self, bitrate: int, url: str):
        """Constructs an HLS stream info object"""
        self.bitrate = bitrate
        assert isinstance(self.bitrate, int)

        self.url = url
        assert isinstance(self.url, str)


class WebcastInfo(object):
    """Webcast info data model"""

    def __init__(self, obj: dict):
        """Constructs webcast info from a dictionary returned from the SermonAudio API"""
        self.display_name = obj['displayName']
        assert isinstance(self.display_name, str)

        self.source_id = obj['sourceID']
        assert isinstance(self.source_id, str)

        self.source_location = obj['sourceLocation']
        assert isinstance(self.source_location, str)

        self.start_time = datetime.datetime.fromtimestamp(obj['startTime'], tz=pytz.utc)
        assert isinstance(self.start_time, datetime.datetime)

        self.preview_image_url = obj['previewImageURL']
        assert isinstance_or_none(self.preview_image_url, str)

        self.peak_listener_count = obj['peakListenerCount']
        assert isinstance(self.peak_listener_count, int)

        self.total_tune_in_count = obj['totalTuneInCount']
        assert isinstance(self.total_tune_in_count, int)

        self.has_video = obj['hasVideo']
        assert isinstance(self.has_video, bool)

        self.audio_url = obj['audioURL']
        assert isinstance(self.audio_url, str)

        self.hls_video_streams = []
        for stream in obj['hlsVideoStreams']:
            stream_info = HLSStreamInfo(stream['bitrate'], stream['url'])
            self.hls_video_streams.append(stream_info)


class SourceNearLocation(object):
    """Model representing a source and it's distance from a search origin"""

    def __init__(self, obj: dict):
        """Constructs source near location from a dictionary returned from the SermonAudio API"""
        self.source = Source(obj['source'])
        assert isinstance(self.source, Source)

        self.meters = obj['meters']
        assert isinstance(self.meters, int)
