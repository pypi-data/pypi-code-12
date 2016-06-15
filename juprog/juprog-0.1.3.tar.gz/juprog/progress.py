import os
import uuid
from IPython.display import HTML, Javascript, display

pb = """
<div id="{id0}">{msg}</div>
<div style="border: 1px solid black; width:500px">
  <div id="{id1}" style="background-color:{color}; width:0%">&nbsp;</div>
</div>
"""

circle_html = """
<script>
%s
</script>

<div id="%s"></div>

<script>
    var ele = "#%s";
    $(ele).progressCircle({
        nPercent        : 0,
        showPercentText : true,
        thickness       : 5,
        circleSize      : 60,
    });
</script>
"""

js_circle = """
$("#%s").progressCircle({
    nPercent        : %s,
    showPercentText : true,
    thickness       : 5,
    circleSize      : 60,
});
"""


class CircleProgress(object):
    """

    Parameters
    ----------
    every : int
    size : sequence size
        if None, use len(sequence)

    Examples
    --------
    >>> from juprog import CircleProgress
    >>> from time import sleep
    >>> for x in CircleProgress(sequence=range(10), every=2):
    ...     sleep(0.2)
    <IPython.core.display.HTML object>
    <IPython.core.display.Javascript object>
    <IPython.core.display.Javascript object>
    <IPython.core.display.Javascript object>
    <IPython.core.display.Javascript object>
    <IPython.core.display.Javascript object>
    <IPython.core.display.Javascript object>
    """
    def __init__(self, sequence, every=1, size=None):
        self.sequence = sequence
        self.every = every
        if size is not None:
            self.size = size
        else:
            try:
                self.size = len(self.sequence)
            except TypeError:
                raise TypeError('can not determine lenth, please provide size')

    def init_display(self, circle):
        fn = os.path.dirname(__file__) + '/html/css/circle.css'
        style = "<style>\n" + open(fn).read() + "</style>" 
        fn2 = os.path.dirname(__file__) + '/html/progress-circle.js'
        js = open(fn2).read()
        display(HTML(style + circle_html % (js, circle, circle)))
    
    def make_bar(self, idx, sizes, circle):
        '''work with jupyter notebook.
        '''
        percent = str(100*idx/sizes)
        display(Javascript(js_circle % (circle, percent)))
    
    def __iter__(self):
        index = 0
        circle = str(uuid.uuid4())
        self.init_display(circle)
    
        for index, record in enumerate(self.sequence, 1):
            if index == 1 or index % self.every == 0:
                self.make_bar(index, self.size, circle)
            yield record
