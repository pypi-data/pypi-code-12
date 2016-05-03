from datetime import timedelta
from pandas import date_range, DataFrame, Series, to_timedelta, Timestamp

class DatasetError(Exception): pass
class ShortDatasetError(DatasetError): pass
class SubMinuteTimestepError(DatasetError): pass
class InterpolationError(DatasetError): pass

def timestep_to_pandas_freq(res):
    """convert a timedelta object to pandas formatted frequency string"""
    return "{}Min".format(int(res.total_seconds() / 60))

class Dataset(object):
    """
    A general purpose dataset, with some quality checking and data cleaning stuff
    It takes a dataframe and a timestep integer
    timestep is the number of seconds expected between readings
    the validate function tests the dataframe to see if it matches the expected timestep
    the interpolate function will force it to do so
    """
    def __init__(self, measurements, timestep, cumulative):
        if timestep % 60 != 0:
            # timesteps must be whole minutes
            raise SubMinuteTimestepError
        # it important to convert to float before any interpolation is done
        self.measurements = measurements.astype(float)

        # force to timezone aware, UTC
        try:
            self.measurements = self.measurements.tz_localize('UTC')
        except TypeError:
            self.measurements = self.measurements.tz_convert('UTC')

        # check we have data
        self.count = int(self.measurements['value'].count())
        if self.count == 0:
            raise ShortDatasetError

        # always store as cumulative
        if not cumulative:
            self.data = self.measurements[:]
            self.measurements = self.measurements.cumsum()
        else:
            self.data = self.measurements.diff()[1:]

        self.timestep = timedelta(seconds=timestep)
        self.earliest = self.measurements.index.min().to_datetime()
        self.latest = self.measurements.index.max().to_datetime()


    def total(self):
        "calculate total consumption - important to keep this the same"
        return self.measurements.diff().value.sum()

    def apparent_timestep(self):
        try:
            return (self.latest - self.earliest)/(self.count-1)
        except ZeroDivisionError:
            raise ShortDatasetError

    def offsets(self):
        return Series(self.measurements.index.get_values()).diff()[1:]

    def consistency_check(self):

        return (self.offsets() == to_timedelta(self.timestep)).all()

    def validate(self):
        ts = self.apparent_timestep()
        return ts == self.timestep and self.consistency_check()

    def interpolate(self):
        if self.validate():
            return self
        return self._interpolate()

    def _interpolate(self):
        pandas_freq = timestep_to_pandas_freq(self.timestep)

        result = self.measurements[:]

        # add regular timestamps with NaNs
        # timedelta = to_timedelta(self.timestep)
        regular_index = date_range(
            start=self.earliest-self.timestep,
            end=self.latest+self.timestep,
            freq=pandas_freq,
            normalize=True,
            tz='UTC'
        )

        result = result.append(DataFrame(index=regular_index, columns=['value']))


        # deduplicate - remove NaNs that overlap with real data
        result["index"] = result.index
        result.drop_duplicates(subset='index', inplace=True)
        del result["index"]

        # interpolate to fill the NaNs
        result = result.sort().interpolate(method="time", closed='left')

        try:
            # resample to remove original data
            # result = result.resample(pandas_freq, closed='left')
            # pick out the data coresponding to regular_index
            # keys = regular_index.values
            keys = [Timestamp(v, tz="UTC") for v in regular_index.values]
            result = result.loc[keys]
            # result = result.loc[regular_index.values]
        except KeyError:
            print(Timestamp(regular_index.values[0], tz="UTC"), result.index[0])
            keys = [Timestamp(v, tz="UTC") for v in regular_index.values]
            print(result.loc[keys])
            raise InterpolationError("Possible timezone mismatch?")

        # drop NaN values as they are not counted in validation
        return Dataset(result.dropna(), self.timestep.total_seconds(), cumulative=True)
