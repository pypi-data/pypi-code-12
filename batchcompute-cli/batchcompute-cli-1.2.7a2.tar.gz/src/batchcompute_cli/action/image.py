from ..const import CMD
from batchcompute.utils.functions import ConfigError
from terminal import Logger, white, blue, green,magenta,bold

from ..util import config, client,formater,result_cache,list2table

log = Logger()

def all(imageId=None):
    if imageId:
        get(imageId)
    else:
        list()


def list():

    result = client.list_images()

    arr = formater.items2arr(result.get('Items'))

    result_len = len(arr)

    arr = formater.format_date_in_arr(arr, ['CreationTime'])

    result_cache.save(arr, 'Id', 'images')

    print('%s' % bold(magenta('Images:')))
    list2table.print_table(arr, ['Id', 'Name',  'EcsImageId','Platform','OwnerId', 'CreationTime'])

    arrlen = len(arr)

    cache_str = white('(cache %s %s)' % (arrlen, 'rows' if arrlen > 1 else 'row'))
    print('%s %s' % (green('Total: %s' % result_len), cache_str))

    print(white('\n  type "%s i <Id|No.>" to show image detail\n' % (CMD)))


def get(imageId):

    imageId = result_cache.get(imageId, 'images')

    print(white('exec: bcs image %s' % imageId))
    result = client.get_image(imageId)

    arr = formater.items2arr([result])
    arr = formater.format_date_in_arr(arr, ['CreationTime'])

    list2table.print_table(arr, ['Id', 'Name', 'EcsImageId', 'Platform','OwnerId', 'CreationTime'],show_no=None)
