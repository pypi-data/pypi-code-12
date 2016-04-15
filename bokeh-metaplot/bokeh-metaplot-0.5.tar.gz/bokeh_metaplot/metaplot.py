from bokeh.core.properties import Dict, String, List
from bokeh.models import Plot
from bokeh.plotting import Figure
from bokeh.charts import Chart
from bokeh.core.properties import Any, Tuple, Dict, List, Enum, Bool
from multipledispatch import dispatch

__namespace__ = dict()

def set_default(dic, key, value):
    if key not in dic:
        dic[key] = value

class MetaPlot(Plot):
    """
    @variables stores custom variable, which should be a tuple with the first argument as it's visible modifier, and the second argument as it's value.
    @category is this plot's category.
    """
    __implementation__ = """
    Plots = require "models/plots/plot"
    class MetaPlot extends Plots.Model
        type: "MetaPlot"
    module.exports =
        Model: MetaPlot
    """
    variables = Dict(String, Tuple(Bool, Any))
    category = List(String)

    @staticmethod
    def __pre_process_args__(kwargs):
        variables = kwargs.pop('variables', dict())
        category = kwargs.pop('category', [])
        return variables, category

    def __post_process__(self):
        self.name = self.name or ''
        self.title = self.title or ''
        self.webgl = True
        self.toolbar_location = None
        self.responsive = True
        self.title_standoff = 0
        self.title_text_alpha = 0
        self.title_text_font_size = '1px'
        self.min_border_left = 0
        self.min_border_right = 0
        self.min_border_bottom = 0
        self.min_border_top = 0

    @dispatch(namespace=__namespace__)
    def __init__(self, *args, **kwargs):
        variables, category = MetaPlot.__pre_process_args__(kwargs)
        super().__init__(*args, **kwargs)
        self.variables, self.category = variables, category
        self.__post_process__()

class MetaFigure(MetaPlot, Figure):
    __implementation__ = """
    Plots = require "models/plots/plot"
    class MetaFigure extends Plots.Model
        type: "MetaFigure"
    module.exports =
        Model: MetaFigure
    """

    def __post_process__(self):
        super().__post_process__()
        self.y_range.range_padding = 0
        self.x_range.range_padding = 0

class MetaChart(MetaPlot, Chart):
    __implementation__ = """
    Plots = require "models/plots/plot"
    class MetaChart extends Plots.Model
        type: "MetaChart"
    module.exports =
        Model: MetaChart
    """

@dispatch(Plot)
def metaize(plot, **kwargs):
    plot.__class__ = MetaPlot
    plot.__post_process__()
    for key, value in kwargs.items():
        setattr(plot, key, value)

@dispatch(Figure)
def metaize(figure, **kwargs):
    figure.__class__ = MetaFigure
    figure.__post_process__()
    for key, value in kwargs.items():
        setattr(figure, key, value)

@dispatch(Chart)
def metaize(chart, **kwargs):
    chart.__class__ = MetaChart
    chart.__post_process__()
    for key, value in kwargs.items():
        setattr(chart, key, value)
