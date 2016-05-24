#!/usr/bin/env python
# encoding: utf-8

from ycyc.base.txtutils import decode, encode


class Buddha(object):
    BuddhasWord = [
        u'冥', u'想', u'怯', u'怛', u'竟', u'訶', u'怯', u'咒', u'耶', u'那',
        u'波', u'栗', u'不', u'集', u'漫', u'奢', u'室', u'罰', u'哆', u'朋',
        u'想', u'逝', u'侄', u'離', u'佛', u'哆', u'死', u'智', u'輸', u'蘇',
        u'槃', u'梵', u'諳', u'利', u'罰', u'哆', u'瑟', u'咒', u'度', u'羯',
        u'諦', u'度', u'呐', u'諳', u'醯', u'悉', u'哆', u'僧', u'以', u'缽',
        u'諸', u'薩', u'菩', u'殿', u'冥', u'者', u'世', u'喝', u'離', u'冥',
        u'哆', u'皤', u'離', u'豆', u'一', u'集', u'恐', u'智', u'所', u'有',
        u'遠', u'菩', u'梵', u'奢', u'怯', u'舍', u'冥', u'波', u'呐', u'跋',
        u'梵', u'哆', u'侄', u'除', u'是', u'娑', u'呐', u'奢', u'哆', u'梵',
        u'怖', u'迦', u'僧', u'夜', u'地', u'能', u'離', u'梵', u'槃', u'提',
        u'諳', u'奢', u'羯', u'除', u'缽', u'爍', u'不', u'沙', u'諦', u'羅',
        u'皤', u'缽', u'佛', u'波', u'諳', u'離', u'缽', u'跋', u'離', u'哆',
        u'故', u'娑', u'滅', u'怯', u'皤', u'諸', u'藐', u'僧', u'侄', u'俱',
        u'瑟', u'缽', u'大', u'怖', u'皤', u'真', u'皤', u'楞', u'朋', u'彌',
        u'孕', u'耶', u'朋', u'南', u'栗', u'阿', u'穆', u'怯', u'都', u'哆',
        u'離', u'哆', u'罰', u'有', u'罰', u'穆', u'夢', u'諸', u'苦', u'尼',
        u'佛', u'菩', u'娑', u'缽', u'哆', u'盧', u'缽', u'道', u'盧', u'怯',
        u'哆', u'冥', u'哆', u'盡', u'吉', u'阿', u'醯', u'隸', u'冥', u'諳',
        u'利', u'梵', u'南', u'哆', u'顛', u'道', u'陀', u'夷', u'罰', u'吉',
        u'寫', u'曰', u'曳', u'悉', u'那', u'皤', u'奢', u'耶', u'以', u'俱',
        u'哆', u'佛', u'南', u'夜', u'數', u'侄', u'藝', u'薩', u'伽', u'怯',
        u'侄', u'南', u'佛', u'吉', u'那', u'三', u'爍', u'梵', u'上', u'等',
        u'呐', u'冥', u'哆', u'楞', u'俱', u'罰', u'依', u'怯', u'羯', u'栗',
        u'侄', u'羅', u'婆', u'道', u'呐', u'蒙', u'僧', u'哆', u'孕', u'謹',
        u'諸', u'寫', u'般', u'俱', u'迦', u'想', u'諳', u'醯', u'阿', u'梵',
        u'哆', u'缽', u'智', u'故', u'俱',
    ]

    @classmethod
    def say(cls, sentence, encoding="utf-8"):
        real_sentence = encode(sentence, encoding)
        return u"".join(
            cls.BuddhasWord[ord(i)]
            for i in real_sentence
        )

    @classmethod
    def think(cls, sentence, encoding="utf-8"):
        real_sentence = decode(sentence, encoding)
        means = "".join(
            chr(cls.BuddhasWord.index(i))
            for i in real_sentence
        )
        return means
