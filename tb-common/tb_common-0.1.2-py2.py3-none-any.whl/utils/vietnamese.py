# encoding=utf-8
import re
import unicodedata

from six import text_type

__author__ = 'hiepsimu'


trantab = {u'A\u0300': u'\xc0',
 u'A\u0301': u'\xc1',
 u'A\u0303': u'\xc3',
 u'A\u0309': u'\u1ea2',
 u'A\u0323': u'\u1ea0',
 u'E\u0300': u'\xc8',
 u'E\u0301': u'\xc9',
 u'E\u0303': u'\u1ebc',
 u'E\u0309': u'\u1eba',
 u'E\u0323': u'\u1eb8',
 u'I\u0300': u'\xcc',
 u'I\u0301': u'\xcd',
 u'I\u0303': u'\u0128',
 u'I\u0309': u'\u1ec8',
 u'I\u0323': u'\u1eca',
 u'O\u0300': u'\xd2',
 u'O\u0301': u'\xd3',
 u'O\u0303': u'\xd5',
 u'O\u0309': u'\u1ece',
 u'O\u0323': u'\u1ecc',
 u'U\u0300': u'\xd9',
 u'U\u0301': u'\xda',
 u'U\u0303': u'\u0168',
 u'U\u0309': u'\u1ee6',
 u'U\u0323': u'\u1ee4',
 u'Y\u0300': u'\u1ef2',
 u'Y\u0301': u'\xdd',
 u'Y\u0303': u'\u1ef8',
 u'Y\u0309': u'\u1ef6',
 u'Y\u0323': u'\u1ef4',
 u'a\u0300': u'\xe0',
 u'a\u0301': u'\xe1',
 u'a\u0303': u'\xe3',
 u'a\u0309': u'\u1ea3',
 u'a\u0323': u'\u1ea1',
 u'e\u0300': u'\xe8',
 u'e\u0301': u'\xe9',
 u'e\u0303': u'\u1ebd',
 u'e\u0309': u'\u1ebb',
 u'e\u0323': u'\u1eb9',
 u'i\u0300': u'\xec',
 u'i\u0301': u'\xed',
 u'i\u0303': u'\u0129',
 u'i\u0309': u'\u1ec9',
 u'i\u0323': u'\u1ecb',
 u'o\u0300': u'\xf2',
 u'o\u0301': u'\xf3',
 u'o\u0303': u'\xf5',
 u'o\u0309': u'\u1ecf',
 u'o\u0323': u'\u1ecd',
 u'u\u0300': u'\xf9',
 u'u\u0301': u'\xfa',
 u'u\u0303': u'\u0169',
 u'u\u0309': u'\u1ee7',
 u'u\u0323': u'\u1ee5',
 u'y\u0300': u'\u1ef3',
 u'y\u0301': u'\xfd',
 u'y\u0303': u'\u1ef9',
 u'y\u0309': u'\u1ef7',
 u'y\u0323': u'\u1ef5',
 u'\xc2\u0300': u'\u1ea6',
 u'\xc2\u0301': u'\u1ea4',
 u'\xc2\u0303': u'\u1eaa',
 u'\xc2\u0309': u'\u1ea8',
 u'\xc2\u0323': u'\u1eac',
 u'\xca\u0300': u'\u1ec0',
 u'\xca\u0301': u'\u1ebe',
 u'\xca\u0303': u'\u1ec4',
 u'\xca\u0309': u'\u1ec2',
 u'\xca\u0323': u'\u1ec6',
 u'\xd4\u0300': u'\u1ed2',
 u'\xd4\u0301': u'\u1ed0',
 u'\xd4\u0303': u'\u1ed6',
 u'\xd4\u0309': u'\u1ed4',
 u'\xd4\u0323': u'\u1ed8',
 u'\xe2\u0300': u'\u1ea7',
 u'\xe2\u0301': u'\u1ea5',
 u'\xe2\u0303': u'\u1eab',
 u'\xe2\u0309': u'\u1ea9',
 u'\xe2\u0323': u'\u1ead',
 u'\xea\u0300': u'\u1ec1',
 u'\xea\u0301': u'\u1ebf',
 u'\xea\u0303': u'\u1ec5',
 u'\xea\u0309': u'\u1ec3',
 u'\xea\u0323': u'\u1ec7',
 u'\xf4\u0300': u'\u1ed3',
 u'\xf4\u0301': u'\u1ed1',
 u'\xf4\u0303': u'\u1ed7',
 u'\xf4\u0309': u'\u1ed5',
 u'\xf4\u0323': u'\u1ed9',
 u'\u0102\u0300': u'\u1eb0',
 u'\u0102\u0301': u'\u1eae',
 u'\u0102\u0303': u'\u1eb4',
 u'\u0102\u0309': u'\u1eb2',
 u'\u0102\u0323': u'\u1eb6',
 u'\u0103\u0300': u'\u1eb1',
 u'\u0103\u0301': u'\u1eaf',
 u'\u0103\u0303': u'\u1eb5',
 u'\u0103\u0309': u'\u1eb3',
 u'\u0103\u0323': u'\u1eb7',
 u'\u01a0\u0300': u'\u1edc',
 u'\u01a0\u0301': u'\u1eda',
 u'\u01a0\u0303': u'\u1ee0',
 u'\u01a0\u0309': u'\u1ede',
 u'\u01a0\u0323': u'\u1ee2',
 u'\u01a1\u0300': u'\u1edd',
 u'\u01a1\u0301': u'\u1edb',
 u'\u01a1\u0303': u'\u1ee1',
 u'\u01a1\u0309': u'\u1edf',
 u'\u01a1\u0323': u'\u1ee3',
 u'\u01af\u0300': u'\u1eea',
 u'\u01af\u0301': u'\u1ee8',
 u'\u01af\u0303': u'\u1eee',
 u'\u01af\u0309': u'\u1eec',
 u'\u01af\u0323': u'\u1ef0',
 u'\u01b0\u0300': u'\u1eeb',
 u'\u01b0\u0301': u'\u1ee9',
 u'\u01b0\u0303': u'\u1eef',
 u'\u01b0\u0309': u'\u1eed',
 u'\u01b0\u0323': u'\u1ef1'}


# Source: https://gist.github.com/thuandt/3421905
def no_accent_vietnamese(s):
    # s = s.decode('utf-8')
    s = re.sub(u'Đ', 'D', s)
    s = re.sub(u'đ', 'd', s)
    return unicodedata.normalize('NFKD', text_type(s)).encode('ASCII', 'ignore').decode('utf-8')


def generate_text_link(text):
    tmp = no_accent_vietnamese(text)
    return re.sub('[\W_]+', '-', tmp)


def to_dungsan(text):
    for k in trantab:
        text = text.replace(k, trantab[k])

    return text