# coding=utf-8
class TplFilenameParser(object):
    def __init__(self, filename):
        self._filename = filename
        self.parser()

    def parser(self):
        #top_obj 和obj都要渲染,如info,adapter
        if self._filename.startswith("###"):
            self._type = "single_and_multi"
        #obj 需要渲染
        elif self._filename.startswith("##"):
            self._type = "multi"
        #top_obj 需要渲染
        elif self._filename.startswith("#"):
            self._type = "single"
        #文件名不需要渲染  内容要渲染
        elif self._filename.startswith("@"):
            self._type="simple"
        # 静态文件 不渲染 直接复制
        else:
            self._type = "static"
        self._filename_to_render = self._filename.replace("#", "")

    def _get_is_static(self):
        return self._type == "static"

    def _get_is_simple(self):
        return self._type == "simple"

    def _get_is_single(self):
        return self._type == "single"

    def _get_is_multi(self):
        return self._type == "multi"

    def _get_is_single_and_multi(self):
        return self._type == "single_and_multi"

    def _get_filename_to_render(self):
        return self._filename_to_render

    is_simple = property(fget=_get_is_simple)  # 如 json_encoder.py
    is_static = property(fget=_get_is_static)  # 如 __init__.py
    is_single = property(fget=_get_is_single)  # 如 goods_bll.py
    is_multi = property(fget=_get_is_multi)  # 如 goods_info.py
    is_single_and_multi = property(fget=_get_is_single_and_multi)
    filename_to_render = property(fget=_get_filename_to_render)
