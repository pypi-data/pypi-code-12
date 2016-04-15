import time
import requests
import _conv_table


BASE_URL = 'http://ejje.weblio.jp/content/%s'
REFERER = 'http://ejje.weblio.jp/'
with open('ok.txt', 'w') as fd:
    for (i, (typo, gold)) in enumerate(sorted(_conv_table.eng_typo.items())):
        time.sleep(0.3)
        r = requests.get(BASE_URL % typo, headers={'referer': REFERER})
        content = r.content.decode('utf8')
        if '一致する見出し語は見つかりません' in content:
            fd.write('    "%s": "%s",\n' % (typo, gold))
        if i % 100 == 0:
            print(i)
print(i)
