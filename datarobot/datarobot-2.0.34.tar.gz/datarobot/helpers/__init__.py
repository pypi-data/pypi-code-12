from .partitioning_methods import *


class RecommenderSettings(object):
    recommender_user_id = None
    recommender_item_id = None

    def __init__(self, recommender_user_id, recommender_item_id):
        self.recommender_user_id = recommender_user_id
        self.recommender_item_id = recommender_item_id

    def collect_payload(self):
        payload = {
            'recommender_user_id': self.recommender_user_id,
            'recommender_item_id': self.recommender_item_id
        }
        return payload


class AdvancedOptions(object):
    """
    Used when setting the target of a project to set advanced options of modelling process.

    Parameters
    ----------
    weights : string, optional
        The name of a column indicating the weight of each row
    response_cap : float in [0.5, 1), optional
        Quantile of the response distribution to use for response capping.
    blueprint_threshold : int, optional
        Number of hours models are permitted to run.
        Minimum 1

    Examples
    --------
    .. code-block:: python

        from datarobot import AdvancedOptions
        advanced_options = AdvancedOptions(
            weights='weights_column',
            response_cap=0.7,
            blueprint_threshold=2)

    """
    weights = None
    response_cap = None
    blueprint_threshold = None
    seed = None

    def __init__(self, weights=None, response_cap=None,
                 blueprint_threshold=None, seed=None):
        self.weights = weights
        self.response_cap = response_cap
        self.blueprint_threshold = blueprint_threshold
        self.seed = seed

    def collect_payload(self):
        response_cap = self.response_cap
        if response_cap is not None:
            response_cap = float(response_cap)
        blueprint_threshold = self.blueprint_threshold
        if blueprint_threshold is not None:
            blueprint_threshold = int(blueprint_threshold)
        seed = self.seed
        if seed is not None:
            seed = int(seed)

        payload = dict(
            weights=self.weights,
            response_cap=response_cap,
            blueprint_threshold=blueprint_threshold,
            seed=seed
        )
        return payload
