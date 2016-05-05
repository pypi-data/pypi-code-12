from ec2ssh2.env_dict import EnvDict
from ec2ssh2.util import ConstantDict
from ec2ssh2 import exceptions

DEFAULTS = ConstantDict(
    EC2SSH2_VPC_SCOPE=None,
    EC2SSH2_TAG_FILTERS='',
    EC2SSH2_KEY_FILE_PATH=None,
    EC2SSH2_REMOTE_USER='ubuntu'
)

def parse_tag_filters(tag_str):
    tags = {}
    if tag_str:
        if ',' in tag_str:
            pieces = tag_str.split(',')
        else:
            pieces = [tag_str]
        for piece in pieces:
            try:
                key, val = piece.split('=')
            except ValueError:
                raise exceptions.InvalidInput(tag_str,
                    "EC2SSH2_TAG_FILTERS should be formatted as: 'key1=val1,key2=val2"
                )
            key = key.strip()
            val = val.strip()
            tags[key] = val
    return tags


class Config(object):
    def __init__(self):
        # doing this lazily would make InvalidInput
        # exceptions more confusing
        self.tag_filters = ConstantDict(**parse_tag_filters(
            self.env.EC2SSH2_TAG_FILTERS
        ))

    @property
    def env(self):
        if not hasattr(self, '_env'):
            self._env = EnvDict(DEFAULTS)
        return self._env

    @property
    def vpc_scope(self):
        return self.env.EC2SSH2_VPC_SCOPE

    @property
    def remote_user(self):
        return self.env.EC2SSH2_REMOTE_USER

    @property
    def key_file_path(self):
        return self.env.EC2SSH2_KEY_FILE_PATH

