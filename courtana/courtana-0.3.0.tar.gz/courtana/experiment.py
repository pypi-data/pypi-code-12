import logging
import os
import pandas as pd
import random
import re

from .video import FileName


log = logging.getLogger(__name__)


class Experiment(object):

    FILE_EXT = 'exp'

    # TOFIX
    # PATH_VIDEOS = ''
    # PATH_TRACKDATA = ''

    def __init__(self, filepath_or_buffer):
        # FIXME what to do when loading an experiment while another wans't save
        self.filepath_or_buffer = filepath_or_buffer
        self.table = None
        try:
            log.info("Loading experiment '%s'" % self.filepath_or_buffer)
            self.table = pd.read_csv(
                filepath_or_buffer=self.filepath_or_buffer,
                index_col=0,
                dtype=object,
                na_values=[],
                keep_default_na=False,
            )
        except IOError as e:
            log.warning("Resolving IOError: %s" % e)
            self._init_empty_experiment()
        except ValueError as e:
            log.warning("Resolving ValueError: %s" % e)
            self._init_empty_experiment()

    def __repr__(self):
        return self.table.__repr__()

    def _add_video(self, filename, blind_id):
        """Add a video using a FileName object.
        """
        video_info = filename.fields()
        video_info.update({'blind_id': str(blind_id).zfill(3)})

        log.info("Adding video '%s'" % video_info)
        new_video = pd.Series(video_info, dtype=str)
        self.table = self.table.append(new_video, ignore_index=True)

    #     """Add a video to the table assuming it is valid.
    #     `parsed_video` is a dict with the fields obtained using the parser
    #     Here, the video is assigned a `blind_id` value like '024'.
    #     Returns False if it fails to add the video, True otherwise.
    #     """
    #     if not (0 < blind_id < 1000):
    #         log.error("Invalid blind_id. Must be in the interval [1, 999]")
    #         return False
    #     # FIXME This loop can become a pain in the a** if the number
    #     # of videos is large. For now, expecting 200 maximum...
    #     while blind_id in self.table.blind_id.values:
    #         log.debug("Randomizing blind id")
    #         blind_id = random.randint(1, len(self.table)+1)
    #     parsed_video.update({'blind_id': str(blind_id).zfill(3)})
    #     log.info("Adding video '%s'" % parsed_video)
    #     new_video = pd.Series(parsed_video, dtype=str)
    #     self.table = self.table.append(new_video, ignore_index=True)

    def _check_video_can_be_inserted(self, filepath, **fields):
        if filepath is None:
            default_fields = {
                k: ''
                for k in self.VIDEO_FILENAME_PATTERN.groupindex.keys()
                if k != 'ext'
            }
            default_fields.update(fields)
            parsed_video = default_fields
        else:
            filename = os.path.basename(filepath)
            try:
                parsed_video = self.parse_video_filename(filename)
            except ValueError as e:
                log.error(e)
                log.info("Ignoring file '%s" % filename)
                return False
            parsed_video.update(fields)

        if self.table.empty or self._lookup(parsed_video) is None:
            return parsed_video
        else:
            log.warning("Ignoring duplicated entry: %s" % parsed_video)
            return False

    def _init_empty_experiment(self):
        log.info("Creating new experiment '%s'" % self.filepath_or_buffer)
        self.table = pd.DataFrame(columns=['blind_id'])

    def _lookup(self, fields):
        """Check whether a parsed video is already present in the table.
        If it does, return its index value.
        """
        query_str = gen_query_string(fields)
        try:
            index = get_index_from_query(self.table, query_str)
            log.debug("Video exists with index %d" % index)
        except ValueError as e:
            log.error(e)
            index = None
        return index

    def save(self):
        log.info("Saving experiment '%s'" % self.filepath_or_buffer)
        self.table.to_csv(self.filepath_or_buffer)

    def add_video(self, filepath, blind_id=1):
        """Add a video to the Experiment table via a `FileName` object.

        This method does not care if the corresponding file exists.

        You can also provide a `blind_id` value to use to blind the data.
        By default, because only one entry is added at a time, the blind
        identifier will be an integer, incrementing as more entries are
        added.

        See the method `add_videos` to add a bunch of videos and shuffle
        the blind values.
        """

        if not (0 < blind_id < 1000):
            log.error("Invalid blind_id. Must be in the interval [1, 999]")
            return False

        # FIXME This loop can become a pain in the a** if the number
        # of videos is large. For now, expecting 200 maximum...
        while blind_id in self.table.blind_id.values:
            log.debug("Randomizing blind id")
            blind_id = random.randint(1, len(self.table)+1)

        self._add_video(FileName(filepath), blind_id)

    def find_videos(directory, extension='.avi'):
        # TODO should courtana care about this? Not today!
        raise NotImplemented

    def add_videos(self, list_of_videos):
        """Adds a list of videos.

        Using this method to add a group of videos allows for generating
        better blind identifiers.
        """
        # Uses `add_video` behind, so the list provided can be a list of
        # filenames or a list of fields dictionaries. Each item of this
        # list should therefore be a valid input for `add_video`.

        # Sanitize the input
        list_of_videos = [FileName(video) for video in list_of_videos]
        list_of_videos = [
            video
            for video in list_of_videos
            if self.table.empty or self._lookup(video.fields()) is None
        ]
        n = len(list_of_videos)
        blind_ids = list(range(len(self.table) + 1, len(self.table) + n + 1))
        random.shuffle(blind_ids)
        for video, blind_id in zip(list_of_videos, blind_ids):
            if self.table.empty or self._lookup(video.fields()) is None:
                self._add_video(video, blind_id)
        log.info("Successfully added %d videos" % n)

    def add_files(self, path, col_name, match_cols, ext='.csv', pattern=None):
        """Add files to the table.
        Walks down the path given in search for all files with extension
        ext. Adds them under the column named col_name and assigns its
        row using the pattern and the match_cols arguments.
        """
        # TOFIX not touched when the refactoring, may be broken
        if pattern is None:
            pattern = self.VIDEO_FILENAME_PATTERN
        # Does the col_name specified exists?
        if col_name not in self.table.columns:
            self.table[col_name] = ''
        print("Looking for tracker results in", path)
        for root, _, files in os.walk(path):
            for f in files:
                if f.endswith(ext):
                    filepath = os.path.abspath(os.path.join(root, f))
                    filename = os.path.basename(filepath)

                    # Is the file already in the table?
                    if filepath not in self.table.loc[:, col_name].values:
                        # Add a new entry
                        print("Adding", filename)
                        match = re.fullmatch(pattern, filename)
                        if match:
                            matches = match.groupdict()
                            query_str = gen_query_string(matches, match_cols)
                            index = get_index_from_query(self.table, query_str)
                            self.table.loc[index, col_name] = filepath
                        else:
                            raise Warning("Match failed!")
                    else:
                        print("Already exists:", filepath)

    def blind(self, filepath, dryrun=False):
        """Renames the input file according to its blind ID.
        IF `dryrun` is True, the filesystem is not touched.
        Returns the resulting blinded file name.
        """
        log.debug("Blinding video %s" % filepath)
        path, filename = os.path.split(filepath)
        _, ext = os.path.splitext(filename)

        index = self._lookup(FileName(filename).fields())
        if index is not None:
            blind_id = self.table.loc[index, 'blind_id']
            blind_filename = 'video_%s%s' % (blind_id, ext)
            if dryrun is True:
                log.info("(DRYRUN) Renaming file '%s to '%s'" % (filename, blind_filename))
            else:
                log.info("Renaming file '%s to '%s'" % (filename, blind_filename))
                os.rename(filepath, os.path.join(path, blind_filename))
        else:
            log.error("Video not found '%s'" % filename)
            raise FileNotFoundError
        return blind_filename


