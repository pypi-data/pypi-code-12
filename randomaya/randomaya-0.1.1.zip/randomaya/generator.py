import xml.etree.ElementTree as ET, random

#   This package is created by Ansar Bedharudeen and its created with the best of my knowledge.
#   Should you find any errors please report it to 1ns1rb@gmail.com
#   All quran text and translations are obtained from Tanzil.net
#   You may search for new translations or any updates  at http://tanzil.net
#   Any new translations or updated data should be copied to 'data' folder

def getRandomAya(lang = 'en.sahih'):
    root = ET.parse('./data/'+lang+'.xml').getroot()
    rand_sura = random.randint(1,114)
    p = "sura[@index='{}']/aya".format(str(rand_sura))
    rand_aya =random.randint(1,len(root.findall(p)))
    path = "sura[@index='{}']/aya[@index='{}']".format(str(rand_sura), str(rand_aya))
    return root.find(path).get('text') + " - Surah:{} Aya:{}".format(rand_sura, rand_aya)

def getMultiRandomAya(lang = ['en.sahih']):
    result ={}
    rand_sura = random.randint(1,114)
    p = "sura[@index='{}']/aya".format(str(rand_sura))
    flag = True
    result['surah'] = str(rand_sura)
    for l in lang:
        root = ET.parse('./data/'+l+'.xml').getroot()
        while(flag):
            rand_aya =random.randint(1,len(root.findall(p)))
            result['aya'] = str(rand_aya)
            flag=False
        name = "sura[@index='{}']".format(str(rand_sura))
        path ="sura[@index='{}']/aya[@index='{}']".format(str(rand_sura), str(rand_aya))
        result[l+' aya'] = root.find(path).get('text')
        result[l+ 'name'] = root.find(name).get('name')
    return result



