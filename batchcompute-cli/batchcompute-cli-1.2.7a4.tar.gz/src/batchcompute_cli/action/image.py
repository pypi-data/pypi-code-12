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

    arr = [{
        'a': '%s: %s' % (blue('Id'), result.get('Id')),
        'b': '%s: %s' % (blue('Name'), result.get('Name')),
        'c': '%s: %s' % (blue('Platform'), result.get('Platform'))
    }, {
        'a': '%s: %s' % (blue('EcsImageId'), result.get('EcsImageId')),

        'b': '%s: %s' % (blue('Created'), formater.from_now(result.get('CreationTime'))),
        'c': '%s: %s' % (blue('OwnerId'), result.get('OwnerId'))
    }]
    print('%s' % bold(magenta('Image:')))
    list2table.print_table(arr, ['a', 'b', 'c'], show_no=False, show_header=False)


    print(blue('Description:'))
    print(result.get('Description'))
