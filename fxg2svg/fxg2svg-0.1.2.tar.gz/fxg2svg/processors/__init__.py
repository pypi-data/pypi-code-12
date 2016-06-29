from collections import defaultdict
import logging
from .default import DefaultTagProcessor
from .common import processors as common_processors
from .text import processors as text_processors
from .geometry import processors as geom_processors
from .img import processors as img_processors
from .fill import processors as fill_processors
from .stroke import processors as stroke_processors
from .mask import processors as mask_processors
from .filters import processors as filters_processors


logger = logging.getLogger(__name__)

all_processors = defaultdict(DefaultTagProcessor)
all_processors.update(common_processors)
all_processors.update(text_processors)
all_processors.update(geom_processors)
all_processors.update(img_processors)
all_processors.update(fill_processors)
all_processors.update(stroke_processors)
all_processors.update(mask_processors)
all_processors.update(filters_processors)


def tag_processor(tagname):
    def register_tag_processor(cls):
        all_processors[tagname] = cls()
        return cls
    return register_tag_processor


@tag_processor('fill')
@tag_processor('stroke')
@tag_processor('content')
@tag_processor('filters')
@tag_processor('Private')
@tag_processor('FontMap')
@tag_processor('Map')
class IgnoreTagProcessor(object):
    def on_start(self, target):
        logger.debug("IGNORING %s %s" % (target.tagname, target.attrs))

    def on_end(self, target):
        pass

    def on_data(self, target):
        pass
