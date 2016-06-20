
# -*- coding:utf-8 -*-

from ..util import it,client,util
from terminal import green
from ..const import IMG_ID,INS_TYPE
import json


def create_image(imageName, ecsImageId, platform='Linux', description=''):

    desc = {}
    desc['Name'] = imageName
    desc['EcsImageId'] = ecsImageId
    desc['Platform'] = platform
    desc['Description'] = description

    print(desc)

    if not ecsImageId.startswith('m-'):
        raise Exception('Invalid ecsImageId')

    result = client.create_image(desc)

    if result.StatusCode==201:
        print(green('Image create: %s' % result.Id))


def trans_platform(platform='Linux'):
    platform = platform.lower()
    if platform=='linux':
        return 'Linux'
    elif platform=='windows':
        return 'Windows'
    else:
        raise Exception('platform should be "linux" or "windows"')
