from .tuning_nnls_chroma import TuningEstimatorMauch

__author__ = 'Jakob Abesser'


class TuningEstimator:
    """ Wrapper class for tuning estimation algorithms
    """

    def __init__(self):
        pass

    @staticmethod
    def process(**options):
        if options['tuning_estimation_method'] == 'mauch_nnls':
            return TuningEstimatorMauch.process(options['fn_wav'])
        else:
            raise Exception("Tuning estimation method not implemented!")


