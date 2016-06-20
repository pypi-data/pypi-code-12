import json
from deepthought.utils.DTSettings import DTSettings

class DTSettingsAPIs(DTSettings):
    _shared_apis = {}

    @classmethod
    def initShared(cls,path):
        cls._shared_apis = json.loads(open(path).read(1073741824))
        return cls._shared_apis

    @classmethod
    def sharedSettings(cls,settings=None):
        if settings is not None:
            cls._shared_apis.update(settings)
        return cls._shared_apis
