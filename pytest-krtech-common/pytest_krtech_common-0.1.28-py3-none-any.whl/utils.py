# coding=utf-8
import random
import string


def randrus_str(length=10):
    valid_letters = 'АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя'
    return ''.join((random.choice(valid_letters) for i in range(length)))


def rand_str(length=10):
    return ''.join(random.sample(string.ascii_letters, length))


def rand_num(length=6):
    digits = '0123456789'
    return ''.join((random.choice(digits) for i in range(length)))
