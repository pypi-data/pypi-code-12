import thumbor.filters
from thumbor.filters import BaseFilter, filter_method


class Filter(BaseFilter):
    phase = thumbor.filters.PHASE_AFTER_LOAD

    @filter_method()
    def force_upscale(self):
        image_size = self.context.request.engine.size
        ratio = min(float(self.context.request.width) / image_size[0], float(self.context.request.height) / image_size[1])
        self.context.request.engine.resize(int(round(image_size[0] * ratio)), int(round(image_size[1] * ratio)))
