from datetime import datetime, timedelta
from traitlets import Unicode
from ipywidgets import DOMWidget

from .traits import Date

jsmodule = "nbextensions/dateslider/index"

now = datetime.now()


class DateSlider(DOMWidget):
    _view_module = Unicode(jsmodule).tag(sync=True)
    _view_name = Unicode("DateSliderView").tag(sync=True)
    _model_module = Unicode(jsmodule).tag(sync=True)
    _model_name = Unicode("DateSliderModel").tag(sync=True)

    value = Date(now).tag(sync=True)
    start = Date(now - timedelta(days=365)).tag(sync=True)
    end = Date(now + timedelta(days=365)).tag(sync=True)
