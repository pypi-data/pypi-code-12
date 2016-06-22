from builtins import object
import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd
from builtins import set
from .. util import robotize


class TimeSeries(object):
    """
    An TimeSeries object generalizes the parsing of a time series of datasets
    Parameters
    ----------
    datasets: List[dataset]
        List of Datasets
    """
    def __init__(self, datasets):
        self.datasets = datasets
        self._data = pd.concat([ds.data for ds in datasets])
        self._data.index = [ds.name for ds in datasets]
        self._data.insert(0, "time", pd.to_datetime([ds.attributes["warp"]["completed_at"] for ds in datasets]))


class GrowthCurve(TimeSeries):
    """
    A GrowthCurve object is used to analyze a series of PlateRead datasets
    Parameters
    ----------
    datasets: List[PlateRead]
        List of PlateRead objects
    """
    def __init__(self, datasets):
        operation_set = set([ds.operation for ds in datasets])
        if len(operation_set) > 1:
            raise RuntimeError("Input Datasets must all be of the same type.")
        self.operation = operation_set.pop()
        if self.operation not in ["absorbance", "fluorescence", "luminescence"]:
            raise RuntimeError("%s has to be of type absorbance, fluorescence or luminescence" % self.operation)
        super(GrowthCurve, self).__init__(datasets)

    def plot(self, wells, title=None, xlabel=None, ylabel=None):
        # Assume well names are consistent across all runs
        well_names = {aq["well_idx"]: aq["name"] for aq in self.datasets[0].attributes["container"]["aliquots"]}
        cont_type = self.datasets[0].attributes["container"]["container_type"]

        if isinstance(wells, list):
            traces = [go.Scatter(x=self._data['time'], y=self._data[well],
                                 name=well_names[robotize(well, cont_type["well_count"], cont_type["col_count"])])
                      for well in wells]
        elif isinstance(wells, str):
            traces = [go.Scatter(x=self._data['time'], y=self._data[wells],
                                 name=well_names[robotize(well, cont_type["well_count"], cont_type["col_count"])])]

        # Assume all data is generated from the same run-id for now
        if not title:
            title = "Growth Curve (%s)" % self.datasets[0].attributes["instruction"]["run"]["id"]
        if not xlabel:
            xlabel = 'Time'
        if not ylabel:
            if self.operation == "absorbance":
                ylabel = "RAU (%s)" % self.datasets[0].attributes["instruction"]["operation"]["wavelength"]
            elif self.operation == "fluorescence":
                ylabel = "RFU (%s/%s)" % (self.datasets[0].attributes["instruction"]["operation"]["excitation"],
                                          self.datasets[0].attributes["instruction"]["operation"]["emission"])
            elif self.operation == "luminescence":
                ylabel = "Luminescence"

        layout = go.Layout(
            title=title,
            xaxis=dict(
                title=xlabel,
                titlefont=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                )
            ),
            yaxis=dict(
                title=ylabel,
                titlefont=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                )
            )
        )

        fig = go.Figure(data=traces, layout=layout)
        return py.iplot(fig)


