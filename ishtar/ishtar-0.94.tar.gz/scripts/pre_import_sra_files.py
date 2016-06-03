import unicodecsv
import datetime

from django.conf import settings

from ishtar_common.data_importer import Importer


def get_year(value):
    try:
        for fmt in ['%d/%m/%Y', '%d/%m/%Y']:
            return datetime.datetime.strptime(value, fmt).year
    except:
        pass

index_list = []


def treatment(data):
    internal_ref = data[37].strip()
    creation = data[34].strip()
    reception = data[19].strip()
    yr = get_year(creation)
    if not yr:
        yr = get_year(reception)

    idx, year = None, None
    if '-' in internal_ref:
        year, y_idx = internal_ref.split('-')
        if len(year) == 4:  # 2007-XXXX
            try:
                year = int(year)
                idx = int(y_idx)
            except ValueError:
                pass
    elif '.' in internal_ref:
        year, y_idx = internal_ref.split('.')
        if len(year) == 4:  # 2011.XXXX
            try:
                year = int(year)
                idx = int(y_idx)
            except ValueError:
                pass
    if not idx:
        idx = int(internal_ref)
    if year and year != yr:
        yr = year
    assert yr  # we should absolutly have a year!

    external_id = "{}{}-{}".format(settings.ISHTAR_LOCAL_PREFIX, yr, idx)
    assert (yr, external_id) not in index_list
    index_list.append((yr, external_id))
    return yr, idx, external_id


new_datas = []
with open('plouf.csv') as csv_file:
    datas = [line for line in unicodecsv.reader(csv_file,
                                                encoding='utf-8')]
    for idx, data in enumerate(datas):
        if idx < 3:
            # headers
            data.append('annee')
            data.append('identifiant numerique')
            data.append('external_id')
            new_datas.append(data)
            continue
        try:
            year, idx, external_id = treatment(data)
            data.append(year)
            data.append(idx)
            data.append(external_id)
            new_datas.append(data)
        except Exception as e:
            print("Line {}: {}".format(idx + 1, e))

csv = Importer()._get_csv(new_datas, empty=u'')
with open('plouf2.csv', 'w') as fle:
    fle.write(csv.encode('utf-8'))
