
from matplotlib import rcParams
import matplotlib as mpl
import matplotlib.pyplot as plt


class Window(object):
    """
    A window in which to add widgets.
    """

    def __init__(self, box, title = 'Window', padding = 0.10, toolbar = False):
        """
        width & height in inches
        """

        self._box = box
        self._padding = padding

        w, h = box.size()

        padding = 0.10

        w += 2.0 * padding
        h += 2.0 * padding

        orig_toolbar_settig = mpl.rcParams['toolbar']

        if not toolbar:
            mpl.rcParams['toolbar'] = 'None'

        self._fig = plt.figure(figsize=(w,h))

        self._fig.subplots_adjust(
            left = 0.0,
            bottom = 0.0,
            right = 1.0,
            top = 1.0,
            wspace = 0.0,
            hspace = 0.0,
        )

        self._fig.canvas.set_window_title(title)

        x = padding
        y = padding

        box._render(self._fig, x, y)

        # restore default rcparams
        mpl.rcParams['toolbar'] = orig_toolbar_settig

        #----------------------------------------------------------------------
        # disable the default keymap

        self._rc_keys_to_disable = []

        for key in rcParams.keys():
            if u'keymap' in key:
                self._rc_keys_to_disable.append(key)
                rcParams[key] = ''

        self._rc_keys_disabled = {}
