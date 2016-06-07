from os import path
from cv2 import imread, floodFill
from PIL.ImageColor import getrgb

def japanmap(dic):
    pref = {s:i for i, s in enumerate(('北海 青森 岩手 宮城 秋田 山形 '
        '福島 茨城 栃木 群馬 埼玉 千葉 東京 神奈川 新潟 富山 石川 福井 '
        '山梨 長野 岐阜 静岡 愛知 三重 滋賀 京 大阪 兵庫 奈良 和歌山 '
        '鳥取 島根 岡山 広島 山口 徳島 香川 愛媛 高知 福岡 佐賀 長崎 '
        '熊本 大分 宮崎 鹿児島 沖縄').split())}
    pos = [eval(s) for s in ('15,15 52,6 57,9 54,19 52,9 52,19 52,24 '
        '52,34 49,31 47,31 47,34 52,36 47,36 47,37 47,24 37,31 34,32 '
        '32,34 44,36 42,34 37,34 42,39 37,39 34,43 32,39 29,39 29,41 '
        '27,39 31,44 29,44 19,38 12,42 22,39 17,41 11,44 22,46 22,44 '
        '17,46 19,48 7,48 3,50 2,52 7,54 8,49 9,54 5,59 54,56').split()]
    p = imread(path.join(path.dirname(__file__),'japan.png'))
    for k, v in dic.items():
        i = k if isinstance(k, int) else pref.get(k.rstrip('都道府県'), -1)
        if 0 <= i < 47:
            c = v if isinstance(v, tuple) else getrgb(v)
            floodFill(p, None, (pos[i][0]*10, pos[i][1]*10), c)
    return p
