import tempfile
import unittest

from . import Experiment


class TestExperiment(unittest.TestCase):

    def test_loading_nonexistent_creates_new(self):
        exp = Experiment('path_to_some_missing_file.exp')
        print(exp.filepath_or_buffer)
        self.assertTrue(exp.table.empty)

    def test_loading_invalid_creates_new(self):
        with tempfile.NamedTemporaryFile(suffix='.'+Experiment.FILE_EXT) as f:
            exp = Experiment(f.name)
            self.assertTrue(exp.table.empty)

    # def test_video_filename_is_correctly_parsed(self):
    #     video_filename = '20160329_mated_virgin_25C_1_test.avi'
    #     expected_result = {
    #         'extra': 'test',
    #         'date': '20160329',
    #         'male': 'virgin',
    #         'female': 'mated',
    #         'id': '1',
    #         'info': '25C'
    #     }
    #     with tempfile.TemporaryFile() as f:
    #         exp = Experiment(f)
    #         result = exp.parse_video_filename(video_filename)
    #     self.assertEqual(result, expected_result)

    # def test_video_filepath_parsing_fails(self):
    #     video_filepath = 'some_dir/20160329_mated_virgin_25C_1_test.avi'
    #     with tempfile.TemporaryFile() as f:
    #         exp = Experiment(f)
    #         with self.assertRaises(ValueError):
    #             exp.parse_video_filename(video_filepath)

    # def test_add_video_with_invalid_name_fails(self):
    #     with tempfile.NamedTemporaryFile(suffix='.'+Experiment.FILE_EXT) as f:
    #         exp = Experiment(f.name)
    #         with tempfile.NamedTemporaryFile(suffix='.avi') as v:
    #             exp.add_video(v.name)
    #         self.assertEqual(len(exp.table), 0)

    def test_add_video_from_filepath(self):
        video_filepath = 'some_dir/20160329_mated_virgin_25C_1_test.avi'
        with tempfile.NamedTemporaryFile(suffix='.'+Experiment.FILE_EXT) as f:
            exp = Experiment(f.name)
            exp.add_video(video_filepath)
            self.assertEqual(len(exp.table.index), 1)

    # def test_add_video_providing_fields(self):
    #     # fields = dict(date='20160329', female='CS')
    #     # with tempfile.NamedTemporaryFile(suffix='.'+Experiment.FILE_EXT) as f:
    #     #     exp = Experiment(f.name)
    #     #     exp.add_video(**fields)
    #     #     # exp.table.dropna(axis=1, inplace=True)  # drop null fields
    #     #     # populated_columns = sorted(list(exp.table.columns))
    #     #     # expected_columns = sorted(['blind_id'] + list(fields.keys()))
    #     #     # self.assertEqual(populated_columns, expected_columns)
    #     #     print(exp.table[exp.table != ''].dropna(axis=1, inplace=True))
    #     #     print(exp.table)
    #         self.fail()

    # def test_add_video_from_filename_and_overwrite_fields(self):
    #     video_filepath = '20160329_mated_virgin_25C_1_test.avi'
    #     with tempfile.NamedTemporaryFile(suffix='.'+Experiment.FILE_EXT) as f:
    #         exp = Experiment(f.name)
    #         exp.add_video(video_filepath, info=None, extra=None)
    #         exp.table.dropna(axis=1, inplace=True)  # drop null fields
    #         populated_columns = sorted(list(exp.table.columns))
    #         expected_columns = sorted(
    #             ['blind_id', 'date', 'female', 'id', 'male'])
    #         self.assertEqual(populated_columns, expected_columns)

    def test_add_multiple_videos(self):
        videos = (
            '20160329_1.avi',
            '20160329_2.avi',
            '20160329_3.avi',
            '20160329_4.avi',
            '20160329_5.avi',
            '20160329_6.avi',
            '20160329_7.avi',
            '20160329_8.avi',
        )
        with tempfile.TemporaryFile() as f:
            exp = Experiment(f)
            exp.add_videos(videos)
            self.assertEqual(len(videos), len(exp.table))

    def test_add_duplicate_videos(self):
        videos = (
            dict(date='20160329', id='1'),
            dict(date='20160329', id='2'),
            dict(date='20160329', id='3'),
            dict(date='20160329', id='4'),
            dict(date='20160329', id='1'),
            dict(date='20160329', id='2'),
            dict(date='20160329', id='5'),
            dict(date='20160329', id='6'),
        )
        with tempfile.TemporaryFile() as f:
            exp = Experiment(f)
            exp.add_videos(videos)
            self.assertEqual(len(exp.table), 6)

    def test_blind(self):
        # TODO how can I test the renaming?
        video = '20160329_1.avi'
        with tempfile.TemporaryFile() as f:
            exp = Experiment(f)
            exp.add_video(video)
            blind_name = exp.blind(video, dryrun=True)
            self.assertEqual(blind_name, 'video_001.avi')

    def test_lookup(self):
        # TODO test file lookup in table to get its index
        pass
