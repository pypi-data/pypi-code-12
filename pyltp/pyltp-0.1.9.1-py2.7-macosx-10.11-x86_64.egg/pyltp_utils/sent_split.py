#!/usr/bin/env python
# -*- coding: utf8 -*-

UNI_PUNC = [u"。", u"！", u"？", u"；", u"……"]
BI_PUNC = [u"。”", u"！”", u"？”", u"；”", u"……”", u"。’", u"！’", u"？’", u"；’", u"……?", u"？！", u"。』", u"！』", u"？』", u"；』", u"……』"]
TRI_PUNC = [u"？！”", u"。’”", u"！’”"]

def sent_split(sent):
    try:
        words = sent.decode('utf-8').strip()
    except:
        raise Exception("Input sentence's encoding should be utf-8")
    result = []
    line = ""
    i = 0
    while i < len(words):
        f = False
        if i + 2 < len(words):
            if (words[i] + words[i+1] + words[i+2]) in TRI_PUNC:
                line += words[i]; i += 1
                line += words[i]; i += 1
                line += words[i]; i += 1
                result.append(line.encode('utf-8'))
                line = ""
                f = True

        if i + 1 < len(words):
            if (words[i] + words[i+1]) in BI_PUNC:
                line += words[i]; i += 1
                line += words[i]; i += 1
                result.append(line.encode('utf-8'))
                line = ""
                f = True

        if not f and (words[i] in UNI_PUNC):
            line += words[i]; i += 1
            result.append(line.encode('utf-8'))
            line = ""
            f = True

        if not f:
            line += words[i]; i += 1

    if len(line) > 0:
        result.append(line.encode('utf-8'))

    return result

