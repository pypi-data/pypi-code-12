# -*- coding: utf-8 -*-

features_mystem_2_syntagrus = {
    'A': 'A',
    'ADV': 'ADV',
    'ANUM': 'A',
    'APRO': 'A',
    'COM': 'COM',
    'CONJ': 'CONJ',
    'INTJ': 'INTJ',
    'NUM': 'NUM',
    'PART': 'PART',
    'PR': 'PR',
    'S': 'S',
    'SPRO': 'S',
    'ADVPRO': 'ADV',
    'V': 'V',

    'ЕД': 'ЕД',
    'МН': 'МН',

    'ЖЕН': 'ЖЕН',
    'МУЖ': 'МУЖ',
    'СРЕД': 'СРЕД',

    'ИМ': 'ИМ',
    'РОД': 'РОД',
    'ДАТ': 'ДАТ',
    'ВИН': 'ВИН',
    'ТВОР': 'ТВОР',
    'ПР': 'ПР',
    'ПАРТ': 'ПАРТ',
    'МЕСТН': 'МЕСТН',
    'ЗВАТ': 'ЗВ',

    '1-Л': '1-Л',
    '2-Л': '2-Л',
    '3-Л': '3-Л',

    'НЕСОВ': 'НЕСОВ',
    'СОВ': 'СОВ',

    'ОД': 'ОД',
    'НЕОД': 'НЕОД',

    'ДЕЕПР': 'ДЕЕПР',
    'ИНФ': 'ИНФ',
    'ПРИЧ': 'ПРИЧ',

    'ПРОШ': 'ПРОШ',
    'НЕПРОШ': 'НЕПРОШ',
    'НАСТ': 'НАСТ',

    'ИЗЪЯВ': 'ИЗЪЯВ',
    'ПОВ': 'ПОВ',
    'КР': 'КР',
    'ПОЛН': '',
    'ПРИТЯЖ': '',

    'СТРАД': 'СТРАД',
    'ДЕЙСТВ': '',

    'СРАВ': 'СРАВ',
    'ПРЕВ': 'ПРЕВ',

    'ПЕ': '',

    'НП': '',

}

feat_syntagrus_ru_en = {
    'S': 'S',
    'A': 'A',
    'V': 'VERB',
    'ADV': 'ADV',
    'NUM': 'NUM',
    'PR': 'PR',
    'COM': 'COM',
    'CONJ': 'CONJ',
    'PART': 'PART',
    'P': 'P',
    'INTJ': 'INTJ',
    'NID': 'NID',

    'ЕД': 'sing',
    'МН': 'plur',

    'ЖЕН': 'femn',
    'МУЖ': 'masc',
    'СРЕД': 'neut',

    'ИМ': 'nomn',
    'РОД': 'gent',
    'ДАТ': 'datv',
    'ВИН': 'accs',
    'ТВОР': 'ablt',
    'ПР': 'loct',
    'ЗВ': 'voct',
    'ПАРТ': 'gen2',
    'МЕСТН': 'loc2',

    'ОД': 'anim',
    'НЕОД': 'inan',
    'ИНФ': 'inf',
    'ПРИЧ': 'adjp',
    'ДЕЕПР': 'advp',
    'ПРОШ': 'pst',
    'НЕПРОШ': 'npst',
    'НАСТ': 'prs',

    '1-Л': 'p1',
    '2-Л': 'p2',
    '3-Л': 'p3',

    'ИЗЪЯВ': 'real',
    'ПОВ': 'imp',
    'КР': 'shrt',

    'НЕСОВ': 'imperf',
    'СОВ': 'perf',
    'СТРАД': 'pass',

    'СЛ': '',
    'СМЯГ': 'comp',
    'СРАВ': 'comp',
    'ПРЕВ': 'supl',
}


class MorphyFormatConverter:
    def __init__(self):
        pass

    @classmethod
    def mystem_2_syntagrus_en(cls, gr):
        gr = [features_mystem_2_syntagrus[g.encode('utf-8')] for g in gr if
              g.encode('utf-8') in features_mystem_2_syntagrus and len(
                  features_mystem_2_syntagrus[g.encode('utf-8')]) > 0]
        return [feat_syntagrus_ru_en[g] for g in gr if g in feat_syntagrus_ru_en]

    @classmethod
    def syntagrus_2_syntagrus_en(cls, gr):
        return [feat_syntagrus_ru_en[g] for g in gr if g in feat_syntagrus_ru_en]

    @classmethod
    def parse_syntagrus_word(cls, word):
        attr = word.attrib
        lemma = attr['LEMMA'].lower() if 'LEMMA' in attr else ''
        link = attr['LINK'] if 'LINK' in attr else None
        features = attr['FEAT'].split(' ') if 'FEAT' in attr else ['UNK']
        for i in range(0, len(features)):
            if features[i].encode('utf-8') in feat_syntagrus_ru_en:
                features[i] = feat_syntagrus_ru_en[features[i].encode('utf-8')]
        dom = int(attr['DOM']) if attr['DOM'] != '_root' else 0
        pos = features[0]
        feat = set(features[1:])
        return [
            unicode(word.text).lower(),
            '_',
            unicode(pos) if pos.strip() else '_',
            unicode(pos) if pos.strip() else '_',
            unicode('|'.join(sorted(feat))) if len(''.join(feat).strip())>0 else '_',
            unicode(str(dom)),
            unicode(link) if dom !=0 else 'ROOT',
            '_',
            '_'
        ]

    @classmethod
    def parse_syntagrus_sentences(cls, root):
        s = []
        for sentence in root.iter('S'):
            words = []
            for i, word in enumerate(sentence.iter('W')):
                parsed = cls.parse_word(word)
                parsed.insert(0, str(i+1))
                words.append('\t'.join(parsed))
            s.append(words)
        return s

#for k in features_mystem_2_syntagrus.keys():
#     print "'"+k+"': '"+ (feat_syntagrus_ru_en[features_mystem_2_syntagrus[k]] if len(features_mystem_2_syntagrus[k])>0 else "") +"',"