def gen_query_string(d, keys=None):
    """Returns a query string.
    d = {'a': 'hello', 'b': 'yes'}
    keys = ['a']
    Returns: "a == 'hello'"
    If no keys are specified, use all that are not None.
    """
    keys = [k for k, v in d.items() if v is not None] if keys is None else keys
    last_key = keys[-1]
    query_str = ""
    for key in keys:
        query_str += "{0} == '{1}'".format(key, d[key])
        if key != last_key:
            query_str += " and "
    return query_str


def get_index_from_query(df, query_str):
    """
    df: DataFrame
    s: query string
    returns int: index
    """

    df = df.copy()  # to make sure we don't screw up the original df

    # Query falls back to the index name if no column exists but in case
    # we need to cast the index value to str, we reset it here anyway
    index_name = df.index.name or 'index'  # name is None if not set previously
    index_dtype = df.index.dtype
    df.reset_index(inplace=True)
    df[index_name] = df[index_name].astype(str)

    df.query(query_str, inplace=True)

    # Restore the index
    df[index_name] = df[index_name].astype(index_dtype)
    df.set_index(index_name, inplace=True)

    if len(df) == 1:
        return df.index.values[0]
    else:
        log.error("Query: %s" % query_str)
        raise ValueError("Query was not enough to select only one row")
