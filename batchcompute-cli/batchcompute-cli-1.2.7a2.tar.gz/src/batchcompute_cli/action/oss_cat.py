from ..util import oss_client,config
# from terminal import white
# from ..const import CMD
from ..const import STRING
def cat(osspath):
    # str or list

    #def_oss_path = config.get_oss_path()

    arr = osspath
    if isinstance(osspath, STRING):
        arr = [osspath]

    for osspath in arr:
        # if not osspath.startswith('oss://'):
        #     osspath = def_oss_path + osspath

        #print(white('exec: %s o ls %s' % (CMD,osspath)))

        print(oss_client.get_data(osspath))


