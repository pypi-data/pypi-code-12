from .dataset import Dataset, ShortDatasetError
from .model import DailyAverageModel

class ShortBaselineError(ShortDatasetError): pass

class SavingCalculation(object):
    """calculate savings between two periods based on a simple consumption model"""

    def __init__(self, measurements, baseline_model, test_period, baseline_period, cumulative):
        self.baseline_period = baseline_period
        self.test_period = test_period
        self.dataset = Dataset(measurements, 60*60*24, cumulative).interpolate()
        df = self.dataset.data
        self.data = df
        self.baseline_data = df[(df.index<=baseline_period.end_date) & (df.index>=baseline_period.start_date)]
        self.test_data = df[(df.index<=test_period.end_date) & (df.index>=test_period.start_date)]
        try:
            self.baseline_model = baseline_model(self.baseline_data, False)
        except ShortDatasetError:
            raise ShortBaselineError("No baseline data")

    def baseline_period_covered(self):
        return self.baseline_period.start_date >= self.dataset.earliest and self.baseline_period.end_date <= self.dataset.latest

    def model(self):
        return self.baseline_model.prediction(self.baseline_data.index)

    def prediction(self):
        return self.baseline_model.prediction(self.test_data.index)

    def savings(self):
        return self.prediction() - self.test_data['value']
